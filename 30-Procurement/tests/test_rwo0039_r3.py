import json
from pathlib import Path

import yaml

import procurement_watch.services as services
from procurement_watch.config import resolve_config
from procurement_watch.database import initialize
from procurement_watch.services import portfolio_watch


def _repository(tmp_path, statuses):
    root = tmp_path / "repository"
    cases = root / "30-Procurement" / "cases"
    config = root / "30-Procurement" / "config"
    cases.mkdir(parents=True)
    config.mkdir(parents=True)
    (config / "sources.yaml").write_text("sources: []\n", encoding="utf-8")
    for case_id, status in statuses.items():
        document = {
            "case_id": case_id,
            "title": f"Legacy case {case_id}",
            "status": status,
            "closed_at": "2026-08-04" if status in ("PURCHASED", "CANCELLED") else None,
        }
        (cases / f"{case_id}.yaml").write_text(
            yaml.safe_dump(document, sort_keys=False), encoding="utf-8"
        )
    return root


def _config(tmp_path, root):
    return resolve_config(
        environ={"HDC_PROCUREMENT_RUNTIME": str(tmp_path / "runtime")},
        repository_root=root,
    )


def _insert_runtime_cases(config, statuses, legacy=True):
    initialize(config)
    connection = services.connect(config)
    for case_id, status in statuses.items():
        connection.execute(
            "INSERT INTO procurement_cases(case_id, title, status, priority, created_at, updated_at) "
            "VALUES (?, ?, ?, 'normal', '2026-07-01', '2026-07-15')",
            (case_id, f"Legacy case {case_id}", status),
        )
    if legacy:
        connection.execute(
            "DELETE FROM runtime_metadata WHERE metadata_key = 'runtime_upgrade_rwo0039_r3'"
        )
    connection.commit()
    connection.close()


def _case_snapshot(connection, case_db_id):
    tables = ("requirements", "case_products", "evaluations", "journal_entries", "watch_run_results")
    snapshot = {
        table: [tuple(row) for row in connection.execute(
            f"SELECT * FROM {table} WHERE case_id = ? ORDER BY rowid", (case_db_id,)
        )]
        for table in tables
    }
    for table in ("products", "vendors", "offers", "price_observations"):
        snapshot[table] = [tuple(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY rowid")]
    return snapshot


def test_legacy_active_case_is_reconciled_once_without_rewriting_history(monkeypatch, tmp_path):
    root = _repository(tmp_path, {"PC-LEGACY": "PURCHASED"})
    config = _config(tmp_path, root)
    _insert_runtime_cases(config, {"PC-LEGACY": "QUALIFYING"})
    connection = services.connect(config)
    case_db_id = connection.execute(
        "SELECT id FROM procurement_cases WHERE case_id = 'PC-LEGACY'"
    ).fetchone()[0]
    connection.execute(
        "INSERT INTO requirements(case_id, requirement_id, name, value_json, status, created_at, updated_at) "
        "VALUES (?, 'external_reference', 'external_reference', ?, 'PASS', '2026-07-01', '2026-07-01')",
        (case_db_id, json.dumps("ORDER-42")),
    )
    connection.execute(
        "INSERT INTO journal_entries(entry_id, case_id, observed_at, recommendation_status, summary_json, changes_json, created_at) "
        "VALUES ('JRN-OLD', ?, '2026-07-10', 'QUALIFYING', '{}', '{}', '2026-07-10')",
        (case_db_id,),
    )
    connection.execute(
        "INSERT INTO products(product_id, product_name, status, created_at, updated_at) "
        "VALUES ('PROD-OLD', 'Historic product', 'candidate', '2026-07-01', '2026-07-01')"
    )
    product_db_id = connection.execute("SELECT id FROM products WHERE product_id = 'PROD-OLD'").fetchone()[0]
    connection.execute(
        "INSERT INTO case_products(case_id, product_id, status, created_at) VALUES (?, ?, 'proposed', '2026-07-01')",
        (case_db_id, product_db_id),
    )
    connection.execute(
        "INSERT INTO vendors(vendor_id, name, status, created_at, updated_at) "
        "VALUES ('VENDOR-OLD', 'Historic vendor', 'known', '2026-07-01', '2026-07-01')"
    )
    vendor_db_id = connection.execute("SELECT id FROM vendors WHERE vendor_id = 'VENDOR-OLD'").fetchone()[0]
    connection.execute(
        "INSERT INTO offers(offer_id, product_id, vendor_id, source_type, source_reference, price_cents, "
        "shipping_cents, total_price_cents, currency, availability, observed_at, status, created_at, updated_at) "
        "VALUES ('OFFER-OLD', ?, ?, 'manual', 'historic://offer', 10000, 500, 10500, 'EUR', "
        "'available', '2026-07-02', 'active', '2026-07-02', '2026-07-02')",
        (product_db_id, vendor_db_id),
    )
    offer_db_id = connection.execute("SELECT id FROM offers WHERE offer_id = 'OFFER-OLD'").fetchone()[0]
    connection.execute(
        "INSERT INTO price_observations(observation_id, offer_id, price_cents, shipping_cents, "
        "total_price_cents, currency, availability, observed_at, source_adapter, validation_status) "
        "VALUES ('OBS-OLD', ?, 10000, 500, 10500, 'EUR', 'available', '2026-07-02', 'manual', 'valid')",
        (offer_db_id,),
    )
    connection.execute(
        "INSERT INTO evaluations(evaluation_id, case_id, offer_id, result, reason, evaluated_at) "
        "VALUES ('EVAL-OLD', ?, ?, 'PASS', 'historic decision', '2026-07-03')",
        (case_db_id, offer_db_id),
    )
    connection.commit()
    before = _case_snapshot(connection, case_db_id)
    connection.close()
    report = config.reports_path / "PC-LEGACY.html"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("historic report", encoding="utf-8")
    report_bytes, report_mtime = report.read_bytes(), report.stat().st_mtime_ns

    monkeypatch.setattr(
        services, "transition_case_status",
        lambda *_args: (_ for _ in ()).throw(AssertionError("normal transition engine used")),
    )
    result = initialize(config)["runtime_upgrade"]
    assert result["status_migrations"] == 1
    assert result["completion_metadata_added"] == 2
    assert result["closure_journals_added"] == 1

    connection = services.connect(config)
    assert tuple(connection.execute(
        "SELECT status, updated_at FROM procurement_cases WHERE id = ?", (case_db_id,)
    ).fetchone()) == ("PURCHASED", "2026-07-15")
    requirements = dict(connection.execute(
        "SELECT requirement_id, value_json FROM requirements WHERE case_id = ?", (case_db_id,)
    ).fetchall())
    assert json.loads(requirements["external_reference"]) == "ORDER-42"
    assert json.loads(requirements["completion_date"]) == "2026-08-04"
    assert json.loads(requirements["closed_flag"]) is True
    journals = connection.execute(
        "SELECT recommendation_status FROM journal_entries WHERE case_id = ? ORDER BY id", (case_db_id,)
    ).fetchall()
    assert [row[0] for row in journals] == ["QUALIFYING", "CLOSED"]
    after_first = _case_snapshot(connection, case_db_id)
    connection.close()
    assert after_first["journal_entries"][:-1] == before["journal_entries"]
    assert report.read_bytes() == report_bytes
    assert report.stat().st_mtime_ns == report_mtime

    second = initialize(config)["runtime_upgrade"]
    assert second["status_migrations"] == 0
    assert second["completion_metadata_added"] == 0
    assert second["closure_journals_added"] == 0
    connection = services.connect(config)
    assert _case_snapshot(connection, case_db_id) == after_first
    connection.close()


def test_upgrade_and_portfolio_treat_purchased_and_cancelled_symmetrically(monkeypatch, tmp_path):
    repository_statuses = {
        "PC-A": "PURCHASED", "PC-B": "CANCELLED",
        "PC-C": "QUALIFYING", "PC-D": "WATCHING",
    }
    root = _repository(tmp_path, repository_statuses)
    config = _config(tmp_path, root)
    _insert_runtime_cases(config, {
        "PC-A": "QUALIFYING", "PC-B": "WATCHING",
        "PC-C": "QUALIFYING", "PC-D": "WATCHING",
    })
    initialize(config)
    calls = []
    monkeypatch.setattr(services, "run_live_watch", lambda _config, case_id: calls.append(case_id) or {
        "recommendation_status": repository_statuses[case_id],
        "failed_sources": 0,
        "status": "succeeded",
    })
    monkeypatch.setattr(services, "case_status", lambda _config, case_id: {
        "case_id": case_id, "valid_offers": 0, "observed_offers": 0,
        "technically_eligible_offers": 0,
    })
    result = portfolio_watch(config)
    assert calls == ["PC-C", "PC-D"]
    assert result["case_count"] == 2
    assert result["completed_count"] == 2
    assert {(item["case_id"], item["status"]) for item in result["completed_procurement"]} == {
        ("PC-A", "PURCHASED"), ("PC-B", "CANCELLED"),
    }


def test_fresh_active_database_requires_no_upgrade(tmp_path):
    root = _repository(tmp_path, {"PC-NEW": "WATCHING"})
    config = _config(tmp_path, root)
    first = initialize(config)["runtime_upgrade"]
    _insert_runtime_cases(config, {"PC-NEW": "WATCHING"}, legacy=False)
    second = initialize(config)["runtime_upgrade"]
    assert first == second == {
        "checked": 0,
        "status_migrations": 0,
        "completion_metadata_added": 0,
        "closure_journals_added": 0,
    }
