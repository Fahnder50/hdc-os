from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class AgentConfig:
    deterministic_fallback: bool
    source_path: Path


def load_agent_config(repository_root: Path) -> AgentConfig:
    path = Path(repository_root) / "30-Procurement" / "config" / "agent.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    agent = document.get("agent", {})
    return AgentConfig(
        deterministic_fallback=bool(agent.get("deterministic_fallback", False)),
        source_path=path,
    )
