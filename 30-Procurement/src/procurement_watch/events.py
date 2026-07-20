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
        if result == "FAIL" and rule_id == "TOTAL_PRICE_WITHIN_BUDGET":
            emit_event(connection, case_db_id, "BUDGET_EXCEEDED", f"{case_db_id}:budget:{offer_id}", "Offer exceeds the case budget.")
        elif result == "FAIL" and rule_id == "PRODUCT_AVAILABLE":
            emit_event(connection, case_db_id, "PRODUCT_UNAVAILABLE", f"{case_db_id}:unavailable:{offer_id}", "Offer is not available.")
        elif result == "UNKNOWN":
            emit_event(connection, case_db_id, "REQUIREMENT_UNKNOWN", f"{case_db_id}:unknown:{offer_id}:{rule_id}", f"Requirement {rule_id} is unknown.")
