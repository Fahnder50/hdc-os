from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path


TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "templates" / "procurement-report.html"


def _list(items, empty="Keine Einträge."):
    if not items:
        return f"<p>{escape(empty)}</p>"
    return "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in items) + "</ul>"


def _date(value, with_time=False):
    if not value:
        return "–"
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.strftime("%d.%m.%Y %H:%M") if with_time else parsed.strftime("%d.%m.")
    except ValueError:
        return str(value)


def _money(value):
    return f"{float(value):.2f} €" if value is not None else "unbekannt"


def _next_date(value):
    if not value:
        return "–"
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return (parsed.replace(hour=0, minute=0) + timedelta(days=1)).strftime("%d.%m.")
    except ValueError:
        return "–"


def _operator_reason(status):
    if status["recommendation_status"] == "BUY_CANDIDATE":
        return "Budget, Verfügbarkeit, Lieferfrist und dokumentierte Anforderungen sind erfüllt."
    reasons = []
    if status.get("active_offers"):
        reasons.append("Versandkosten fehlen; Endpreis bitte im Checkout prüfen.")
    if any("RUNTIME" in warning for warning in status.get("warnings", [])):
        reasons.append("Die gewünschte Laufzeit ist noch nicht eindeutig bestätigt.")
    if any("LINUX" in warning or "NUT" in warning for warning in status.get("warnings", [])):
        reasons.append("Linux-Monitoring konnte noch nicht eindeutig bestätigt werden.")
    return " ".join(dict.fromkeys(reasons)) or "Weitere Beobachtungen stehen noch aus."


def _change_lines(changes):
    if changes.get("first_run"):
        return ["Erster Beobachtungslauf."]
    lines = []
    for change in changes.get("price_changes", []):
        lines.append(f"Preis {change['model']} bei {change['vendor']}: {_money(change['before'])} → {_money(change['after'])}")
    for change in changes.get("delivery_changes", []):
        lines.append(f"Lieferung {change['model']} bei {change['vendor']}: {_date(change['before'])} → {_date(change['after'])}")
    lines.extend(f"Neues Angebot: {offer_id}" for offer_id in changes.get("new_offers", []))
    if changes.get("new_events"):
        lines.append(f"Neue Events: {len(changes['new_events'])}")
    return lines or ["Keine Änderungen seit dem letzten Lauf."]


def _operator_events(events):
    labels = {
        "REQUIREMENT_UNKNOWN": "Eine technische Anforderung konnte noch nicht eindeutig bestätigt werden.",
        "DELIVERY_UNKNOWN": "Die Lieferung konnte noch nicht sicher gegen die Frist geprüft werden.",
        "SOURCE_FAILED": "Eine öffentliche Quelle war beim letzten Lauf nicht erreichbar.",
        "BUDGET_EXCEEDED": "Ein Angebot überschreitet das reguläre Budget.",
        "OVER_BUDGET": "Ein Angebot überschreitet das absolute Budget.",
    }
    return [labels.get(event.get("event_type"), "Eine Procurement-Änderung wurde erkannt.") for event in events]


def _offer_rows(offers):
    rows = []
    for index, offer in enumerate(offers[:3], start=1):
        medal = ("🥇", "🥈", "🥉")[index - 1]
        rows.append(
            "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in (
                f"{medal} {index}", offer.get("model_number") or offer.get("product_name"),
                offer.get("vendor_name"), _money(offer.get("price")), _date(offer.get("delivery_date_latest")),
                offer.get("evidence_status") or "unbekannt",
            )) + "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="6">Keine Angebote.</td></tr>'


def _price_rows(history):
    rows = []
    for item in history:
        rows.append("<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in (
            _date(item.get("observed_at"), True), item.get("model_number") or item.get("offer_id"), _money(item.get("price")),
        )) + "</tr>")
    return "".join(rows) or '<tr><td colspan="3">Noch keine Preisentwicklung vorhanden.</td></tr>'


def _journal_rows(entries):
    rows = []
    for entry in entries:
        changes = "; ".join(_change_lines(entry["changes"]))
        rows.append("<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in (
            _date(entry.get("observed_at"), True), entry.get("watch_run_id"), entry.get("recommendation_status"), changes,
        )) + "</tr>")
    return "".join(rows) or '<tr><td colspan="4">Noch kein Journal-Eintrag.</td></tr>'


def render_report(data, generated_at=None):
    generated_at = generated_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    status = data["status"]
    entries = data.get("journal", [])
    latest_entry = entries[0] if entries else None
    latest_run = status.get("last_watch_run") or {}
    ranked_offer_id = status.get("ranking", [None])[0].get("offer_id") if status.get("ranking") else None
    top_offer = next((offer for offer in data["offers"] if offer.get("offer_id") == ranked_offer_id), None)
    recommendation = status["recommendation_status"]
    if recommendation == "BUY_CANDIDATE":
        decision = "JETZT KAUFEN"
    elif recommendation == "CONDITIONAL_BUY":
        decision = "NOCH WARTEN"
    else:
        decision = "NOCH NICHT KAUFEN"
    changes = latest_entry["changes"] if latest_entry else {"first_run": True}
    values = {
        "{{CASE_ID}}": escape(str(status["case_id"])),
        "{{TITLE}}": escape(str(status["title"])),
        "{{GENERATED_AT}}": escape(_date(generated_at, True)),
        "{{RECOMMENDATION_STATUS}}": escape(decision),
        "{{RECOMMENDATION_REASON}}": escape(_operator_reason(status)),
        "{{STAGE}}": escape(str(recommendation)),
        "{{TOP_MODEL}}": escape(str(top_offer.get("model_number") or top_offer.get("product_name") if top_offer else "Noch offen")),
        "{{TOP_PRICE}}": escape(_money(top_offer.get("total_price") or top_offer.get("price") if top_offer else None)),
        "{{TOP_VENDOR}}": escape(str(top_offer.get("vendor_name") if top_offer else "Noch offen")),
        "{{TOP_DELIVERY}}": escape(_date(top_offer.get("delivery_date_latest") if top_offer else None)),
        "{{NEXT_OBSERVATION}}": escape(_next_date(latest_run.get("ended_at"))),
        "{{BUDGET_TARGET}}": escape(_money(status.get("budget_target"))),
        "{{BUDGET_BEST}}": escape(_money(status.get("best_observed_price"))),
        "{{BUDGET_STATUS}}": escape(str(status.get("budget_status", "NO_OFFER"))),
        "{{CHANGE_LINES}}": _list(_change_lines(changes)),
        "{{OFFER_ROWS}}": _offer_rows(data["offers"]),
        "{{PRICE_ROWS}}": _price_rows(data["history"]),
        "{{JOURNAL_ROWS}}": _journal_rows(entries),
        "{{TECHNICAL_DETAILS}}": _list([_operator_reason(status)] + status.get("purchase_conditions", []), "Keine offenen technischen Hinweise."),
        "{{EVENT_ROWS}}": _list(_operator_events(data["events"]), "Keine offenen Events."),
        "{{RAW_DATA}}": escape(str({"offers": len(data["offers"]), "observations": len(data["history"]), "evaluations": len(data["evaluations"])})),
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
