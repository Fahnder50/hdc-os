from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class AgentConfig:
    provider: str
    model: str
    endpoint: str
    timeout_seconds: float
    deterministic_fallback: bool
    source_path: Path


def load_agent_config(repository_root: Path) -> AgentConfig:
    path = Path(repository_root) / "30-Procurement" / "config" / "agent.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    agent = document.get("agent", {})
    provider = str(agent.get("provider", ""))
    if provider != "ollama":
        raise ValueError("Only the local Ollama provider is supported; cloud providers are forbidden")
    return AgentConfig(
        provider=provider,
        model=str(agent.get("model", "")),
        endpoint=str(agent.get("endpoint", "")),
        timeout_seconds=float(agent.get("timeout_seconds", 180)),
        deterministic_fallback=bool(agent.get("deterministic_fallback", False)),
        source_path=path,
    )
