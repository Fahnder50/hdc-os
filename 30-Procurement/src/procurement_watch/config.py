from dataclasses import dataclass
import os
from pathlib import Path

import yaml


@dataclass(frozen=True)
class AppConfig:
    runtime_path: Path
    database_path: Path
    logs_path: Path
    reports_path: Path
    repository_root: Path
    repository_version: str | None
    sources_path: Path
    policy_path: Path
    portfolio_path: Path
    request_timeout: float
    user_agent: str
    max_retries: int


def resolve_config(environ=None, repository_root=None):
    values = os.environ if environ is None else environ
    root = Path(repository_root or Path(__file__).resolve().parents[3])
    default_config_root = root / "30-Procurement" / "config"
    runtime_path = Path(values.get("HDC_PROCUREMENT_RUNTIME", root / "30-Procurement" / "runtime"))
    return AppConfig(
        runtime_path=runtime_path,
        database_path=Path(values.get("HDC_PROCUREMENT_DB", runtime_path / "database.sqlite")),
        logs_path=Path(values.get("HDC_PROCUREMENT_LOGS", runtime_path / "logs")),
        reports_path=Path(values.get("HDC_PROCUREMENT_REPORTS", runtime_path / "journals")),
        repository_root=root,
        repository_version=values.get("HDC_REPOSITORY_VERSION"),
        sources_path=Path(values.get("HDC_PROCUREMENT_SOURCES", default_config_root / "sources.yaml")),
        policy_path=Path(values.get("HDC_PROCUREMENT_POLICY", default_config_root / "watch-policy.yaml")),
        portfolio_path=Path(values.get("HDC_PROCUREMENT_PORTFOLIO", default_config_root / "portfolio.yaml")),
        request_timeout=float(values.get("HDC_PROCUREMENT_TIMEOUT", "20")),
        user_agent=values.get("HDC_PROCUREMENT_USER_AGENT", "HDC-Procurement-Watch/0.1"),
        max_retries=int(values.get("HDC_PROCUREMENT_RETRIES", "1")),
    )


def load_yaml_config(path):
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as file:
        value = yaml.safe_load(file)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Configuration root must be a mapping: {config_path}")
    return value
