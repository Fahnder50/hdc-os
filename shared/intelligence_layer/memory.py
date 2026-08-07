import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping


FEEDBACK_VALUES = frozenset({"ACCEPT", "REJECT", "DEFER"})
DECISION_FIELDS = ("recommendation", "owner_decision", "reason", "timestamp", "procurement_case")


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(value, temporary, indent=2, ensure_ascii=False)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path:
            temporary_path.unlink(missing_ok=True)


class DecisionMemory:
    def __init__(self, path: Path):
        self.path = Path(path)

    def all(self) -> list[Mapping[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []

    def record(self, decision: Mapping[str, Any]) -> None:
        if set(decision) != set(DECISION_FIELDS):
            raise ValueError("Decision memory accepts exactly recommendation, owner_decision, reason, timestamp and procurement_case")
        if decision["owner_decision"] not in FEEDBACK_VALUES:
            raise ValueError("Owner decision must be ACCEPT, REJECT or DEFER")
        values = self.all()
        if any(item["procurement_case"] == decision["procurement_case"] and item["timestamp"] == decision["timestamp"] for item in values):
            raise ValueError("This owner decision is already recorded")
        values.append(dict(decision))
        _atomic_json(self.path, values)

    def relevant(self, case_ids: set[str]) -> list[Mapping[str, Any]]:
        return [item for item in self.all() if item["procurement_case"] in case_ids]


class FeedbackMemory:
    def __init__(self, path: Path):
        self.path = Path(path)

    def all(self) -> list[Mapping[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []

    def record(self, procurement_case: str, feedback: str, timestamp: str) -> None:
        if feedback not in FEEDBACK_VALUES:
            raise ValueError("Feedback must be ACCEPT, REJECT or DEFER")
        values = self.all()
        if any(item["procurement_case"] == procurement_case and item["timestamp"] == timestamp for item in values):
            raise ValueError("Exactly one feedback entry is allowed per owner decision")
        values.append({"procurement_case": procurement_case, "feedback": feedback, "timestamp": timestamp})
        _atomic_json(self.path, values)
