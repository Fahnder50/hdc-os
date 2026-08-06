from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

import yaml


DYNAMIC_FIELDS = {"configuration_hash", "installation_state", "last_verification"}
REQUIRED_FIELDS = {"scheduler_id", "name", "version", "owner", "trigger", "schedule", "runtime", "configuration_hash", "installation_state", "last_verification"}


def configuration_hash(definition: Mapping[str, Any]) -> str:
    desired = {key: value for key, value in definition.items() if key not in DYNAMIC_FIELDS}
    canonical = json.dumps(desired, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def load_registry(path: Path) -> list[Mapping[str, Any]]:
    document = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    entries = document.get("schedulers", [])
    ids = []
    for entry in entries:
        missing = REQUIRED_FIELDS - set(entry)
        if missing:
            raise ValueError(f"Scheduler registry entry is missing: {', '.join(sorted(missing))}")
        if entry["scheduler_id"] in ids:
            raise ValueError(f"Duplicate scheduler_id: {entry['scheduler_id']}")
        ids.append(entry["scheduler_id"])
        expected = configuration_hash(entry)
        if entry["configuration_hash"] != expected:
            raise ValueError(f"Registry hash mismatch for {entry['scheduler_id']}: expected {expected}")
    return entries


def persist_dynamic_state(path: Path, scheduler_id: str, status: Mapping[str, Any]) -> None:
    """Atomically persist only the runtime-owned fields of one registry entry."""
    registry_path = Path(path)
    source = registry_path.read_text(encoding="utf-8")
    entries = load_registry(registry_path)
    matches = [entry for entry in entries if entry.get("scheduler_id") == scheduler_id]
    if len(matches) != 1:
        raise ValueError(f"Registry must contain exactly one scheduler_id: {scheduler_id}")

    entry = matches[0]
    replacements = {
        "configuration_hash": configuration_hash(entry),
        "installation_state": status["installation_state"],
        "last_verification": status["last_verification"],
    }
    candidate = _replace_dynamic_scalars(source, scheduler_id, replacements)

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", prefix=f".{registry_path.name}.",
            suffix=".tmp", dir=registry_path.parent, delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(candidate)
            temporary.flush()
            os.fsync(temporary.fileno())
        # Validate the complete candidate, including its recomputed hash, before replacement.
        load_registry(temporary_path)
        os.replace(temporary_path, registry_path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _replace_dynamic_scalars(source: str, scheduler_id: str, replacements: Mapping[str, Any]) -> str:
    root = yaml.compose(source)
    scheduler_sequence = next(
        value for key, value in root.value if key.value == "schedulers"
    )
    target = next(
        item for item in scheduler_sequence.value
        if any(key.value == "scheduler_id" and value.value == scheduler_id for key, value in item.value)
    )
    locations = {
        key.value: (value.start_mark.index, value.end_mark.index)
        for key, value in target.value if key.value in DYNAMIC_FIELDS
    }
    if set(locations) != DYNAMIC_FIELDS:
        raise ValueError(f"Registry dynamic fields are incomplete for {scheduler_id}")
    candidate = source
    for field, (start, end) in sorted(locations.items(), key=lambda item: item[1][0], reverse=True):
        encoded = "null" if replacements[field] is None else json.dumps(str(replacements[field]), ensure_ascii=False)
        candidate = candidate[:start] + encoded + candidate[end:]
    return candidate
