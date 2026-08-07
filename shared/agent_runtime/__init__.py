"""Generic, domain-neutral runtime for HDC-OS agents."""

from .contracts import (
    Agent,
    AgentResult,
    LifecycleState,
    Trigger,
)
from .runtime import AgentRuntime

__all__ = [
    "Agent",
    "AgentResult",
    "AgentRuntime",
    "LifecycleState",
    "Trigger",
]
