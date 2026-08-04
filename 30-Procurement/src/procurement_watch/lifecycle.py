"""Generic procurement lifecycle independent of post-purchase use."""


ACTIVE_CASE_STATUSES = (
    "WATCHING",
    "QUALIFYING",
    "READY_FOR_REVIEW",
    "BUY_CANDIDATE",
)
COMPLETION_STATUSES = ("PURCHASED", "CANCELLED")
ARCHIVE_VIEW = "CLOSED"
CASE_STATUSES = (*ACTIVE_CASE_STATUSES, *COMPLETION_STATUSES)

ALLOWED_TRANSITIONS = {
    "WATCHING": frozenset(("QUALIFYING", "CANCELLED")),
    "QUALIFYING": frozenset(("READY_FOR_REVIEW", "CANCELLED")),
    "READY_FOR_REVIEW": frozenset(("BUY_CANDIDATE", "CANCELLED")),
    "BUY_CANDIDATE": frozenset(("PURCHASED", "CANCELLED")),
    "PURCHASED": frozenset(),
    "CANCELLED": frozenset(),
}


def is_active(status):
    return str(status).upper() in ACTIVE_CASE_STATUSES


def is_completed(status):
    return str(status).upper() in COMPLETION_STATUSES


def validate_case_status(status):
    normalized = str(status).upper()
    if normalized not in CASE_STATUSES:
        raise ValueError(
            f"Invalid procurement lifecycle status {status!r}; expected one of: "
            f"{', '.join(CASE_STATUSES)}"
        )
    return normalized


def transition_case_status(current_status, target_status):
    """Validate and return the only permitted next persistent case status."""
    current = validate_case_status(current_status)
    target = validate_case_status(target_status)
    if current == target:
        return current
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"Invalid procurement lifecycle transition: {current} -> {target}")
    return target


def archive_view(status):
    """Return the runtime-only archive view for a completed persistent status."""
    normalized = validate_case_status(status)
    return ARCHIVE_VIEW if normalized in COMPLETION_STATUSES else normalized


__all__ = [
    "ACTIVE_CASE_STATUSES", "COMPLETION_STATUSES", "ARCHIVE_VIEW",
    "CASE_STATUSES", "ALLOWED_TRANSITIONS", "is_active", "is_completed",
    "validate_case_status", "transition_case_status", "archive_view",
]
