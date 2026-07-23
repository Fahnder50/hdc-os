from datetime import datetime, timezone
from html import escape
from pathlib import Path


TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "templates" / "procurement-report.html"


def _list(items, empty="Keine Einträge."):
    if not items:
        return f"<p>{escape(empty)}</p>"
    return "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in items) + "</ul>"


def render_report(data, generated_at=None):
    generated_at = generated_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    status = data["status"]
    offers = data["offers"]
    history = data["history"]
    evaluations = data["evaluations"]
    events = data["events"]
    watch_runs = data["watch_runs"]
    offer_rows = "".join(
        "<tr>" + "".join(
            f"<td>{escape(str(value))}</td>" for value in (
                row.get("offer_id"), row.get("product_name"), row.get("vendor_name"),
                row.get("total_price"), row.get("currency"), row.get("availability"), row.get("observed_at"),
            )
        ) + "</tr>" for row in offers
    ) or '<tr><td colspan="7">Keine Angebote.</td></tr>'
    evaluation_rows = "".join(
        f"<tr><td>{escape(str(row['rule_id']))}</td><td>{escape(str(row['result']))}</td><td>{escape(str(row['reason'] or ''))}</td></tr>" for row in evaluations
    ) or '<tr><td colspan="3">Keine Bewertungen.</td></tr>'
    event_rows = "".join(
        f"<tr><td>{escape(str(row['event_type']))}</td><td>{escape(str(row['severity']))}</td><td>{escape(str(row['status']))}</td><td>{escape(str(row['message'] or ''))}</td></tr>" for row in events
    ) or '<tr><td colspan="4">Keine Events.</td></tr>'
    history_rows = "".join(
        f"<tr><td>{escape(str(row['observed_at']))}</td><td>{escape(str(row['offer_id']))}</td><td>{escape(str(row['total_price']))} {escape(str(row['currency']))}</td><td>{escape(str(row['availability']))}</td></tr>" for row in history
    ) or '<tr><td colspan="4">Keine Preisbeobachtungen.</td></tr>'
    values = {
        "{{CASE_ID}}": escape(str(status["case_id"])),
        "{{TITLE}}": escape(str(status["title"])),
        "{{GENERATED_AT}}": escape(generated_at),
        "{{RECOMMENDATION_STATUS}}": escape(str(status["recommendation_status"])),
        "{{PRIORITY}}": escape(str(status["priority"])),
        "{{BUDGET}}": escape(str(status["budget"])),
        "{{PRODUCT_CANDIDATES}}": str(status["product_candidates"]),
        "{{ACTIVE_OFFERS}}": str(status["active_offers"]),
        "{{CHEAPEST_AVAILABLE}}": escape(str(status["cheapest_available_offer"])),
        "{{CHEAPEST_BUDGET_COMPLIANT}}": escape(str(status["cheapest_budget_compliant_offer"])),
        "{{REQUIREMENTS}}": _list(status["open_required_requirements"], "Keine offenen Pflichtanforderungen."),
        "{{WARNINGS}}": _list(status["warnings"], "Keine Warnungen."),
        "{{OFFER_ROWS}}": offer_rows,
        "{{HISTORY_ROWS}}": history_rows,
        "{{EVALUATION_ROWS}}": evaluation_rows,
        "{{EVENT_ROWS}}": event_rows,
        "{{WATCH_RUNS}}": _list([f"{row['watch_run_id']}: {row['status']} ({row['started_at']})" for row in watch_runs], "Keine Watch-Läufe."),
    }
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    for token, value in values.items():
        template = template.replace(token, value)
    return template


def write_case_report(config, data):
    config.reports_path.mkdir(parents=True, exist_ok=True)
    destination = config.reports_path / f"{data['status']['case_id']}.html"
    destination.write_text(render_report(data), encoding="utf-8")
    return destination
