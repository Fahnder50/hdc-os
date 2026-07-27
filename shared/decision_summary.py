from dataclasses import dataclass
from html import escape


@dataclass(frozen=True)
class DecisionDimension:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class DecisionSummary:
    dimensions: tuple[DecisionDimension, ...]
    engine_status: str | None
    recommendation: str
    reasons: tuple[str, ...]
    change_conditions: tuple[str, ...]


def create_decision_summary(dimensions, recommendation, reasons, change_conditions, engine_status=None):
    normalized = tuple(
        dimension if isinstance(dimension, DecisionDimension) else DecisionDimension(**dimension)
        for dimension in dimensions
    )
    names = [dimension.name for dimension in normalized]
    if not normalized or len(names) != len(set(names)):
        raise ValueError("Decision summary requires an ordered collection of uniquely named dimensions")
    return DecisionSummary(normalized, engine_status, recommendation, tuple(reasons), tuple(change_conditions))


def render_decision_summary(summary):
    rows = "".join(
        "<tr><th>{}</th><td><strong>{}</strong><br>{}</td></tr>".format(
            escape(dimension.name), escape(dimension.status), escape(dimension.detail)
        )
        for dimension in summary.dimensions
    )
    reasons = "".join(f"<li>{escape(reason)}</li>" for reason in summary.reasons)
    conditions = "".join(f"<li>{escape(condition)}</li>" for condition in summary.change_conditions)
    return (
        '<section class="decision-summary"><h2>Decision Summary</h2>'
        f"<table><tbody>{rows}</tbody></table>"
        f"<p><strong>Engine-Status:</strong> {escape(summary.engine_status or 'nicht angegeben')}</p>"
        f"<h3>Handlungsempfehlung: {escape(summary.recommendation)}</h3>"
        f"<h3>Warum?</h3><ul>{reasons or '<li>Keine unmittelbaren Entscheidungsgründe dokumentiert.</li>'}</ul>"
        f"<h3>Die Empfehlung würde sich ändern wenn …</h3><ul>{conditions or '<li>Keine Änderungsbedingungen dokumentiert.</li>'}</ul>"
        "</section>"
    )
