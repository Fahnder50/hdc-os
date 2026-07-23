import json
import uuid

from .events import emit_evaluation_events


RULES = (
    "TOTAL_PRICE_WITHIN_TARGET",
    "TOTAL_PRICE_WITHIN_BUDGET",
    "OVER_ABSOLUTE_BUDGET",
    "PRODUCT_AVAILABLE",
    "DELIVERY_ELIGIBILITY",
    "RUNTIME_TARGET_DOCUMENTED",
    "LINE_INTERACTIVE_DOCUMENTED",
    "AUTOMATIC_VOLTAGE_REGULATION_DOCUMENTED",
    "USB_DATA_INTERFACE_DOCUMENTED",
    "LINUX_MONITORING_DOCUMENTED",
    "NUT_COMPATIBLE_DOCUMENTED",
    "BATTERY_BACKED_OUTPUTS_MINIMUM",
    "ROUTER_FIREWALL_DIMENSIONING_DOCUMENTED",
    "GERMANY_230V_DOCUMENTED",
    "NEW_WITH_WARRANTY_DOCUMENTED",
    "AUTOMATIC_FAILOVER_DOCUMENTED",
    "STANDALONE_OPERATION_DOCUMENTED",
    "CLOUD_FREE_OPERATION_DOCUMENTED",
    "MONITORING_CAPABILITY_CLASSIFIED",
)
LEGACY_RULES = (
    "TOTAL_PRICE_WITHIN_BUDGET",
    "PRODUCT_AVAILABLE",
    "RUNTIME_TARGET_DOCUMENTED",
    "AUTOMATIC_FAILOVER_DOCUMENTED",
    "STANDALONE_OPERATION_DOCUMENTED",
    "CLOUD_FREE_OPERATION_DOCUMENTED",
    "MONITORING_CAPABILITY_CLASSIFIED",
)


def _technical_value(product, key):
    try:
        technical = json.loads(product["technical_json"] or "{}")
    except (TypeError, json.JSONDecodeError):
        return None
    value = technical.get(key)
    return None if value in (None, "unknown", "UNKNOWN") else value


def _documented_boolean(value):
    return value is True or str(value).lower() in {"true", "required", "supported", "pass", "local", "preferred"}


def _technical_rule(rule_id):
    return {
        "LINE_INTERACTIVE_DOCUMENTED": "line_interactive",
        "AUTOMATIC_VOLTAGE_REGULATION_DOCUMENTED": "automatic_voltage_regulation",
        "USB_DATA_INTERFACE_DOCUMENTED": "usb_data_interface",
        "LINUX_MONITORING_DOCUMENTED": "linux_monitoring",
        "NUT_COMPATIBLE_DOCUMENTED": "nut_compatible",
        "ROUTER_FIREWALL_DIMENSIONING_DOCUMENTED": "router_firewall_dimensioning",
        "GERMANY_230V_DOCUMENTED": "germany_230v",
        "NEW_WITH_WARRANTY_DOCUMENTED": "new_with_warranty",
        "AUTOMATIC_FAILOVER_DOCUMENTED": "automatic_failover",
        "STANDALONE_OPERATION_DOCUMENTED": "standalone_operation",
        "CLOUD_FREE_OPERATION_DOCUMENTED": "cloud_free_operation",
        "MONITORING_CAPABILITY_CLASSIFIED": "monitoring_capability",
    }.get(rule_id)


def _evaluate_rule(rule_id, offer, product, requirements, target_runtime):
    target_price = requirements.get("budget_target_price")
    maximum_price = requirements.get("budget_maximum_total_price")
    absolute_price = requirements.get("budget_absolute_maximum_total_price")
    if rule_id == "TOTAL_PRICE_WITHIN_TARGET":
        if offer["total_price_cents"] is None or target_price is None:
            return "UNKNOWN", "Total price or target price is missing."
        return ("PASS", "Total price is at or below the preferred target price.") if offer["total_price_cents"] <= int(float(target_price) * 100) else ("REVIEW", "Total price exceeds the preferred target price.")
    if rule_id == "TOTAL_PRICE_WITHIN_BUDGET":
        if offer["total_price_cents"] is None or maximum_price is None:
            return "UNKNOWN", "Total price or regular maximum budget is missing."
        return ("PASS", "Total price is within the regular maximum budget.") if offer["total_price_cents"] <= int(float(maximum_price) * 100) else ("FAIL", "Total price exceeds the regular maximum budget.")
    if rule_id == "OVER_ABSOLUTE_BUDGET":
        if offer["total_price_cents"] is None or absolute_price is None:
            return "UNKNOWN", "Total price or absolute budget is missing."
        return ("PASS", "Total price is within the absolute budget.") if offer["total_price_cents"] <= int(float(absolute_price) * 100) else ("FAIL", "Total price exceeds the absolute budget.")
    if rule_id == "PRODUCT_AVAILABLE":
        availability = (offer["availability"] or "").lower()
        return ("PASS", "Offer is available.") if availability in {"available", "in_stock", "instock", "in stock"} else ("FAIL", "Offer is not available.") if availability else ("UNKNOWN", "Availability is missing.")
    if rule_id == "DELIVERY_ELIGIBILITY":
        eligibility = offer["delivery_eligibility"] or "unknown"
        return ("PASS", "Delivery or pickup is eligible by the case deadline.") if eligibility == "true" else ("FAIL", "Delivery is later than the case deadline.") if eligibility == "false" else ("UNKNOWN", "Delivery cannot be verified by the case deadline.")
    if rule_id == "RUNTIME_TARGET_DOCUMENTED":
        runtime = _technical_value(product, "runtime_hours")
        if runtime is None or target_runtime is None:
            return "UNKNOWN", "Runtime target or documented runtime is missing."
        return ("PASS", "Documented runtime meets target.") if float(runtime) >= float(target_runtime) else ("FAIL", "Documented runtime is below target.")
    if rule_id == "BATTERY_BACKED_OUTPUTS_MINIMUM":
        value = _technical_value(product, "battery_backed_outputs")
        required = requirements.get("battery_backed_outputs_minimum")
        if value is None or required is None:
            return "UNKNOWN", "Battery-backed output count is missing."
        return ("PASS", "Minimum battery-backed outputs are documented.") if int(value) >= int(required) else ("FAIL", "Too few battery-backed outputs are documented.")
    key = _technical_rule(rule_id)
    if key:
        value = _technical_value(product, key)
        if value is None:
            return "UNKNOWN", "Technical information is missing."
        return ("PASS", "Technical capability is documented.") if _documented_boolean(value) else ("FAIL", "Technical capability is documented as unsupported.")
    return "NOT_APPLICABLE", "Rule is not applicable."


def evaluate_case(connection, case_id, watch_run_db_id=None):
    case = connection.execute("SELECT * FROM procurement_cases WHERE case_id = ?", (case_id,)).fetchone()
    if case is None:
        raise ValueError(f"Unknown case: {case_id}")
    requirement_rows = connection.execute("SELECT requirement_id, value_json FROM requirements WHERE case_id = ?", (case["id"],)).fetchall()
    requirements = {row["requirement_id"]: json.loads(row["value_json"]) for row in requirement_rows}
    target_runtime = requirements.get("target_runtime_hours")
    offers = connection.execute(
        """
        SELECT offers.*, products.id AS product_db_id, products.technical_json,
            products.model_number, products.evidence_status, products.outlet_type
        FROM offers
        JOIN products ON products.id = offers.product_id
        JOIN case_products ON case_products.product_id = products.id
        WHERE case_products.case_id = ? AND offers.status = 'active'
        """,
        (case["id"],),
    ).fetchall()
    rule_set = RULES if any(row["source_type"] in {"geizhals", "json-ld-live"} for row in offers) else LEGACY_RULES
    all_results = []
    for offer in offers:
        offer_results = []
        for rule_id in rule_set:
            result, reason = _evaluate_rule(rule_id, offer, offer, requirements, target_runtime)
            evaluation_id = f"EVAL-{uuid.uuid4().hex[:12]}"
            connection.execute(
                """
                INSERT INTO evaluations(evaluation_id, case_id, offer_id, watch_run_id, rule_id, result, reason, evaluated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (evaluation_id, case["id"], offer["id"], watch_run_db_id, rule_id, result, reason),
            )
            offer_results.append({"rule_id": rule_id, "result": result, "reason": reason})
        emit_evaluation_events(connection, case["id"], offer["id"], offer_results)
        all_results.append({"offer_id": offer["offer_id"], "evaluations": offer_results})
    return all_results
