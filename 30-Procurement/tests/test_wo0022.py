from pathlib import Path

import procurement_watch.cli as cli
import procurement_watch.services as services
from procurement_watch.config import resolve_config
from procurement_watch.services import import_all_cases, import_case, portfolio_status, portfolio_watch


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_import_all_imports_the_portfolio(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    result = import_all_cases(config)
    assert result["count"] == 5
    assert {item["case_id"] for item in result["imported"]} == {"PC-0001", "PC-0002", "PC-0003", "PC-0004", "PC-0005"}


def test_portfolio_watch_continues_after_case_failure(monkeypatch, tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    import_all_cases(config)
    called = []

    def fake_watch(_config, case_id):
        called.append(case_id)
        if case_id == "PC-0004":
            raise RuntimeError("source unavailable")
        return {"status": "succeeded", "recommendation_status": "REVIEW", "offers_processed": 2, "failed_sources": 0}

    monkeypatch.setattr(services, "run_live_watch", fake_watch)
    result = portfolio_watch(config)
    assert called == ["PC-0001", "PC-0002", "PC-0003", "PC-0004", "PC-0005"]
    assert result["status"] == "completed_with_warnings"
    assert result["error_count"] == 1
    assert result["cases"][3]["status"] == "FAILED"


def test_portfolio_status_counts_active_case_recommendations(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    import_case(config, REPO_ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    result = portfolio_status(config)
    assert result["initialized"] is True
    assert result["active_cases"] == 1
    assert result["statuses"]["NO_CANDIDATE"] == 1
    assert result["last_run"] is None


def test_cli_watch_all_returns_warning_exit_code_without_aborting(monkeypatch, capsys):
    monkeypatch.setattr(cli, "portfolio_watch", lambda _config: {
        "cases": [{"case_id": "PC-0004", "status": "FAILED", "offers": 0, "sources": 1, "errors": 1, "error": "offline"}],
        "case_count": 1,
        "offer_count": 0,
        "source_count": 1,
        "error_count": 1,
        "duration_seconds": 0.1,
        "health": {"watching": 1, "conditional_buy": 0, "review": 0, "blocked": 0, "errors": 1},
        "status": "completed_with_warnings",
    })
    assert cli.main(["watch", "live", "--all"]) == 1
    assert "Portfolio completed with warnings." in capsys.readouterr().out
