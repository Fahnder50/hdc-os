import json
from typing import Any, Mapping, Sequence

from .contracts import KnowledgeItem


class ContextBuilder:
    """Deterministically constructs the smallest serializable analysis context."""

    def build(self, request: Mapping[str, Any], knowledge: Sequence[KnowledgeItem], decisions: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        return {
            "request": json.loads(json.dumps(request, default=str)),
            "knowledge": [{"source": item.source.value, "reference": item.reference, "content": item.content} for item in knowledge],
            "decision_memory": list(decisions),
        }


class PromptBuilder:
    """Contains only role, task, context integration and schema integration."""

    def build(self, role: str, task: str, context: Mapping[str, Any], schema: Mapping[str, Any]) -> str:
        return "\n\n".join((
            f"ROLE:\n{role}",
            f"ANALYSIS TASK:\n{task}",
            "CONTEXT:\n" + json.dumps(context, ensure_ascii=False, default=str),
            "OUTPUT JSON SCHEMA:\n" + json.dumps(schema, ensure_ascii=False),
        ))
