import os

from operations_cockpit.runtime import CockpitRuntime
import operations_cockpit.render as render_module
from shared.agent_runtime import AgentResult, AgentRuntime, LifecycleState, Trigger


def _contract(domain):
    return {"domain": {"id": domain, "version": "1.0"}, "health": "HEALTHY", "summary": "current", "status": "CURRENT", "last_update": "2026-08-06T07:00:00Z", "requires_action": False, "recommendations": [], "links": []}


class FakeAgent:
    agent_id = "fake-agent"
    name = "Fake"
    version = "1.0"
    owner = "Owner"
    responsibility = "Test runtime refresh."
    supported_triggers = frozenset({Trigger.MANUAL})
    input_contract = {}
    output_contract = {}
    current_state = LifecycleState.IDLE
    execution_result = None
    execution_metadata = {}

    def collect(self, trigger, payload): return {"case": "C-1"}
    def analyze(self, context): return {}
    def generate_report(self, context, analysis): return AgentResult({"ok": True}, 1, 0)
    def persist_report(self, result): return "summary.json"


class FailingAgent(FakeAgent):
    def analyze(self, context): raise RuntimeError("failed")


class DashboardAgent(FakeAgent):
    def dashboard_contracts(self, result, execution):
        return [_contract("test-agent")]


class FailingDashboardAgent(FailingAgent):
    def dashboard_contracts(self, result, execution):
        raise AssertionError("failed agents must not publish dashboard contracts")


def test_successful_agent_run_publishes_contracts_and_refreshes_exactly_once(tmp_path):
    contracts = []
    refreshes = []
    result = AgentRuntime(tmp_path / "logs", contracts.append, lambda: refreshes.append("refresh")).execute(DashboardAgent(), Trigger.MANUAL)
    assert result["execution_result"] == "SUCCESS"
    assert len(contracts) == 1
    assert refreshes == ["refresh"]
    assert result["dashboard_refresh"]["result"] == "SUCCESS"


def test_failed_agent_run_never_refreshes(tmp_path):
    refreshes = []
    result = AgentRuntime(tmp_path / "logs", lambda value: None, lambda: refreshes.append("refresh")).execute(FailingDashboardAgent(), Trigger.MANUAL)
    assert result["execution_result"] == "FAILED"
    assert result["dashboard_refresh"]["result"] == "NOT_RUN"
    assert refreshes == []


def test_refresh_failure_preserves_both_previous_views(tmp_path, monkeypatch):
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    (contracts / "domain.json").write_text(__import__("json").dumps(_contract("domain")), encoding="utf-8")
    (tmp_path / "Latest.md").write_text("old markdown", encoding="utf-8")
    (tmp_path / "Latest.html").write_text("old html", encoding="utf-8")
    real_replace = os.replace
    calls = {"count": 0}

    def fail_second(source, destination):
        calls["count"] += 1
        if calls["count"] == 2:
            raise OSError("controlled replacement failure")
        return real_replace(source, destination)

    monkeypatch.setattr(render_module.os, "replace", fail_second)
    try:
        CockpitRuntime(tmp_path).build()
    except OSError:
        pass
    assert (tmp_path / "Latest.md").read_text(encoding="utf-8") == "old markdown"
    assert (tmp_path / "Latest.html").read_text(encoding="utf-8") == "old html"
    assert "controlled replacement failure" in (tmp_path / ".refresh.log").read_text(encoding="utf-8")


def test_refresh_status_is_rendered_from_same_model(tmp_path):
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    (contracts / "domain.json").write_text(__import__("json").dumps(_contract("domain")), encoding="utf-8")
    CockpitRuntime(tmp_path).build()
    markdown = (tmp_path / "Latest.md").read_text(encoding="utf-8")
    assert "## Cockpit Refresh" in markdown
    assert "Refresh Result:** SUCCESS" in markdown
