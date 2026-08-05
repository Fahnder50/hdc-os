import ast
from html import unescape
import json
from pathlib import Path

from operations_cockpit.contracts import REQUIRED_FIELDS, load_contracts, validate_contract
from operations_cockpit.runtime import CockpitRuntime
from operations_dashboard.contracts import publish as publish_operations
from procurement_agent.dashboard_contracts import publish as publish_procurement


ROOT = Path(__file__).resolve().parents[2]


def _contract(domain, health="HEALTHY", action=False):
    return {
        "domain": {"id": domain, "version": "1.0"},
        "health": health,
        "summary": f"{domain} summary",
        "status": "CURRENT",
        "last_update": "2026-08-05T08:00:00+02:00",
        "requires_action": action,
        "recommendations": [{"id": domain, "text": f"Review {domain}."}] if action else [],
        "links": [],
        "details": {"value": domain},
    }


def test_contract_has_exact_required_fields_and_one_documented_optional_field():
    value = _contract("future-domain")
    validate_contract(value)
    assert set(REQUIRED_FIELDS) == set(value) - {"details"}


def test_future_domain_is_rendered_without_runtime_changes(tmp_path):
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    (contracts / "security.json").write_text(json.dumps(_contract("security")), encoding="utf-8")
    CockpitRuntime(tmp_path).build()
    assert "## Security" in (tmp_path / "Latest.md").read_text(encoding="utf-8")


def test_runtime_reads_contracts_and_writes_exactly_two_views(tmp_path):
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    for domain in ("procurement", "deployment", "assets", "agents"):
        (contracts / f"{domain}.json").write_text(json.dumps(_contract(domain, "CRITICAL" if domain == "deployment" else "HEALTHY", domain == "deployment")), encoding="utf-8")
    model = CockpitRuntime(tmp_path).build()
    assert model["overall_health"] == "CRITICAL"
    assert {path.name for path in tmp_path.iterdir() if path.is_file() and not path.name.startswith(".")} == {"Latest.md", "Latest.html"}
    markdown = (tmp_path / "Latest.md").read_text(encoding="utf-8")
    html = unescape((tmp_path / "Latest.html").read_text(encoding="utf-8"))
    for section in ("Overall Health", "Today's Summary", "Daily Briefing", "Procurement", "Deployment", "Assets", "Agents", "Recommended Actions"):
        assert section in markdown and section in html
    assert "Review deployment" in markdown and "Review deployment" in html


def test_daily_briefing_contains_only_changes_since_previous_build(tmp_path):
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    path = contracts / "assets.json"
    path.write_text(json.dumps(_contract("assets")), encoding="utf-8")
    CockpitRuntime(tmp_path).build()
    CockpitRuntime(tmp_path).build()
    assert "No important changes since the previous cockpit run." in (tmp_path / "Latest.md").read_text(encoding="utf-8")


def test_cockpit_runtime_has_no_domain_imports():
    forbidden = {"procurement_agent", "procurement_watch", "operations_dashboard", "agent_runtime"}
    for path in (ROOT / "Dashboard" / "src" / "operations_cockpit").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
        imported |= {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        assert not imported & forbidden


def test_operations_producer_publishes_deployment_and_asset_contracts(tmp_path):
    publish_operations(ROOT, tmp_path)
    contracts = {item["domain"]["id"]: item for item in load_contracts(tmp_path)}
    assert contracts["deployment"]["status"] == "NOT_READY"
    assert contracts["deployment"]["details"]["missing_hardware"] == ["OPNsense Firewall", "Managed Switch"]
    assert contracts["assets"]["details"]["productive_assets"] == 1
    assert contracts["assets"]["details"]["asset_health"] == "HEALTHY"


def test_procurement_and_agent_contracts_use_published_agent_outputs(tmp_path, monkeypatch):
    runtime = tmp_path / "runtime"
    (runtime / "logs").mkdir(parents=True)
    (runtime / "executive-summaries").mkdir()
    (runtime / "logs" / "run.json").write_text(json.dumps({
        "ended_at": "2026-08-05T07:01:14+00:00", "execution_result": "SUCCESS", "duration_seconds": 62.6,
        "analysis": {"provider": "deterministic-fallback", "model": "rules-v1", "fallback_used": True}
    }), encoding="utf-8")
    (runtime / "executive-summaries" / "summary.json").write_text(json.dumps({
        "executive_summary": {"summary": "Four cases analyzed."}, "recommendations": [],
        "dashboard": {"active_procurement_cases": 4}
    }), encoding="utf-8")
    monkeypatch.setenv("HDC_AGENT_RUNTIME", str(runtime))
    publish_procurement(tmp_path / "contracts")
    contracts = {item["domain"]["id"]: item for item in load_contracts(tmp_path / "contracts")}
    assert contracts["procurement"]["details"]["active_cases"] == 4
    assert contracts["agents"]["details"]["provider"] == "deterministic-fallback"
    assert contracts["agents"]["details"]["fallback_used"] is True
