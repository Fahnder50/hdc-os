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
    daily_at: str
    task_name: str
    source_path: Path


def load_agent_config(repository_root: Path) -> AgentConfig:
    path = Path(repository_root) / "30-Procurement" / "config" / "agent.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    agent = document.get("agent", {})
    scheduler = document.get("scheduler", {})
    provider = str(agent.get("provider", ""))
    if provider != "ollama":
        raise ValueError("Only the local Ollama provider is supported; cloud providers are forbidden")
    daily_at = str(scheduler.get("daily_at", ""))
    parts = daily_at.split(":")
    if len(parts) != 2 or not all(part.isdigit() for part in parts) or not (0 <= int(parts[0]) <= 23 and 0 <= int(parts[1]) <= 59):
        raise ValueError("scheduler.daily_at must use HH:MM")
    return AgentConfig(
        provider=provider,
        model=str(agent.get("model", "")),
        endpoint=str(agent.get("endpoint", "")),
        timeout_seconds=float(agent.get("timeout_seconds", 180)),
        deterministic_fallback=bool(agent.get("deterministic_fallback", False)),
        daily_at=daily_at,
        task_name=str(scheduler.get("task_name", "HDC-OS Procurement Agent")),
        source_path=path,
    )
