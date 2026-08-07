import json
from pathlib import Path

import pytest

from procurement_agent.agent import ProcurementAgent
from procurement_agent.analyzers import DeterministicFallbackAnalysisProvider, OllamaLocalAnalysisProvider
from procurement_agent.config import load_agent_config
from shared.agent_runtime import AgentResult, AgentRuntime, LifecycleState, Trigger
from shared.agent_runtime.scheduler import SchedulerTrigger
from shared.scheduler_lifecycle.registry import load_registry
from shared.intelligence_layer import DecisionMemory, IntelligenceLayer, IntelligenceMetrics, load_intelligence_config


ROOT = Path(__file__).resolve().parents[2]


class FakeAgent:
    agent_id = "fake-agent"
    name = "Fake"
    version = "1.0"
    owner = "Owner"
    responsibility = "Test one runtime contract."
    supported_triggers = frozenset({Trigger.MANUAL, Trigger.SCHEDULED})
    input_contract = {}
    output_contract = {}
    current_state = LifecycleState.IDLE
    execution_result = None

    def collect(self, trigger, payload):
        return {"case": "C-1"}

    def analyze(self, context):
        return {"recommendations": []}

    def generate_report(self, context, analysis):
        return AgentResult({"ok": True}, 1, 0)

    def persist_report(self, result):
        return "summary.json"


def test_runtime_enforces_complete_lifecycle_and_one_log(tmp_path):
    agent = FakeAgent()
    result = AgentRuntime(tmp_path).execute(agent, Trigger.MANUAL)
    assert result["lifecycle"] == [state.value for state in LifecycleState]
    assert result["exit_status"] == "SUCCESS"
    assert agent.current_state == LifecycleState.COMPLETED
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_scheduler_only_supplies_scheduled_trigger(tmp_path):
    result = SchedulerTrigger(AgentRuntime(tmp_path)).start(FakeAgent())
    assert result["trigger"] == "SCHEDULED"


def test_event_trigger_is_prepared_but_not_implemented(tmp_path):
    with pytest.raises(ValueError, match="reserved"):
        AgentRuntime(tmp_path).execute(FakeAgent(), Trigger.EVENT)


class CapturingAnalyzer:
    def __init__(self):
        self.context = None

    provider_name = "local-model"
    model = "test-model"

    def generate(self, prompt, schema):
        self.context = prompt
        return {
            "executive_summary": "Local analysis",
            "procurement_recommendations": [{
                "case_id": "PC-1", "recommendation": "NO_ACTION",
                "information_status": "INFORMATION", "reasoning": "No change."
            }],
        }


class EmptyRetriever:
    def retrieve(self, terms): return ()


def _intelligence(tmp_path, provider):
    return IntelligenceLayer(provider, EmptyRetriever(), DecisionMemory(tmp_path / "decisions.json"), IntelligenceMetrics(tmp_path / "metrics.json"))


def test_analyzer_receives_serializable_context_only_and_owner_keeps_authority(tmp_path):
    analyzer = CapturingAnalyzer()
    schemas = ROOT / "30-Procurement" / "schema"
    agent = ProcurementAgent(object(), tmp_path, _intelligence(tmp_path, analyzer), schemas_directory=schemas)
    context = {"cases": [{"case_id": "PC-1"}], "case_errors": []}
    analysis = agent.analyze(context)
    assert json.dumps(context) in analyzer.context
    result = agent.generate_report(context, analysis)
    assert result.recommendation_count == 1
    assert result.report["approval"] == {
        "decision_authority": "Project Owner",
        "agent_may_decide": False,
        "owner_options": ["ACCEPT", "REJECT", "DEFER"],
    }


@pytest.mark.parametrize("recommendation", ["BUY_NOW", "ORDER", "APPROVE"])
def test_forbidden_recommendations_are_rejected(tmp_path, recommendation):
    agent = ProcurementAgent(object(), tmp_path, schemas_directory=ROOT / "30-Procurement" / "schema")
    context = {"cases": [{"case_id": "PC-1"}], "case_errors": []}
    analysis = {"recommendations": [{
        "case_id": "PC-1", "recommendation": recommendation,
        "information_status": "INFORMATION", "reason": "invalid"
    }]}
    with pytest.raises(ValueError, match="forbidden recommendation"):
        agent.generate_report(context, analysis)


def test_exactly_one_recommendation_per_case_is_required(tmp_path):
    agent = ProcurementAgent(object(), tmp_path, schemas_directory=ROOT / "30-Procurement" / "schema")
    context = {"cases": [{"case_id": "PC-1"}, {"case_id": "PC-2"}], "case_errors": []}
    with pytest.raises(ValueError, match="exactly one"):
        agent.generate_report(context, {"recommendations": []})


class FailingAgent(FakeAgent):
    def analyze(self, context):
        raise RuntimeError("model unavailable")


def test_failed_runs_reach_completed_and_identify_failed_phase(tmp_path):
    agent = FailingAgent()
    result = AgentRuntime(tmp_path).execute(agent, Trigger.MANUAL)
    assert result["execution_result"] == "FAILED"
    assert result["failed_phase"] == "ANALYZE"
    assert result["lifecycle"] == [state.value for state in LifecycleState]
    assert agent.current_state == LifecycleState.COMPLETED
    assert len(list(tmp_path.glob("*.json"))) == 1


@pytest.mark.parametrize("endpoint", ["https://127.0.0.1:11434", "http://example.com", "http://8.8.8.8:11434"])
def test_model_provider_technically_rejects_cloud_endpoints(endpoint):
    with pytest.raises(ValueError):
        OllamaLocalAnalysisProvider("llama3.2:3b", endpoint, 1)


def test_provider_and_model_are_configuration_driven():
    config = load_intelligence_config(ROOT)
    assert config.provider.value == "OLLAMA"
    assert config.model == "llama3.2:3b"


def test_schema_invalid_model_response_uses_explicit_fallback(tmp_path):
    class InvalidModel:
        provider_name = "ollama"
        model = "test-model"

        def generate(self, prompt, schema):
            return {"recommendations": []}

    agent = ProcurementAgent(
        object(), tmp_path, _intelligence(tmp_path, InvalidModel()),
        fallback_provider=DeterministicFallbackAnalysisProvider(),
        schemas_directory=ROOT / "30-Procurement" / "schema",
    )
    context = {"cases": [{"case_id": "PC-1", "current_evaluation": "WATCHING", "changes": {}}], "case_errors": []}
    analysis = agent.analyze(context)
    assert len(analysis["recommendations"]) == 1
    assert agent.execution_metadata["fallback_used"] is True
    assert agent.execution_metadata["provider"] == "deterministic-fallback"


def test_procurement_scheduler_is_owned_by_scheduler_registry():
    entries = load_registry(ROOT / "20-Operations" / "config" / "schedulers.yaml")
    assert len(entries) == 1
    assert entries[0]["scheduler_id"] == "procurement-agent-daily"
    assert entries[0]["schedule"]["at"] == "07:00"
