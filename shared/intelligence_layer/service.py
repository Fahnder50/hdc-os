from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable, Mapping

from .builders import ContextBuilder, PromptBuilder
from .memory import DecisionMemory, FeedbackMemory
from .metrics import IntelligenceMetrics


@dataclass(frozen=True)
class IntelligenceOutcome:
    analysis: Mapping[str, Any]
    metadata: Mapping[str, Any]


class IntelligenceLayer:
    """The single domain-neutral knowledge and decision service."""

    def __init__(self, provider, retriever, decision_memory: DecisionMemory, metrics: IntelligenceMetrics, context_builder=None, prompt_builder=None, feedback_memory: FeedbackMemory | None = None):
        self.provider, self.retriever = provider, retriever
        self.decision_memory, self.metrics = decision_memory, metrics
        self.feedback_memory = feedback_memory
        self.context_builder = context_builder or ContextBuilder()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def record_owner_decision(self, *, recommendation: str, owner_decision: str, reason: str, timestamp: str, procurement_case: str) -> None:
        if self.feedback_memory is None:
            raise RuntimeError("Feedback Memory is not configured")
        decision = {"recommendation": recommendation, "owner_decision": owner_decision, "reason": reason, "timestamp": timestamp, "procurement_case": procurement_case}
        # Both memories validate the closed feedback enum before either file is changed.
        if owner_decision not in {"ACCEPT", "REJECT", "DEFER"}:
            raise ValueError("Owner decision must be ACCEPT, REJECT or DEFER")
        self.decision_memory.record(decision)
        self.feedback_memory.record(procurement_case, owner_decision, timestamp)

    def analyze(self, *, role: str, task: str, request: Mapping[str, Any], schema: Mapping[str, Any], validate: Callable[[Mapping[str, Any]], None], fallback=None, fallback_validate: Callable[[Mapping[str, Any]], None] | None = None) -> IntelligenceOutcome:
        started = perf_counter()
        case_ids = {item["case_id"] for item in request.get("cases", [])}
        terms = tuple(sorted(case_ids | {"procurement", "sprint", "bottleneck", "deployment", "governance"}))
        knowledge = self.retriever.retrieve(terms)
        decisions = self.decision_memory.relevant(case_ids)
        context = self.context_builder.build(request, knowledge, decisions)
        prompt = self.prompt_builder.build(role, task, context, schema)
        fallback_used = schema_error = False
        provider_error = None
        active = self.provider
        try:
            analysis = active.generate(prompt, schema)
            validate(analysis)
            successful = True
        except Exception as error:
            provider_error = error
            schema_error = error.__class__.__name__ == "SchemaValidationError"
            if fallback is None:
                self.metrics.record(perf_counter() - started, False, schema_error, False)
                raise
            fallback_used, successful, active = True, False, fallback
            try:
                analysis = fallback.analyze(request)
                (fallback_validate or validate)(analysis)
            except Exception:
                self.metrics.record(perf_counter() - started, False, schema_error, True)
                raise
        values = self.metrics.record(perf_counter() - started, successful, schema_error, fallback_used)
        metadata = {
            "provider": getattr(active, "provider_name", active.__class__.__name__), "model": getattr(active, "model", "unknown"),
            "configured_provider": self.provider.provider_name, "configured_model": self.provider.model,
            "fallback_used": fallback_used, "provider_error": str(provider_error) if provider_error else None,
            "knowledge_sources": [{"source": item.source.value, "reference": item.reference} for item in knowledge],
            "considered_decisions": list(decisions), "metrics": values,
        }
        return IntelligenceOutcome(analysis, metadata)
