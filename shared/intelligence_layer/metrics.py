from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .contracts import IntelligenceHealth
from .memory import _atomic_json


class IntelligenceMetrics:
    def __init__(self, path: Path):
        self.path = Path(path)

    def read(self) -> dict[str, Any]:
        if self.path.exists():
            import json
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {"ai_calls": 0, "successful_model_responses": 0, "schema_errors": 0, "fallback_uses": 0, "total_response_seconds": 0.0, "last_successful_ai_response": None}

    def record(self, duration_seconds: float, successful: bool, schema_error: bool, fallback_used: bool) -> Mapping[str, Any]:
        value = self.read()
        value["ai_calls"] += 1
        value["successful_model_responses"] += int(successful)
        value["schema_errors"] += int(schema_error)
        value["fallback_uses"] += int(fallback_used)
        value["total_response_seconds"] = round(value["total_response_seconds"] + duration_seconds, 6)
        if successful:
            value["last_successful_ai_response"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        calls = value["ai_calls"]
        value["fallback_rate"] = round(value["fallback_uses"] / calls, 6)
        value["average_response_seconds"] = round(value["total_response_seconds"] / calls, 6)
        value["health"] = self.health(value).value
        _atomic_json(self.path, value)
        return value

    @staticmethod
    def health(value: Mapping[str, Any]) -> IntelligenceHealth:
        if value.get("successful_model_responses", 0) == 0 and value.get("ai_calls", 0):
            return IntelligenceHealth.DEGRADED
        if value.get("fallback_uses", 0) or value.get("schema_errors", 0):
            return IntelligenceHealth.WARNING
        return IntelligenceHealth.HEALTHY
