from dataclasses import dataclass
import os
from pathlib import Path

import yaml


@dataclass(frozen=True)
class AppConfig:
    database_path: Path
    logs_path: Path
    reports_path: Path
    repository_root: Path
    repository_version: str | None


def resolve_config(environ=None, repository_root=None):
    values = os.environ if environ is None else environ
    root = Path(repository_root or Path(__file__).resolve().parents[3])
    return AppConfig(
        database_path=Path(values.get("HDC_PROCUREMENT_DB", r"C:\HDC\Data\procurement\procurement.db")),
        logs_path=Path(values.get("HDC_PROCUREMENT_LOGS", r"C:\HDC\Data\procurement\logs")),
        reports_path=Path(values.get("HDC_PROCUREMENT_REPORTS", r"C:\HDC\Data\procurement\reports")),
        repository_root=root,
        repository_version=values.get("HDC_REPOSITORY_VERSION"),
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
