import json
from pathlib import Path
from typing import Any, Mapping

from shared.intelligence_providers import OllamaProvider


ANALYSIS_SCHEMA = {
    "type": "object",
    "required": ["summary", "important_changes", "critical_developments", "unchanged_cases", "risks", "open_points", "recommendations"],
    "properties": {
        "summary": {"type": "string"},
        "important_changes": {"type": "array"},
        "critical_developments": {"type": "array"},
        "unchanged_cases": {"type": "array"},
        "risks": {"type": "array"},
        "open_points": {"type": "array"},
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["case_id", "recommendation", "information_status", "reason"],
                "properties": {
                    "case_id": {"type": "string"},
                    "recommendation": {"enum": ["KEEP_WATCHING", "REQUEST_REVIEW", "BUY_CANDIDATE", "NO_ACTION"]},
                    "information_status": {"enum": ["INFORMATION", "RECOMMENDATION", "ACTION_REQUIRED"]},
                    "reason": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}

PROCUREMENT_INTELLIGENCE_SCHEMA = {
    "type": "object",
    "required": ["executive_summary", "procurement_recommendations"],
    "properties": {
        "executive_summary": {"type": "string"},
        "procurement_recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["case_id", "recommendation", "information_status", "reasoning"],
                "properties": {
                    "case_id": {"type": "string"},
                    "recommendation": {"enum": ["KEEP_WATCHING", "REQUEST_REVIEW", "BUY_CANDIDATE", "NO_ACTION"]},
                    "information_status": {"enum": ["INFORMATION", "RECOMMENDATION", "ACTION_REQUIRED"]},
                    "reasoning": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}


class SchemaValidationError(ValueError):
    pass


def validate_schema(value: Any, schema: Mapping[str, Any], schemas_directory: Path) -> None:
    """Validate the JSON-Schema subset used by the checked-in agent schemas."""
    expected = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "boolean": bool, "number": (int, float), "integer": int}
    if expected in types and not isinstance(value, types[expected]):
        raise SchemaValidationError(f"Expected {expected}, got {type(value).__name__}")
    if "const" in schema and value != schema["const"]:
        raise SchemaValidationError(f"Expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise SchemaValidationError(f"Value {value!r} is not allowed")
    if isinstance(value, dict):
        missing = [key for key in schema.get("required", []) if key not in value]
        if missing:
            raise SchemaValidationError(f"Missing required properties: {', '.join(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = set(value) - set(properties)
            if extras:
                raise SchemaValidationError(f"Unexpected properties: {', '.join(sorted(extras))}")
        for key, child in properties.items():
            if key in value:
                validate_schema(value[key], child, schemas_directory)
    if isinstance(value, list) and "items" in schema:
        item_schema = schema["items"]
        if "$ref" in item_schema:
            item_schema = json.loads((schemas_directory / item_schema["$ref"]).read_text(encoding="utf-8"))
        for item in value:
            validate_schema(item, item_schema, schemas_directory)


OllamaLocalAnalysisProvider = OllamaProvider


class DeterministicFallbackAnalysisProvider:
    """Explicit non-AI fallback used only when configured or when local AI fails."""

    provider_name = "deterministic-fallback"
    model = "rules-v1"

    def analyze(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        recommendations = []
        for case in context["cases"]:
            status = case["current_evaluation"]
            if case.get("error"):
                recommendation, information_status = "REQUEST_REVIEW", "ACTION_REQUIRED"
            elif status == "BUY_CANDIDATE":
                recommendation, information_status = "BUY_CANDIDATE", "RECOMMENDATION"
            elif status in {"READY_FOR_REVIEW", "BLOCKED"}:
                recommendation, information_status = "REQUEST_REVIEW", "ACTION_REQUIRED"
            elif status in {"WATCHING", "QUALIFYING"}:
                recommendation, information_status = "KEEP_WATCHING", "INFORMATION"
            else:
                recommendation, information_status = "NO_ACTION", "INFORMATION"
            recommendations.append({"case_id": case["case_id"], "recommendation": recommendation, "information_status": information_status, "reason": f"Deterministic fallback derived from {status}."})
        changed = [item["case_id"] for item in context["cases"] if item["changes"]]
        return {
            "summary": f"{len(context['cases'])} procurement cases analyzed by deterministic fallback; {len(changed)} changed.",
            "important_changes": changed,
            "critical_developments": [item["case_id"] for item in context["cases"] if item["current_evaluation"] in {"BUY_CANDIDATE", "READY_FOR_REVIEW", "BLOCKED"}],
            "unchanged_cases": [item["case_id"] for item in context["cases"] if not item["changes"]],
            "risks": list(context["case_errors"]),
            "open_points": [item["case_id"] for item in context["cases"] if item["current_evaluation"] in {"QUALIFYING", "BLOCKED"}],
            "recommendations": recommendations,
        }


# Compatibility alias makes the former provider's fallback role explicit.
LocalRuleAnalysisProvider = DeterministicFallbackAnalysisProvider
