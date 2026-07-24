from pathlib import Path

from procurement_watch.config import resolve_config
from procurement_watch.database import initialize
from procurement_watch.services import portfolio_status


def test_runtime_bootstrap_creates_separated_structure(tmp_path):
    runtime = tmp_path / "runtime"
    config = resolve_config(environ={"HDC_PROCUREMENT_RUNTIME": str(runtime)}, repository_root=tmp_path)
    initialize(config)
    assert config.database_path == runtime / "database.sqlite"
    assert config.reports_path == runtime / "journals"
    for directory in (runtime, runtime / "journals", runtime / "logs", runtime / "cache", runtime / "observations"):
        assert directory.is_dir()


def test_portfolio_status_exposes_health_shape(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_RUNTIME": str(tmp_path / "runtime")}, repository_root=tmp_path)
    result = portfolio_status(config)
    assert result["initialized"] is False
    assert result["active_cases"] == 0
    assert result["statuses"] == {}
