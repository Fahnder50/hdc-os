from pathlib import Path

import pytest

import procurement_watch.services as services
from procurement_watch.config import resolve_config
from procurement_watch.lifecycle import (
    ACTIVE_CASE_STATUSES,
    ARCHIVE_VIEW,
    CASE_STATUSES,
    COMPLETION_STATUSES,
    validate_case_status,
)
from procurement_watch.services import (
    add_product,
    case_status,
    import_all_cases,
    import_case,
    portfolio_watch,
    report_case,
    run_live_watch,
    run_watch,
)


ROOT = Path(__file__).resolve().parents[2]
PC1 = ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml"


def config(tmp_path):
    return resolve_config(
        environ={"HDC_PROCUREMENT_RUNTIME": str(tmp_path / "runtime")},
        repository_root=ROOT,
    )


def test_lifecycle_contract_is_complete_and_unambiguous():
    assert ACTIVE_CASE_STATUSES == (
        "WATCHING", "QUALIFYING", "READY_FOR_REVIEW", "BUY_CANDIDATE",
    )
    assert COMPLETION_STATUSES == ("PURCHASED", "CANCELLED")
    assert ARCHIVE_VIEW == "CLOSED"
    assert len(CASE_STATUSES) == len(set(CASE_STATUSES)) == 6
    assert "REVIEW" not in CASE_STATUSES and "EVALUATING" not in CASE_STATUSES
    with pytest.raises(ValueError, match="Invalid procurement lifecycle status"):
        validate_case_status("CLOSED")


def test_existing_cases_migrate_without_loss_and_only_active_cases_are_watched(monkeypatch, tmp_path):
    runtime = config(tmp_path)
    assert import_all_cases(runtime)["count"] == 5
    called = []
    monkeypatch.setattr(services, "run_live_watch", lambda _config, case_id: called.append(case_id) or {
        "recommendation_status": "QUALIFYING", "failed_sources": 0, "status": "succeeded",
    })
    result = portfolio_watch(runtime)
    assert called == ["PC-0002", "PC-0003", "PC-0004", "PC-0005"]
    assert result["case_count"] == 4
    assert [(item["case_id"], item["status"]) for item in result["completed_procurement"]] == [
        ("PC-0001", "PURCHASED")
    ]


def test_completed_case_causes_no_web_request_watch_or_new_journal(monkeypatch, tmp_path):
    runtime = config(tmp_path)
    import_all_cases(runtime)
    monkeypatch.setattr(services, "collect_source", lambda *_args, **_kwargs: pytest.fail("web request attempted"))
    connection = services.connect(runtime)
    case_db_id = connection.execute("SELECT id FROM procurement_cases WHERE case_id = 'PC-0001'").fetchone()[0]
    before = connection.execute("SELECT COUNT(*) FROM journal_entries WHERE case_id = ?", (case_db_id,)).fetchone()[0]
    connection.close()
    with pytest.raises(ValueError, match="not active for watching"):
        run_live_watch(runtime, "PC-0001")
    run_watch(runtime)
    connection = services.connect(runtime)
    after = connection.execute("SELECT COUNT(*) FROM journal_entries WHERE case_id = ?", (case_db_id,)).fetchone()[0]
    connection.close()
    assert after == before


def test_completed_case_is_read_only_and_manual_view_is_closure_only(tmp_path):
    runtime = config(tmp_path)
    import_case(runtime, PC1)
    status = case_status(runtime, "PC-0001")
    assert status["case_status"] == "PURCHASED"
    assert status["lifecycle_status"] == "CLOSED"
    assert status["recommendation_status"] == "CLOSED"
    assert status["market_evaluation_active"] is False
    assert status["completion_date"] == "2026-08-03"
    assert status["external_reference"] is None
    with pytest.raises(ValueError, match="closed for procurement changes"):
        add_product(runtime, "LATE-PRODUCT", "Late", case_id="PC-0001")
    connection = services.connect(runtime)
    before = [tuple(row) for row in connection.execute(
        "SELECT offer_id, status, price_cents FROM offers ORDER BY offer_id"
    )]
    connection.close()
    report = report_case(runtime, "PC-0001").read_text(encoding="utf-8")
    connection = services.connect(runtime)
    after = [tuple(row) for row in connection.execute(
        "SELECT offer_id, status, price_cents FROM offers ORDER BY offer_id"
    )]
    connection.close()
    assert after == before
    assert "PROCUREMENT ABGESCHLOSSEN" in report
    assert "Keine Markt-, Preis- oder Kaufempfehlungsbewertung mehr aktiv" in report
    assert "JETZT KAUFEN" not in report


def test_generic_cancelled_case_needs_no_asset_or_operations_data(tmp_path):
    runtime = config(tmp_path)
    source = (ROOT / "30-Procurement/cases/PC-0002-Rollbarer-Netzwerkschrank.yaml").read_text(encoding="utf-8")
    source = source.replace("PC-0002", "TEST-GENERIC", 1)
    source = source.replace("status: WATCHING", "status: CANCELLED", 1)
    source = "\n".join(line for line in source.splitlines() if not line.startswith("requirement_profile:")) + "\n"
    path = tmp_path / "generic-cancelled.yaml"
    path.write_text(source, encoding="utf-8")
    import_case(runtime, path)
    status = case_status(runtime, "TEST-GENERIC")
    assert status["case_status"] == "CANCELLED"
    assert status["external_reference"] is None
    assert status["procurement_completed"] is True
    assert portfolio_watch(runtime)["case_count"] == 0
