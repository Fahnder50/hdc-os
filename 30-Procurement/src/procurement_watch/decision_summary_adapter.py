from datetime import date

from shared.decision_summary import DecisionDimension, create_decision_summary, render_decision_summary


TECHNICAL_RULES = {
    "AUTOMATIC_FAILOVER_DOCUMENTED": "Automatische Umschaltung ist noch nicht eindeutig bestätigt.",
    "AUTOMATIC_VOLTAGE_REGULATION_DOCUMENTED": "Automatische Spannungsregelung ist noch nicht eindeutig bestätigt.",
    "BATTERY_BACKED_OUTPUTS_MINIMUM": "Die erforderliche Anzahl batteriegestützter Ausgänge ist noch nicht eindeutig bestätigt.",
    "CLOUD_FREE_OPERATION_DOCUMENTED": "Cloud-freier Betrieb ist noch nicht eindeutig bestätigt.",
    "GERMANY_230V_DOCUMENTED": "Die Eignung für das deutsche 230-Volt-Netz ist noch nicht eindeutig bestätigt.",
    "LINUX_MONITORING_DOCUMENTED": "Linux-Monitoring ist noch nicht eindeutig bestätigt.",
    "LINE_INTERACTIVE_DOCUMENTED": "Die Line-Interactive-Technik ist noch nicht eindeutig bestätigt.",
    "MONITORING_CAPABILITY_CLASSIFIED": "Die Monitoring-Fähigkeit ist noch nicht eindeutig bestätigt.",
    "NEW_WITH_WARRANTY_DOCUMENTED": "Neuzustand und Garantie sind noch nicht eindeutig bestätigt.",
    "NUT_COMPATIBLE_DOCUMENTED": "Linux-NUT-Kompatibilität ist noch nicht eindeutig bestätigt.",
    "ROUTER_FIREWALL_DIMENSIONING_DOCUMENTED": "Die Dimensionierung für Router und Firewall ist noch nicht eindeutig bestätigt.",
    "RUNTIME_TARGET_DOCUMENTED": "Die Ziel-Laufzeit ist noch nicht eindeutig bestätigt.",
    "STANDALONE_OPERATION_DOCUMENTED": "Der eigenständige Betrieb ist noch nicht eindeutig bestätigt.",
    "USB_DATA_INTERFACE_DOCUMENTED": "Die USB-Datenschnittstelle ist noch nicht eindeutig bestätigt.",
}

BUDGET_RULES = {
    "OVER_ABSOLUTE_BUDGET",
    "OVER_MAXIMUM_BUDGET",
    "TOTAL_PRICE_WITHIN_BUDGET",
    "TOTAL_PRICE_WITHIN_TARGET",
    "WITHIN_MAXIMUM_BUDGET",
    "WITHIN_TARGET_BUDGET",
}

RISK_RULES = {
    "RUNTIME_TARGET_DOCUMENTED": "Die gewünschte Ziel-Laufzeit ist noch nicht eindeutig bestätigt.",
}


def _facts(warnings, purchase_conditions=()):
    technical = []
    risks = []
    for warning in warnings:
        rule_id = warning.split(":", 1)[0]
        if rule_id in BUDGET_RULES:
            continue
        fact = TECHNICAL_RULES.get(rule_id)
        result = warning.split(":", 1)[1].strip() if ":" in warning else ""
        if fact:
            if result == "NOT_VERIFIED":
                fact = f"{fact} [NOT_VERIFIED]"
            if fact not in technical:
                technical.append(fact)
            risk_fact = RISK_RULES.get(rule_id)
            if risk_fact and risk_fact not in risks:
                risks.append(risk_fact)
        else:
            fallback = {
                "DELIVERY_ELIGIBILITY": "Die Lieferbarkeit ist nicht vollständig bestätigt.",
                "PRODUCT_AVAILABLE": "Die Verfügbarkeit ist nicht vollständig bestätigt.",
                "TOTAL_PRICE_WITHIN_TARGET": "Der Preis liegt nicht sicher innerhalb des Zielbudgets.",
                "TOTAL_PRICE_WITHIN_BUDGET": "Der Endpreis liegt nicht sicher innerhalb der zulässigen Obergrenze.",
            }.get(rule_id, f"Offener Bewertungsaspekt: {rule_id}.")
            if fallback not in risks:
                risks.append(fallback)
    if any("Versandkosten" in condition or "Endpreis" in condition for condition in purchase_conditions):
        risks.append("Versandkosten und Endpreis sind vor dem Checkout noch nicht belastbar bestätigt.")
    risks = list(dict.fromkeys(risks))
    return technical, risks


def _format_date(value):
    if not value:
        return "nicht beobachtet"
    return date.fromisoformat(str(value)).strftime("%d.%m.%Y")


def build_procurement_decision_summary(status, data=None, money_formatter=None):
    money = money_formatter or (lambda value: f"{value:.2f} €" if value is not None else "unbekannt")
    offers = status.get("active_offers", 0)
    ranking = status.get("ranking", [])
    technical_facts, risk_facts = _facts(status.get("warnings", []), status.get("purchase_conditions", []))
    nonblocking_facts = [f"{item['title']}: {item['description']}" for item in status.get("requirement_facts", [])]
    target_date = status.get("target_date")
    earliest_delivery = status.get("earliest_observed_delivery") or next(
        (item.get("delivery_date_latest") for item in ranking if item.get("delivery_date_latest")), None
    )
    buffer_days = None
    if target_date and earliest_delivery:
        buffer_days = (date.fromisoformat(str(target_date)) - date.fromisoformat(str(earliest_delivery))).days
    budget_status = status.get("budget_status", "NO_OFFER")
    budget_labels = {
        "WITHIN_TARGET_BUDGET": "Innerhalb Zielbudget",
        "WITHIN_MAXIMUM_BUDGET": "Über Zielbudget, aber zulässig",
        "OVER_MAXIMUM_BUDGET": "Budget überschritten",
        "NO_OFFER": "Keine Preisbasis",
    }
    recommendation = status["recommendation_status"]
    action = {"BUY_CANDIDATE": "JETZT KAUFEN", "CONDITIONAL_BUY": "NOCH WARTEN"}.get(recommendation, "NICHT KAUFEN")
    market_detail = f"{offers} auswertbare Angebote" if offers else "Keine auswertbaren Angebote"
    reasons = []
    reasons.append(f"Budget: {budget_labels.get(budget_status, budget_status)}.")
    if technical_facts:
        reasons.append(f"Kaufkritische Technik bleibt offen: {len(technical_facts)} Sachverhalte.")
    if nonblocking_facts:
        reasons.append(f"Nicht blockierende offene oder vorgeschlagene Anforderungen: {len(nonblocking_facts)} Sachverhalte.")
    else:
        reasons.append("Es sind keine kaufkritischen technischen Sachverhalte offen.")
    if not target_date:
        time_status = "Zeitbewertung nicht möglich"
        time_detail = "Zieltermin nicht definiert · Puffer nicht berechenbar"
    elif buffer_days is not None and buffer_days >= 0:
        time_status = "Lieferung vor Zieltermin"
        time_detail = f"Zieltermin: {_format_date(target_date)} · früheste Lieferung: {_format_date(earliest_delivery)} · Puffer: {buffer_days} Tage"
    elif earliest_delivery:
        time_status = "Lieferung nach Zieltermin"
        time_detail = f"Zieltermin: {_format_date(target_date)} · früheste Lieferung: {_format_date(earliest_delivery)} · Puffer: {buffer_days} Tage"
    else:
        time_status = "Liefertermin offen"
        time_detail = f"Zieltermin: {_format_date(target_date)} · früheste Lieferung: nicht beobachtet · Puffer: nicht berechenbar"
    if not target_date:
        reasons.append("Zeit: Zeitbewertung nicht möglich; Zieltermin nicht definiert und Puffer nicht berechenbar.")
    elif buffer_days is not None:
        reasons.append(f"Zeit: Früheste Lieferung vor dem Zieltermin mit {buffer_days} Tagen Puffer.")
    else:
        reasons.append("Zeit: Ein belastbarer Liefertermin ist noch offen.")
    conditions = []
    if budget_status != "WITHIN_TARGET_BUDGET":
        conditions.append("Wenn der Endpreis innerhalb des Zielbudgets liegt, kann die Budgetbedingung entfallen.")
    if technical_facts:
        conditions.append("Wenn die offenen kaufkritischen technischen Sachverhalte belastbar bestätigt sind, kann die Technikbedingung entfallen.")
    if buffer_days is not None:
        conditions.append("Wenn der Lieferpuffer unter 2 Tage fällt oder der Zieltermin verfehlt wird, muss die Zeitbewertung neu geprüft werden.")
    else:
        conditions.append("Wenn ein belastbarer Liefertermin vor dem Zieltermin vorliegt, kann die Zeitbewertung abgeschlossen werden.")
    summary = create_decision_summary([
        DecisionDimension("Markt", "Angebote vorhanden" if offers else "Keine Angebote", market_detail),
        DecisionDimension("Budget", budget_labels.get(budget_status, budget_status), f"Bestes beobachtetes Angebot: {money(status.get('best_observed_price'))}"),
        DecisionDimension("Technik", f"{len(technical_facts) + len(nonblocking_facts)} offene Sachverhalte" if technical_facts or nonblocking_facts else "Keine offenen Sachverhalte", "; ".join(technical_facts + nonblocking_facts) or "Keine offenen technischen Punkte"),
        DecisionDimension("Zeit", time_status, time_detail),
        DecisionDimension("Risiko", f"{len(risk_facts)} offene Sachverhalte" if risk_facts else "Keine offenen Sachverhalte", "; ".join(risk_facts) or "Keine bekannten Risiken"),
    ], action, reasons, conditions, engine_status=recommendation)
    return render_decision_summary(summary)
