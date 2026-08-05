from dataclasses import dataclass
from typing import Any, Mapping

from .contracts import Agent, Trigger
from .runtime import AgentRuntime


@dataclass(frozen=True)
class SchedulerTrigger:
    """Thin scheduler boundary. Scheduling and domain evaluation stay separate."""

    runtime: AgentRuntime

    def start(self, agent: Agent, payload: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        return self.runtime.execute(agent, Trigger.SCHEDULED, payload)
