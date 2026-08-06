from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping, Protocol, runtime_checkable


class LifecycleState(StrEnum):
    IDLE = "IDLE"
    TRIGGERED = "TRIGGERED"
    COLLECT = "COLLECT"
    ANALYZE = "ANALYZE"
    GENERATE_REPORT = "GENERATE_REPORT"
    WAIT_FOR_OWNER = "WAIT_FOR_OWNER"
    COMPLETED = "COMPLETED"


LIFECYCLE = tuple(LifecycleState)


class Trigger(StrEnum):
    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"
    EVENT = "EVENT"


@dataclass(frozen=True)
class AgentResult:
    report: Mapping[str, Any]
    case_count: int
    recommendation_count: int
    errors: tuple[Mapping[str, Any], ...] = ()
    status: str = "SUCCESS"
    failed_phase: str | None = None


@runtime_checkable
class AnalysisProvider(Protocol):
    """Read-only boundary: providers receive only a serializable context."""

    def analyze(self, context: Mapping[str, Any]) -> Mapping[str, Any]: ...


@runtime_checkable
class Agent(Protocol):
    agent_id: str
    name: str
    version: str
    owner: str
    responsibility: str
    supported_triggers: frozenset[Trigger]
    input_contract: Mapping[str, Any]
    output_contract: Mapping[str, Any]
    current_state: LifecycleState
    execution_result: AgentResult | None
    execution_metadata: Mapping[str, Any]

    def collect(self, trigger: Trigger, payload: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def analyze(self, context: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def generate_report(self, context: Mapping[str, Any], analysis: Mapping[str, Any]) -> AgentResult: ...
    def persist_report(self, result: AgentResult) -> str: ...
    def dashboard_contracts(self, result: AgentResult, execution: Mapping[str, Any]) -> list[Mapping[str, Any]]: ...


@dataclass
class ExecutionTrace:
    states: list[LifecycleState] = field(default_factory=lambda: [LifecycleState.IDLE])

    def advance(self, state: LifecycleState) -> None:
        expected = LIFECYCLE[len(self.states)]
        if state != expected:
            raise ValueError(f"Invalid lifecycle transition: expected {expected}, got {state}")
        self.states.append(state)
