from pathlib import Path
import sqlite3

import pytest
import yaml

import procurement_watch.services as services
from procurement_watch.config import resolve_config
from procurement_watch.services import case_status, import_all_cases, import_case, portfolio_watch, run_live_watch


ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml"
ASSET = ROOT / "20-Operations/assets/records/UPS-RTR-01.yaml"
ACCEPTANCE = ROOT / "20-Operations/assets/acceptance/UPS-RTR-01.yaml"


def config(tmp_path):
    return resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=ROOT)


def test_pc0001_is_purchased_and_not_watched_or_recommended(monkeypatch, tmp_path):
    runtime = config(tmp_path)
    import_all_cases(runtime)
    called = []
    monkeypatch.setattr(services, "run_live_watch", lambda _config, case_id: called.append(case_id) or {
        "recommendation_status": "REVIEW", "failed_sources": 0, "status": "succeeded",
    })
    result = portfolio_watch(runtime)
    assert "PC-0001" not in called
    assert called == ["PC-0002", "PC-0003", "PC-0004", "PC-0005"]
    status = case_status(runtime, "PC-0001")
    assert status["case_status"] == "PURCHASED"
    assert status["watch_enabled"] is False
    assert status["recommendation_status"] == "CLOSED"
    assert result["case_count"] == 4
    with pytest.raises(ValueError, match="not active for watching"):
        run_live_watch(runtime, "PC-0001")


def test_reimporting_closed_case_preserves_procurement_history(tmp_path):
    runtime = config(tmp_path)
    import_case(runtime, CASE)
    connection = sqlite3.connect(runtime.database_path)
    case_id = connection.execute("SELECT id FROM procurement_cases WHERE case_id = 'PC-0001'").fetchone()[0]
    before_requirements = connection.execute("SELECT COUNT(*) FROM requirements WHERE case_id = ?", (case_id,)).fetchone()[0]
    connection.execute(
        "INSERT INTO evaluations(evaluation_id, case_id, rule_id, result, reason, evaluated_at) VALUES ('WO36-HISTORY', ?, 'HISTORY', 'PASS', 'preserved', '2026-08-03T00:00:00Z')",
        (case_id,),
    )
    connection.commit()
    connection.close()
    import_case(runtime, CASE)
    connection = sqlite3.connect(runtime.database_path)
    assert connection.execute("SELECT COUNT(*) FROM requirements WHERE case_id = ?", (case_id,)).fetchone()[0] >= before_requirements
    assert connection.execute("SELECT COUNT(*) FROM evaluations WHERE evaluation_id = 'WO36-HISTORY'").fetchone()[0] == 1
    connection.close()


def test_asset_data_external_loads_and_completed_acceptance_are_synchronized():
    asset = yaml.safe_load(ASSET.read_text(encoding="utf-8"))
    acceptance = yaml.safe_load(ACCEPTANCE.read_text(encoding="utf-8"))
    assert asset["manufacturer"] == "Eaton"
    assert asset["model"] == "3S850D"
    assert acceptance["product_name"] == "Eaton 3S 850 DIN"
    assert asset["status"] == "PRODUCTION"
    assert asset["mounted_in_rack"] is False and asset["infrastructure"] == "gateway"
    assert {item["name"] for item in acceptance["external_loads"]} == {
        "Speedport Smart 4", "Telefon", "Elspet Automatic Litter Box",
    }
    assert all(item["registered_asset"] is False for item in acceptance["external_loads"])
    assert acceptance["production_transition_allowed"] is True
    assert acceptance["acceptance_blockers"] == []


def test_litter_box_is_external_and_not_registered_as_asset():
    registry = yaml.safe_load((ROOT / "20-Operations/assets/registry.yaml").read_text(encoding="utf-8"))
    assert "Elspet-Automatic-Litter-Box" in registry["external_components"]
    assert all(item["asset_id"] != "Elspet-Automatic-Litter-Box" for item in registry["assets"])


def test_other_procurement_cases_remain_watching():
    for case_id in range(2, 6):
        path = next((ROOT / "30-Procurement/cases").glob(f"PC-{case_id:04d}-*.yaml"))
        assert yaml.safe_load(path.read_text(encoding="utf-8"))["status"] == "WATCHING"


def test_wo0036_acceptance_metadata_is_complete():
    case = yaml.safe_load(CASE.read_text(encoding="utf-8"))
    handover = (ROOT / "20-Operations/WO-0036-Procurement-to-Asset-Handover.md").read_text(encoding="utf-8")
    assert case["reviewed_by"] == "Lead Architect"
    assert str(case["last_review"]) == "2026-08-03"
    assert "status: Accepted" in handover
    assert "reviewed_by: Lead Architect" in handover
    assert 'last_review: "2026-08-03"' in handover
