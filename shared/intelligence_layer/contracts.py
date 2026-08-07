from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping, Protocol


class ProviderKind(StrEnum):
    OLLAMA = "OLLAMA"
    LLAMACPP = "LLAMACPP"
    LOCAL_MODEL = "LOCAL_MODEL"
    DETERMINISTIC = "DETERMINISTIC"


class IntelligenceHealth(StrEnum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    DEGRADED = "DEGRADED"


class RetrievalSource(StrEnum):
    ACCEPTED_ARCHITECTURE = "ACCEPTED_ARCHITECTURE"
    PROCUREMENT_CASES = "PROCUREMENT_CASES"
    PROCUREMENT_REPORTS = "PROCUREMENT_REPORTS"
    PROCUREMENT_HISTORY = "PROCUREMENT_HISTORY"
    ASSET_STATUS = "ASSET_STATUS"
    GOVERNANCE_RULES = "GOVERNANCE_RULES"
    CURRENT_SPRINT = "CURRENT_SPRINT"
    CURRENT_BOTTLENECK = "CURRENT_BOTTLENECK"
    CURRENT_DEPLOYMENT_STATE = "CURRENT_DEPLOYMENT_STATE"


@dataclass(frozen=True)
class KnowledgeItem:
    source: RetrievalSource
    reference: str
    content: str


class IntelligenceProvider(Protocol):
    provider_kind: ProviderKind
    provider_name: str
    model: str

    def generate(self, prompt: str, schema: Mapping[str, Any]) -> Mapping[str, Any]: ...


class KnowledgeRetriever(Protocol):
    def retrieve(self, terms: tuple[str, ...]) -> tuple[KnowledgeItem, ...]: ...
