import json
from pathlib import Path
from typing import Any, Mapping


REQUIRED_FIELDS = ("domain", "health", "summary", "status", "last_update", "requires_action", "recommendations", "links")
HEALTH_VALUES = {"HEALTHY", "WARNING", "CRITICAL"}


def validate_contract(value: Mapping[str, Any]) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in value]
    if missing:
        raise ValueError(f"Dashboard contract is missing: {', '.join(missing)}")
    extras = set(value) - set(REQUIRED_FIELDS) - {"details"}
    if extras:
        raise ValueError(f"Dashboard contract has undocumented fields: {', '.join(sorted(extras))}")
    if set(value["domain"]) != {"id", "version"}:
        raise ValueError("domain must contain exactly id and version")
    if value["health"] not in HEALTH_VALUES:
        raise ValueError(f"Invalid dashboard health: {value['health']}")
    if not isinstance(value["requires_action"], bool) or not isinstance(value["recommendations"], list) or not isinstance(value["links"], list):
        raise ValueError("Invalid dashboard contract field types")
    if "details" in value and not isinstance(value["details"], dict):
        raise ValueError("details must be an object")


def load_contracts(directory: Path) -> list[Mapping[str, Any]]:
    contracts = []
    for path in sorted(Path(directory).glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        validate_contract(value)
        contracts.append(value)
    ids = [item["domain"]["id"] for item in contracts]
    if len(ids) != len(set(ids)):
        raise ValueError("Each dashboard domain may occur only once")
    return contracts
