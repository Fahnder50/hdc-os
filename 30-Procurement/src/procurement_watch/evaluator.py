import json
import uuid

from .events import emit_evaluation_events


RULES = (
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
    return technical.get(key)


def _documented_boolean(value):
    return value is True or str(value).lower() in {"true", "required", "supported", "pass", "local", "preferred"}


def _evaluate_rule(rule_id, offer, product, budget_cents, target_runtime):
    if rule_id == "TOTAL_PRICE_WITHIN_BUDGET":
        if offer["total_price_cents"] is None or budget_cents is None:
            return "UNKNOWN", "Total price or budget is missing."
        return ("PASS", "Total price is within budget.") if offer["total_price_cents"] <= budget_cents else ("FAIL", "Total price exceeds budget.")
    if rule_id == "PRODUCT_AVAILABLE":
        availability = (offer["availability"] or "").lower()
        return ("PASS", "Offer is available.") if availability in {"available", "in_stock", "instock", "in stock"} else ("FAIL", "Offer is not available.") if availability else ("UNKNOWN", "Availability is missing.")
    if rule_id == "RUNTIME_TARGET_DOCUMENTED":
        runtime = _technical_value(product, "runtime_hours")
        if runtime is None or target_runtime is None:
            return "UNKNOWN", "Runtime target or documented runtime is missing."
        return ("PASS", "Documented runtime meets target.") if float(runtime) >= float(target_runtime) else ("FAIL", "Documented runtime is below target.")
    technical_keys = {
        "AUTOMATIC_FAILOVER_DOCUMENTED": "automatic_failover",
        "STANDALONE_OPERATION_DOCUMENTED": "standalone_operation",
        "CLOUD_FREE_OPERATION_DOCUMENTED": "cloud_free_operation",
        "MONITORING_CAPABILITY_CLASSIFIED": "monitoring_capability",
    }
    if rule_id in technical_keys:
        value = _technical_value(product, technical_keys[rule_id])
        if value is None:
            return "UNKNOWN", "Technical information is missing."
        return ("PASS", "Technical capability is documented.") if _documented_boolean(value) else ("FAIL", "Technical capability is documented as unsupported.")
    return "NOT_APPLICABLE", "Rule is not applicable."


def evaluate_case(connection, case_id, watch_run_db_id=None):
    case = connection.execute("SELECT * FROM procurement_cases WHERE case_id = ?", (case_id,)).fetchone()
    if case is None:
        raise ValueError(f"Unknown case: {case_id}")
    budget = connection.execute("SELECT value_json FROM requirements WHERE case_id = ? AND requirement_id = 'budget_maximum_total_price'", (case["id"],)).fetchone()
    budget_cents = int(json.loads(budget[0]) * 100) if budget else None
    target = connection.execute("SELECT value_json FROM requirements WHERE case_id = ? AND requirement_id = 'target_runtime_hours'", (case["id"],)).fetchone()
    target_runtime = json.loads(target[0]) if target else None
    offers = connection.execute(
        """
        SELECT offers.*, products.id AS product_db_id, products.technical_json
        FROM offers
        JOIN products ON products.id = offers.product_id
        JOIN case_products ON case_products.product_id = products.id
        WHERE case_products.case_id = ? AND offers.status = 'active'
        """,
        (case["id"],),
    ).fetchall()
    all_results = []
    for offer in offers:
        offer_results = []
        for rule_id in RULES:
            result, reason = _evaluate_rule(rule_id, offer, offer, budget_cents, target_runtime)
            evaluation_id = f"EVAL-{uuid.uuid4().hex[:12]}"
            connection.execute(
                """
                INSERT INTO evaluations(evaluation_id, case_id, offer_id, watch_run_id, rule_id, result, reason, evaluated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (evaluation_id, case["id"], offer["id"], watch_run_db_id, rule_id, result, reason),
            )
            evaluation = {"rule_id": rule_id, "result": result, "reason": reason}
            offer_results.append(evaluation)
        emit_evaluation_events(connection, case["id"], offer["id"], offer_results)
        all_results.append({"offer_id": offer["offer_id"], "evaluations": offer_results})
    return all_results
