import json
from pathlib import Path

import pytest

from procurement_agent.agent import ProcurementAgent
from procurement_agent.analyzers import ANALYSIS_SCHEMA, DeterministicFallbackAnalysisProvider, SchemaValidationError
from shared.intelligence_layer import (
    ContextBuilder, DecisionMemory, FeedbackMemory, IntelligenceLayer, IntelligenceMetrics,
    KnowledgeItem, PromptBuilder, ProviderKind, RepositoryKnowledgeRetriever, RetrievalSource,
)


ROOT = Path(__file__).resolve().parents[2]


class Provider:
    provider_kind = ProviderKind.LOCAL_MODEL
    provider_name = "local-test"
    model = "test"

    def __init__(self, response): self.response, self.prompt = response, None
    def generate(self, prompt, schema): self.prompt = prompt; return self.response


class Retriever:
    def __init__(self): self.terms = None
    def retrieve(self, terms):
        self.terms = terms
        return (KnowledgeItem(RetrievalSource.PROCUREMENT_CASES, "case.md", "PC-1 relevant"),)


def _response():
    return {"executive_summary": "Summary", "procurement_recommendations": [{"case_id": "PC-1", "recommendation": "NO_ACTION", "information_status": "INFORMATION", "reasoning": "No change."}]}


def _layer(tmp_path, provider, retriever=None):
    return IntelligenceLayer(provider, retriever or Retriever(), DecisionMemory(tmp_path / "decisions.json"), IntelligenceMetrics(tmp_path / "metrics.json"))


def test_exactly_one_domain_neutral_intelligence_layer_drives_procurement(tmp_path):
    provider, retriever = Provider(_response()), Retriever()
    agent = ProcurementAgent(object(), tmp_path, _layer(tmp_path, provider, retriever), schemas_directory=ROOT / "30-Procurement" / "schema")
    context = {"cases": [{"case_id": "PC-1"}], "case_errors": []}
    assert agent.analyze(context)["summary"] == "Summary"
    assert "PC-1" in retriever.terms
    assert "OUTPUT JSON SCHEMA" in provider.prompt
    assert "RepositoryKnowledgeRetriever" not in provider.prompt
    assert set(_response()) == {"executive_summary", "procurement_recommendations"}


def test_retrieval_source_allowlist_is_exact_and_no_repository_walk(tmp_path):
    allowed = {item.value for item in RetrievalSource}
    assert allowed == {"ACCEPTED_ARCHITECTURE", "PROCUREMENT_CASES", "PROCUREMENT_REPORTS", "PROCUREMENT_HISTORY", "ASSET_STATUS", "GOVERNANCE_RULES", "CURRENT_SPRINT", "CURRENT_BOTTLENECK", "CURRENT_DEPLOYMENT_STATE"}
    forbidden = tmp_path / "secret.txt"
    forbidden.write_text("PC-1 must never be retrieved", encoding="utf-8")
    items = RepositoryKnowledgeRetriever(ROOT, tmp_path / "reports", tmp_path / "history").retrieve(("PC-1",))
    assert all("secret.txt" not in item.reference for item in items)


def test_context_and_prompt_builders_are_deterministic_and_limited():
    item = KnowledgeItem(RetrievalSource.PROCUREMENT_CASES, "PC-1.md", "relevant")
    context = ContextBuilder().build({"cases": []}, [item], [])
    first = PromptBuilder().build("role", "task", context, ANALYSIS_SCHEMA)
    second = PromptBuilder().build("role", "task", context, ANALYSIS_SCHEMA)
    assert first == second
    assert set(context) == {"request", "knowledge", "decision_memory"}
    assert first.count("ROLE:") == first.count("ANALYSIS TASK:") == first.count("CONTEXT:") == first.count("OUTPUT JSON SCHEMA:") == 1


def test_decision_and_feedback_memory_accept_only_owner_contract(tmp_path):
    decisions, feedback = DecisionMemory(tmp_path / "decisions.json"), FeedbackMemory(tmp_path / "feedback.json")
    decision = {"recommendation": "NO_ACTION", "owner_decision": "ACCEPT", "reason": "Agreed", "timestamp": "2026-08-07T08:00:00Z", "procurement_case": "PC-1"}
    decisions.record(decision)
    feedback.record("PC-1", "ACCEPT", decision["timestamp"])
    assert decisions.all() == [decision]
    assert len(feedback.all()) == 1
    with pytest.raises(ValueError): feedback.record("PC-1", "APPROVE", decision["timestamp"])
    with pytest.raises(ValueError): decisions.record({**decision, "owner_decision": "APPROVE"})


def test_intelligence_layer_records_exactly_one_feedback_per_owner_decision(tmp_path):
    feedback = FeedbackMemory(tmp_path / "feedback.json")
    layer = IntelligenceLayer(Provider(_response()), Retriever(), DecisionMemory(tmp_path / "decisions.json"), IntelligenceMetrics(tmp_path / "metrics.json"), feedback_memory=feedback)
    values = {"recommendation": "NO_ACTION", "owner_decision": "DEFER", "reason": "Wait", "timestamp": "2026-08-07T08:00:00Z", "procurement_case": "PC-1"}
    layer.record_owner_decision(**values)
    assert len(feedback.all()) == 1
    with pytest.raises(ValueError, match="already recorded"):
        layer.record_owner_decision(**values)
    assert len(feedback.all()) == 1


def test_schema_error_uses_unchanged_fallback_and_persists_metrics(tmp_path):
    provider = Provider({"recommendations": []})
    layer = _layer(tmp_path, provider)
    request = {"cases": [{"case_id": "PC-1", "current_evaluation": "WATCHING", "changes": {}}], "case_errors": []}
    def validate(value):
        if set(value) != set(ANALYSIS_SCHEMA["required"]): raise SchemaValidationError("invalid")
    outcome = layer.analyze(role="role", task="task", request=request, schema=ANALYSIS_SCHEMA, validate=validate, fallback=DeterministicFallbackAnalysisProvider())
    metrics = IntelligenceMetrics(tmp_path / "metrics.json").read()
    assert outcome.metadata["fallback_used"] is True
    assert metrics["ai_calls"] == metrics["schema_errors"] == metrics["fallback_uses"] == 1
    assert metrics["fallback_rate"] == 1.0
    assert metrics["health"] == "DEGRADED"


def test_explainability_and_cockpit_intelligence_contract(tmp_path):
    agent = ProcurementAgent(object(), tmp_path, _layer(tmp_path, Provider(_response())), schemas_directory=ROOT / "30-Procurement" / "schema")
    context = {"cases": [{"case_id": "PC-1"}], "case_errors": []}
    analysis = agent.analyze(context)
    result = agent.generate_report(context, analysis)
    assert result.report["explainability"]["knowledge_sources"]
    assert result.report["explainability"]["reasoning"] == [{"case_id": "PC-1", "reason": "No change."}]
    contracts = agent.dashboard_contracts(result, {"ended_at": "2026-08-07T08:00:00Z", "duration_seconds": 1.0})
    intelligence = next(item for item in contracts if item["domain"]["id"] == "intelligence")
    assert set(("intelligence_health", "active_provider", "model", "fallback_rate", "last_successful_ai_response")) <= set(intelligence["details"])


def test_provider_contract_foresees_only_local_and_deterministic_kinds():
    assert {item.value for item in ProviderKind} == {"OLLAMA", "LLAMACPP", "LOCAL_MODEL", "DETERMINISTIC"}
    layer_files = (ROOT / "shared" / "intelligence_layer").glob("*.py")
    assert all("OllamaProvider" not in path.read_text(encoding="utf-8") for path in layer_files)
