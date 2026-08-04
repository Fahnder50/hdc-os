from pathlib import Path

import procurement_watch.services as services
from procurement_watch.config import resolve_config
from procurement_watch.services import (
    case_status,
    history_for_case,
    import_all_cases,
    import_case,
    portfolio_watch,
    report_case,
    transition_case,
)


ROOT = Path(__file__).resolve().parents[2]
BASE_CASE = ROOT / "30-Procurement/cases/PC-0002-Rollbarer-Netzwerkschrank.yaml"


def config(tmp_path):
    return resolve_config(
        environ={"HDC_PROCUREMENT_RUNTIME": str(tmp_path / "runtime")},
        repository_root=ROOT,
    )


def generic_case(tmp_path, case_id):
    source = BASE_CASE.read_text(encoding="utf-8").replace("PC-0002", case_id, 1)
    source = "\n".join(line for line in source.splitlines() if not line.startswith("requirement_profile:")) + "\n"
    path = tmp_path / f"{case_id}.yaml"
    path.write_text(source, encoding="utf-8")
    return path


def case_counts(runtime, case_id):
    connection = services.connect(runtime)
    case_db_id = connection.execute(
        "SELECT id FROM procurement_cases WHERE case_id = ?", (case_id,)
    ).fetchone()[0]
    result = {
        "products": connection.execute("SELECT COUNT(*) FROM case_products WHERE case_id = ?", (case_db_id,)).fetchone()[0],
        "evaluations": connection.execute("SELECT COUNT(*) FROM evaluations WHERE case_id = ?", (case_db_id,)).fetchone()[0],
        "journal": connection.execute("SELECT COUNT(*) FROM journal_entries WHERE case_id = ?", (case_db_id,)).fetchone()[0],
        "watch_results": connection.execute("SELECT COUNT(*) FROM watch_run_results WHERE case_id = ?", (case_db_id,)).fetchone()[0],
    }
    connection.close()
    return result


def test_portfolio_filters_purchased_before_watch_and_freezes_report_and_data(monkeypatch, tmp_path):
    runtime = config(tmp_path)
    import_all_cases(runtime)
    report_path = report_case(runtime, "PC-0001")
    report_before = report_path.read_bytes()
    timestamp_before = report_path.stat().st_mtime_ns
    counts_before = case_counts(runtime, "PC-0001")
    history_before = history_for_case(runtime, "PC-0001")
    called = []

    monkeypatch.setattr(services, "run_live_watch", lambda _config, case_id: called.append(case_id) or {
        "recommendation_status": "WATCHING", "failed_sources": 0, "status": "succeeded",
    })
    result = portfolio_watch(runtime)

    assert called == ["PC-0002", "PC-0003", "PC-0004", "PC-0005"]
    assert result["case_count"] == result["health"]["active"] == 4
    assert result["health"]["watching"] == 4
    assert result["completed_count"] == 1
    assert result["completed_procurement"] == [{
        "case_id": "PC-0001",
        "title": "USV für Internet-Gateway",
        "status": "PURCHASED",
        "completion_date": "2026-08-03",
    }]
    assert report_path.read_bytes() == report_before
    assert report_path.stat().st_mtime_ns == timestamp_before
    assert case_counts(runtime, "PC-0001") == counts_before
    assert history_for_case(runtime, "PC-0001") == history_before


def test_cancelled_case_gets_one_final_journal_entry_then_remains_frozen(monkeypatch, tmp_path):
    runtime = config(tmp_path)
    case_id = "TEST-CANCELLED-R2"
    import_case(runtime, generic_case(tmp_path, case_id))
    for target in ("QUALIFYING", "READY_FOR_REVIEW", "CANCELLED"):
        transition_case(runtime, case_id, target)

    status = case_status(runtime, case_id)
    assert status["case_status"] == "CANCELLED"
    completion_date = status["completion_date"]
    connection = services.connect(runtime)
    case_db_id = connection.execute("SELECT id FROM procurement_cases WHERE case_id = ?", (case_id,)).fetchone()[0]
    journal = connection.execute(
        "SELECT recommendation_status, observed_at FROM journal_entries WHERE case_id = ? ORDER BY observed_at",
        (case_db_id,),
    ).fetchall()
    connection.close()
    assert [tuple(row) for row in journal] == [("CLOSED", completion_date)]

    report_path = report_case(runtime, case_id)
    report_before = report_path.read_bytes()
    timestamp_before = report_path.stat().st_mtime_ns
    counts_before = case_counts(runtime, case_id)
    monkeypatch.setattr(services, "run_live_watch", lambda *_args: (_ for _ in ()).throw(AssertionError("completed case reached watch engine")))
    result = portfolio_watch(runtime)
    assert result["case_count"] == 0 and result["completed_count"] == 1
    assert result["completed_procurement"][0]["completion_date"] == completion_date
    assert report_case(runtime, case_id) == report_path
    assert report_path.read_bytes() == report_before
    assert report_path.stat().st_mtime_ns == timestamp_before
    assert case_counts(runtime, case_id) == counts_before


def test_completed_cases_never_enter_active_metrics(monkeypatch, tmp_path):
    runtime = config(tmp_path)
    import_all_cases(runtime)
    cancelled_id = "TEST-CANCELLED-METRICS"
    import_case(runtime, generic_case(tmp_path, cancelled_id))
    transition_case(runtime, cancelled_id, "CANCELLED")
    monkeypatch.setattr(services, "run_live_watch", lambda _config, case_id: {
        "recommendation_status": {
            "PC-0002": "WATCHING",
            "PC-0003": "QUALIFYING",
            "PC-0004": "READY_FOR_REVIEW",
            "PC-0005": "BUY_CANDIDATE",
        }[case_id],
        "failed_sources": 0,
        "status": "succeeded",
    })
    result = portfolio_watch(runtime)
    assert result["case_count"] == result["health"]["active"] == 4
    assert result["health"] | {
        "watching": 1, "qualifying": 1, "ready_for_review": 1, "buy_candidate": 1,
    } == result["health"]
    assert result["completed_count"] == 2
    assert {(item["case_id"], item["status"]) for item in result["completed_procurement"]} == {
        ("PC-0001", "PURCHASED"), (cancelled_id, "CANCELLED"),
    }


def test_purchased_and_cancelled_are_symmetrically_filtered_before_watch_all(monkeypatch, tmp_path):
    runtime = config(tmp_path)
    purchased_id = "TEST-TV-PURCHASED"
    cancelled_id = "TEST-WASHING-MACHINE-CANCELLED"
    watching_id = "TEST-TOOLS-WATCHING"
    for case_id in (purchased_id, cancelled_id, watching_id):
        import_case(runtime, generic_case(tmp_path, case_id))

    for target in ("QUALIFYING", "READY_FOR_REVIEW", "BUY_CANDIDATE", "PURCHASED"):
        transition_case(runtime, purchased_id, target)
    for target in ("QUALIFYING", "READY_FOR_REVIEW", "CANCELLED"):
        transition_case(runtime, cancelled_id, target)

    frozen = {}
    for case_id in (purchased_id, cancelled_id):
        report = report_case(runtime, case_id)
        frozen[case_id] = {
            "report": report,
            "bytes": report.read_bytes(),
            "mtime": report.stat().st_mtime_ns,
            "counts": case_counts(runtime, case_id),
        }

    engine_calls = []
    monkeypatch.setattr(services, "run_live_watch", lambda _config, case_id: engine_calls.append(case_id) or {
        "recommendation_status": "WATCHING", "failed_sources": 0, "status": "succeeded",
    })
    result = portfolio_watch(runtime)

    assert engine_calls == [watching_id]
    assert result["case_count"] == 1
    assert result["completed_count"] == 2
    assert {(item["case_id"], item["status"]) for item in result["completed_procurement"]} == {
        (purchased_id, "PURCHASED"),
        (cancelled_id, "CANCELLED"),
    }
    for case_id in (purchased_id, cancelled_id):
        report = frozen[case_id]["report"]
        assert report.read_bytes() == frozen[case_id]["bytes"]
        assert report.stat().st_mtime_ns == frozen[case_id]["mtime"]
        assert case_counts(runtime, case_id) == frozen[case_id]["counts"]
