from dataclasses import dataclass
from pathlib import Path

import yaml

from .contracts import ProviderKind


@dataclass(frozen=True)
class IntelligenceConfig:
    provider: ProviderKind
    model: str
    endpoint: str
    timeout_seconds: float


def load_intelligence_config(repository_root: Path) -> IntelligenceConfig:
    path = Path(repository_root) / "10-Engineering" / "config" / "intelligence.yaml"
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    provider = ProviderKind(str(value.get("provider", "")).upper())
    if not value.get("model"):
        raise ValueError("A local Intelligence Layer model is required")
    return IntelligenceConfig(provider, str(value["model"]), str(value.get("endpoint", "")), float(value.get("timeout_seconds", 180)))
