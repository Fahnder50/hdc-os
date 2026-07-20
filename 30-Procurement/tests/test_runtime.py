import sqlite3

import procurement_watch.cli as cli
import procurement_watch.services as services_module
from procurement_watch.config import load_yaml_config, resolve_config
from procurement_watch.database import schema_status
from procurement_watch.services import init_database, procurement_status, run_watch


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
        repository_root=tmp_path,
    )
    first = init_database(config)
    second = init_database(config)
    assert first["schema_version"] == "001"
    assert second["repository_version"] == "knowledge-v1.2"
    connection = sqlite3.connect(config.database_path)
    metadata = dict(connection.execute("SELECT metadata_key, metadata_value FROM runtime_metadata").fetchall())
    migration_count = connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
    connection.close()
    assert len(metadata["repository_commit"]) == 40
    assert all(character in "0123456789abcdef" for character in metadata["repository_commit"])
    assert metadata["repository_version"] == "knowledge-v1.2"
    assert metadata["schema_version"] == "001"
    assert migration_count == 1


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
    assert status["schema_version"] == "001"
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
