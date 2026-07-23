import uuid


EVENT_SEVERITIES = ("INFO", "NOTICE", "WARNING", "ACTION_REQUIRED", "ERROR")
EVENT_TYPES = (
    "BUY_CANDIDATE",
    "PRICE_DROP",
    "PRICE_INCREASE",
    "RULE_FAILED",
    "CASE_COMPLETED",
    "CASE_CHANGED",
    "BUDGET_EXCEEDED",
    "PRODUCT_UNAVAILABLE",
    "PRODUCT_AVAILABLE",
    "PRODUCT_AVAILABLE_AGAIN",
    "REQUIREMENT_UNKNOWN",
    "OFFER_CHANGED",
    "PRICE_TARGET_REACHED",
    "SOURCE_FAILED",
    "DELIVERY_UNKNOWN",
    "DELIVERY_TOO_LATE",
    "OVER_BUDGET",
    "OUT_OF_STOCK",
)
EVENT_DEFAULT_SEVERITY = {
    "BUY_CANDIDATE": "ACTION_REQUIRED",
    "PRICE_DROP": "NOTICE",
    "PRICE_INCREASE": "NOTICE",
    "RULE_FAILED": "WARNING",
    "CASE_COMPLETED": "INFO",
    "CASE_CHANGED": "INFO",
    "BUDGET_EXCEEDED": "WARNING",
    "PRODUCT_UNAVAILABLE": "WARNING",
    "PRODUCT_AVAILABLE": "INFO",
    "PRODUCT_AVAILABLE_AGAIN": "INFO",
    "REQUIREMENT_UNKNOWN": "NOTICE",
    "OFFER_CHANGED": "NOTICE",
    "PRICE_TARGET_REACHED": "ACTION_REQUIRED",
    "SOURCE_FAILED": "ERROR",
    "DELIVERY_UNKNOWN": "WARNING",
    "DELIVERY_TOO_LATE": "WARNING",
    "OVER_BUDGET": "WARNING",
    "OUT_OF_STOCK": "WARNING",
}


def classify_event(event_type, severity=None):
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unknown event type: {event_type}")
    selected = severity or EVENT_DEFAULT_SEVERITY[event_type]
    if selected not in EVENT_SEVERITIES:
        raise ValueError(f"Unknown event severity: {selected}")
    return selected


def emit_event(connection, case_db_id, event_type, deduplication_key, message, severity=None):
    event_id = f"EV-{uuid.uuid4().hex[:12]}"
    selected_severity = classify_event(event_type, severity)
    connection.execute(
        """
        INSERT OR IGNORE INTO events(event_id, case_id, event_type, severity, deduplication_key, status, message, created_at)
        VALUES (?, ?, ?, ?, ?, 'open', ?, datetime('now'))
        """,
        (event_id, case_db_id, event_type, selected_severity, deduplication_key, message),
    )


def emit_evaluation_events(connection, case_db_id, offer_id, evaluations):
    for evaluation in evaluations:
        result = evaluation["result"]
        rule_id = evaluation["rule_id"]
        if result in {"UNKNOWN", "REVIEW"} and rule_id == "DELIVERY_ELIGIBILITY":
            emit_event(connection, case_db_id, "DELIVERY_UNKNOWN", f"{case_db_id}:delivery-unknown:{offer_id}", "Offer delivery cannot be verified against the deadline.")
        elif result == "FAIL" and rule_id == "DELIVERY_ELIGIBILITY":
            emit_event(connection, case_db_id, "DELIVERY_TOO_LATE", f"{case_db_id}:delivery-late:{offer_id}", "Offer cannot meet the procurement deadline.")
        elif result == "FAIL" and rule_id in {"TOTAL_PRICE_WITHIN_BUDGET", "OVER_ABSOLUTE_BUDGET", "WITHIN_MAXIMUM_BUDGET", "OVER_MAXIMUM_BUDGET"}:
            event_type = "OVER_BUDGET" if rule_id in {"OVER_ABSOLUTE_BUDGET", "OVER_MAXIMUM_BUDGET"} else "BUDGET_EXCEEDED"
            emit_event(connection, case_db_id, event_type, f"{case_db_id}:budget:{offer_id}:{rule_id}", "Offer exceeds the applicable case budget.")
        elif result == "FAIL" and rule_id == "PRODUCT_AVAILABLE":
            emit_event(connection, case_db_id, "PRODUCT_UNAVAILABLE", f"{case_db_id}:unavailable:{offer_id}", "Offer is not available.")
        elif result in {"UNKNOWN", "REVIEW"}:
            emit_event(connection, case_db_id, "REQUIREMENT_UNKNOWN", f"{case_db_id}:unknown:{rule_id}", f"Requirement {rule_id} is unknown or requires review for one or more offers.")
