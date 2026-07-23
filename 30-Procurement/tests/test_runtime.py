import sqlite3
from pathlib import Path

import procurement_watch.cli as cli
import procurement_watch.services as services_module
from procurement_watch.config import load_yaml_config, resolve_config
from procurement_watch.database import schema_status
from procurement_watch.backup import backup_database, restore_database
from procurement_watch.adapters import AdapterError, parse_json_ld_file
from procurement_watch.events import EVENT_SEVERITIES, EVENT_TYPES, classify_event, emit_event
from procurement_watch.services import add_offer, add_product, case_status, current_events, doctor, import_case, init_database, offers_for_case, procurement_status, recent_watch_runs, run_watch, history_for_case


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_configuration_resolution(monkeypatch, tmp_path):
    monkeypatch.setenv("HDC_PROCUREMENT_DB", str(tmp_path / "data" / "procurement.db"))
    monkeypatch.setenv("HDC_PROCUREMENT_LOGS", str(tmp_path / "logs"))
    monkeypatch.setenv("HDC_PROCUREMENT_REPORTS", str(tmp_path / "reports"))
    config = resolve_config(repository_root=tmp_path)
    assert config.database_path == tmp_path / "data" / "procurement.db"
    assert config.logs_path == tmp_path / "logs"
    assert config.reports_path == tmp_path / "reports"


def test_yaml_configuration_loads_mapping(tmp_path):
    config_path = tmp_path / "watch-policy.yaml"
    config_path.write_text("watch:\n  enabled: true\n", encoding="utf-8")
    assert load_yaml_config(config_path) == {"watch": {"enabled": True}}


def test_database_initialization_is_repeatable_and_tracks_repository(monkeypatch, tmp_path):
    config = resolve_config(
        environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db"), "HDC_REPOSITORY_VERSION": "knowledge-v1.2"},
        repository_root=REPO_ROOT,
    )
    first = init_database(config)
    second = init_database(config)
    assert first["schema_version"] == "003"
    assert second["repository_version"] == "knowledge-v1.2"
    connection = sqlite3.connect(config.database_path)
    metadata = dict(connection.execute("SELECT metadata_key, metadata_value FROM runtime_metadata").fetchall())
    migration_count = connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
    connection.close()
    assert len(metadata["repository_commit"]) == 40
    assert all(character in "0123456789abcdef" for character in metadata["repository_commit"])
    assert metadata["repository_version"] == "knowledge-v1.2"
    assert metadata["schema_version"] == "003"
    assert migration_count == 3


def test_foreign_keys_are_enforced(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=tmp_path)
    init_database(config)
    connection = sqlite3.connect(config.database_path)
    try:
        connection.execute("INSERT INTO case_products(case_id, product_id) VALUES (1, 1)")
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("foreign key constraint was not enforced")
    finally:
        connection.close()


def test_watch_run_completes_and_status_reads_it(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=tmp_path)
    result = run_watch(config)
    status = procurement_status(config)
    assert result["status"] == "succeeded"
    assert result["ended_at"]
    assert status["last_watch_run"]["watch_run_id"] == result["watch_run_id"]
    assert status["last_watch_run"]["status"] == "succeeded"
    assert status["schema_version"] == "003"
    assert status["initialized"] is True


def test_watch_run_can_record_failure(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=tmp_path)
    result = run_watch(config, simulate_failure=True)
    assert result["status"] == "failed"
    assert result["error_count"] == 1


def test_schema_status_before_initialization(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "missing.db")}, repository_root=tmp_path)
    status = schema_status(config)
    assert status["reachable"] is False
    assert status["schema_version"] is None


def test_status_does_not_initialize_or_create_paths(tmp_path):
    database_path = tmp_path / "missing" / "procurement.db"
    config = resolve_config(
        environ={
            "HDC_PROCUREMENT_DB": str(database_path),
            "HDC_PROCUREMENT_LOGS": str(tmp_path / "logs"),
            "HDC_PROCUREMENT_REPORTS": str(tmp_path / "reports"),
        },
        repository_root=tmp_path,
    )
    status = procurement_status(config)
    assert status["initialized"] is False
    assert status["cases"] is None
    assert status["open_events"] is None
    assert not database_path.exists()
    assert not config.logs_path.exists()
    assert not config.reports_path.exists()


def test_cli_successful_watch_returns_zero(monkeypatch, tmp_path):
    monkeypatch.setenv("HDC_PROCUREMENT_DB", str(tmp_path / "procurement.db"))
    assert cli.main(["watch", "run"]) == 0


def test_cli_failed_watch_returns_nonzero(monkeypatch):
    monkeypatch.setattr(cli, "run_watch", lambda config: {"status": "failed", "error_count": 1})
    assert cli.main(["watch", "run"]) == 1


def test_watch_run_rolls_back_and_closes_on_exception(monkeypatch, tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=tmp_path)
    init_database(config)
    real_connection = services_module.connect(config)

    class FailingConnection:
        def __init__(self, connection):
            self.connection = connection
            self.rollback_called = False
            self.close_called = False
            self.execute_count = 0

        def execute(self, *args, **kwargs):
            self.execute_count += 1
            if self.execute_count == 2:
                raise RuntimeError("simulated database failure")
            return self.connection.execute(*args, **kwargs)

        def commit(self):
            return self.connection.commit()

        def rollback(self):
            self.rollback_called = True
            return self.connection.rollback()

        def close(self):
            self.close_called = True
            return self.connection.close()

    failing_connection = FailingConnection(real_connection)
    monkeypatch.setattr(services_module, "connect", lambda config: failing_connection)
    try:
        run_watch(config)
    except RuntimeError:
        pass
    else:
        raise AssertionError("simulated database failure did not propagate")
    assert failing_connection.rollback_called is True
    assert failing_connection.close_called is True


def test_evaluations_reference_watch_runs_and_enforce_foreign_key(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=tmp_path)
    init_database(config)
    connection = sqlite3.connect(config.database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    foreign_keys = connection.execute("PRAGMA foreign_key_list(evaluations)").fetchall()
    assert any(row[2] == "watch_runs" and row[3] == "watch_run_id" for row in foreign_keys)
    connection.execute(
        "INSERT INTO procurement_cases(case_id, title, status, priority, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        ("PC-TEST", "Test case", "evaluating", "normal", "2026-07-20T00:00:00+00:00", "2026-07-20T00:00:00+00:00"),
    )
    case_id = connection.execute("SELECT id FROM procurement_cases WHERE case_id = 'PC-TEST'").fetchone()[0]
    try:
        connection.execute(
            "INSERT INTO evaluations(evaluation_id, case_id, watch_run_id, result, evaluated_at) VALUES (?, ?, ?, ?, ?)",
            ("EV-TEST", case_id, 999, "UNKNOWN", "2026-07-20T00:00:00+00:00"),
        )
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("evaluation watch_run foreign key was not enforced")
    finally:
        connection.close()


def test_pc001_import_products_offers_history_and_evaluation(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    case_path = "30-Procurement/cases/PC-0001-Router-USV.yaml"
    imported = import_case(config, case_path)
    assert imported["case_id"] == "PC-0001"
    add_product(
        config,
        "PROD-PC001-001",
        "Beispiel Router-USV",
        manufacturer="Beispielhersteller",
        model="UPS-001",
        technical={
            "runtime_hours": 4,
            "automatic_failover": True,
            "standalone_operation": True,
            "cloud_free_operation": True,
            "monitoring_capability": "local",
        },
        case_id="PC-0001",
    )
    add_offer(config, "OFFER-PC001-001", "PROD-PC001-001", "VENDOR-001", "Beispielhändler", "39.99", "4.99", "EUR", "in_stock", "manual", "manual:test", case_id="PC-0001")
    assert len(offers_for_case(config, "PC-0001")) == 1
    assert len(history_for_case(config, "PC-0001")) == 1
    result = run_watch(config)
    assert result["status"] == "succeeded"
    status = case_status(config, "PC-0001")
    assert status["recommendation_status"] == "BUY_CANDIDATE"
    assert status["cheapest_budget_compliant_offer"] == 44.98


def test_pc001_reimport_and_observation_history_are_idempotent(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    case_path = "30-Procurement/cases/PC-0001-Router-USV.yaml"
    import_case(config, case_path)
    import_case(config, case_path)
    add_product(config, "PROD-PC001-002", "Historienprodukt", case_id="PC-0001")
    add_offer(config, "OFFER-PC001-002", "PROD-PC001-002", "VENDOR-002", "Händler", "40.00", "0", "EUR", "available", "manual", case_id="PC-0001")
    add_offer(config, "OFFER-PC001-002", "PROD-PC001-002", "VENDOR-002", "Händler", "35.00", "0", "EUR", "available", "manual", case_id="PC-0001")
    assert len(history_for_case(config, "PC-0001")) == 2


def test_json_ld_adapter_reads_fixture_and_handles_invalid_source():
    parsed = parse_json_ld_file("30-Procurement/tests/fixtures/router-ups-jsonld.html")
    assert parsed["product_name"] == "Beispiel Router-USV"
    assert parsed["price"] == "39.99"
    assert parsed["availability"] == "instock"
    try:
        parse_json_ld_file("30-Procurement/tests/fixtures/does-not-exist.html")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing fixture did not fail")


def test_json_ld_adapter_reports_malformed_source(tmp_path):
    fixture = tmp_path / "broken.html"
    fixture.write_text('<script type="application/ld+json">{broken</script>', encoding="utf-8")
    try:
        parse_json_ld_file(fixture)
    except AdapterError:
        pass
    else:
        raise AssertionError("malformed JSON-LD did not fail")


def test_json_ld_adapter_allows_missing_optional_fields(tmp_path):
    fixture = tmp_path / "partial.html"
    fixture.write_text('<script type="application/ld+json">{"@type":"Product","name":"Partial"}</script>', encoding="utf-8")
    parsed = parse_json_ld_file(fixture)
    assert parsed["product_name"] == "Partial"
    assert parsed["price"] is None


def test_event_deduplication_for_unknown_requirements(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    import_case(config, "30-Procurement/cases/PC-0001-Router-USV.yaml")
    add_product(config, "PROD-UNKNOWN", "Unbewertetes Produkt", case_id="PC-0001")
    add_offer(config, "OFFER-UNKNOWN", "PROD-UNKNOWN", "VENDOR-UNKNOWN", "Händler", "39.99", "0", "EUR", "in_stock", "manual", case_id="PC-0001")
    run_watch(config)
    connection = sqlite3.connect(config.database_path)
    first_count = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    connection.close()
    run_watch(config)
    connection = sqlite3.connect(config.database_path)
    second_count = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    connection.close()
    assert first_count > 0
    assert second_count == first_count


def test_price_observations_are_immutable(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    init_database(config)
    add_product(config, "PROD-IMMUTABLE", "Immutable Test")
    added = add_offer(config, "OFFER-IMMUTABLE", "PROD-IMMUTABLE", "VENDOR-IMMUTABLE", "Test Vendor", "10.00", "0", "EUR", "available", "manual")
    connection = sqlite3.connect(config.database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.execute("UPDATE price_observations SET total_price_cents = 1 WHERE observation_id = ?", (added["observation_id"],))
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("price observation update was not blocked")
    finally:
        connection.close()


def test_watch_run_writes_report_and_structured_log(tmp_path):
    config = resolve_config(
        environ={
            "HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db"),
            "HDC_PROCUREMENT_LOGS": str(tmp_path / "logs"),
            "HDC_PROCUREMENT_REPORTS": str(tmp_path / "reports"),
        },
        repository_root=REPO_ROOT,
    )
    import_case(config, "30-Procurement/cases/PC-0001-Router-USV.yaml")
    result = run_watch(config)
    report = config.reports_path / "PC-0001.html"
    log_file = config.logs_path / "procurement-watch.jsonl"
    assert result["status"] == "succeeded"
    assert report.exists()
    assert "PC-0001" in report.read_text(encoding="utf-8")
    assert "<script src=" not in report.read_text(encoding="utf-8")
    assert log_file.exists()
    assert '"watch_run_id"' in log_file.read_text(encoding="utf-8")


def test_operational_health_and_read_models(tmp_path):
    config = resolve_config(
        environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")},
        repository_root=REPO_ROOT,
    )
    init_database(config)
    health = doctor(config)
    assert health["ok"] is True
    assert current_events(config)["initialized"] is True
    assert recent_watch_runs(config)["runs"] == []


def test_database_backup_and_restore(tmp_path):
    config = resolve_config(
        environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")},
        repository_root=REPO_ROOT,
    )
    init_database(config)
    backup = backup_database(config, tmp_path / "backup" / "procurement.db")
    config.database_path.unlink()
    restored = restore_database(config, backup)
    assert restored == config.database_path
    assert schema_status(config)["schema_version"] == "003"


def test_event_classification_contract_is_persisted(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    init_database(config)
    connection = sqlite3.connect(config.database_path)
    emit_event(connection, None, "BUY_CANDIDATE", "case:buy", "Review purchase candidate.")
    connection.commit()
    event = connection.execute("SELECT event_type, severity FROM events WHERE deduplication_key = 'case:buy'").fetchone()
    connection.close()
    assert event == ("BUY_CANDIDATE", "ACTION_REQUIRED")
    assert set(EVENT_SEVERITIES) == {"INFO", "NOTICE", "WARNING", "ACTION_REQUIRED", "ERROR"}
    assert "CASE_CHANGED" in EVENT_TYPES
    assert classify_event("SOURCE_FAILED") == "ERROR"
