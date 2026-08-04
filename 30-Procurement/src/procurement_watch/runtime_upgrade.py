"""Idempotent reconciliation of legacy runtime completion states.

This upgrade path is intentionally separate from the normal lifecycle
transition engine. Repository completion states are authoritative only while
upgrading an existing runtime.
"""

from datetime import date, datetime
import json
from pathlib import Path
import uuid

import yaml


ACTIVE_STATUSES = ("WATCHING", "QUALIFYING", "READY_FOR_REVIEW", "BUY_CANDIDATE")
COMPLETION_STATUSES = ("PURCHASED", "CANCELLED")
TRANSITION_TRIGGER = "procurement_cases_transition_update_contract"
UPGRADE_MARKER = "runtime_upgrade_rwo0039_r3"
TRANSITION_TRIGGER_SQL = f"""
CREATE TRIGGER IF NOT EXISTS {TRANSITION_TRIGGER}
BEFORE UPDATE OF status ON procurement_cases
WHEN OLD.status <> NEW.status AND NOT (
    (OLD.status = 'WATCHING' AND NEW.status IN ('QUALIFYING', 'CANCELLED')) OR
    (OLD.status = 'QUALIFYING' AND NEW.status IN ('READY_FOR_REVIEW', 'CANCELLED')) OR
    (OLD.status = 'READY_FOR_REVIEW' AND NEW.status IN ('BUY_CANDIDATE', 'CANCELLED')) OR
    (OLD.status = 'BUY_CANDIDATE' AND NEW.status IN ('PURCHASED', 'CANCELLED'))
)
BEGIN
    SELECT RAISE(ABORT, 'invalid procurement lifecycle transition');
END
"""


def _text(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value) if value is not None else None


def _repository_completions(repository_root):
    cases_path = Path(repository_root) / "30-Procurement" / "cases"
    result = {}
    for path in sorted(cases_path.glob("PC-*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        status = str(document.get("status", "")).upper()
        if status not in COMPLETION_STATUSES or not document.get("case_id"):
            continue
        result[document["case_id"]] = {
            "status": status,
            "completion_date": _text(
                document.get("closed_at")
                or document.get("purchased_at")
                or document.get("cancelled_at")
            ),
        }
    return result


def _requirement(connection, case_db_id, requirement_id):
    return connection.execute(
        "SELECT value_json FROM requirements WHERE case_id = ? AND requirement_id = ?",
        (case_db_id, requirement_id),
    ).fetchone()


def _insert_requirement_if_missing(connection, case_db_id, requirement_id, value, observed_at):
    if _requirement(connection, case_db_id, requirement_id) is not None:
        return False
    connection.execute(
        """
        INSERT INTO requirements(case_id, requirement_id, name, value_json, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'PASS', ?, ?)
        """,
        (case_db_id, requirement_id, requirement_id, json.dumps(value), observed_at, observed_at),
    )
    return True


def _insert_closure_journal_if_missing(connection, case_db_id, observed_at):
    exists = connection.execute(
        "SELECT 1 FROM journal_entries WHERE case_id = ? AND recommendation_status = 'CLOSED' LIMIT 1",
        (case_db_id,),
    ).fetchone()
    if exists:
        return False
    summary = {
        "recommendation_status": "CLOSED",
        "offers": [],
        "active_offers": 0,
        "events": [],
    }
    changes = {
        "completion_migration": True,
        "price_changes": [],
        "delivery_changes": [],
        "new_offers": [],
        "new_events": [],
    }
    connection.execute(
        """
        INSERT INTO journal_entries(entry_id, case_id, watch_run_id, observed_at,
            recommendation_status, summary_json, changes_json, created_at)
        VALUES (?, ?, NULL, ?, 'CLOSED', ?, ?, ?)
        """,
        (
            f"JRN-{uuid.uuid4().hex[:12]}", case_db_id, observed_at,
            json.dumps(summary, sort_keys=True), json.dumps(changes, sort_keys=True), observed_at,
        ),
    )
    return True


def reconcile_legacy_runtime(connection, repository_root):
    """Upgrade repository-completed legacy cases without normal transitions."""
    result = {
        "checked": 0,
        "status_migrations": 0,
        "completion_metadata_added": 0,
        "closure_journals_added": 0,
    }
    already_applied = connection.execute(
        "SELECT 1 FROM runtime_metadata WHERE metadata_key = ?", (UPGRADE_MARKER,)
    ).fetchone()
    if already_applied:
        return result

    repository_cases = _repository_completions(repository_root)
    result["checked"] = len(repository_cases)
    if not repository_cases:
        connection.execute(
            "INSERT INTO runtime_metadata(metadata_key, metadata_value, created_at) VALUES (?, 'applied', ?)",
            (UPGRADE_MARKER, datetime.now().astimezone().isoformat(timespec="seconds")),
        )
        return result

    runtime_rows = {
        row["case_id"]: row
        for row in connection.execute(
            "SELECT id, case_id, status, updated_at FROM procurement_cases"
        ).fetchall()
    }
    mismatches = [
        (runtime_rows[case_id], repository)
        for case_id, repository in repository_cases.items()
        if case_id in runtime_rows
        and runtime_rows[case_id]["status"] in ACTIVE_STATUSES
    ]
    if mismatches:
        connection.execute(f"DROP TRIGGER IF EXISTS {TRANSITION_TRIGGER}")
        try:
            for runtime, repository in mismatches:
                connection.execute(
                    "UPDATE procurement_cases SET status = ? WHERE id = ?",
                    (repository["status"], runtime["id"]),
                )
                result["status_migrations"] += 1
        finally:
            connection.execute(TRANSITION_TRIGGER_SQL)

    for case_id, repository in repository_cases.items():
        runtime = runtime_rows.get(case_id)
        if runtime is None:
            continue
        effective_status = repository["status"] if runtime["status"] in ACTIVE_STATUSES else runtime["status"]
        if effective_status != repository["status"]:
            continue
        completion_date = repository["completion_date"] or runtime["updated_at"]
        if _insert_requirement_if_missing(
            connection, runtime["id"], "completion_date", completion_date, completion_date
        ):
            result["completion_metadata_added"] += 1
        if _insert_requirement_if_missing(
            connection, runtime["id"], "closed_flag", True, completion_date
        ):
            result["completion_metadata_added"] += 1
        if _insert_closure_journal_if_missing(connection, runtime["id"], completion_date):
            result["closure_journals_added"] += 1
    connection.execute(
        "INSERT INTO runtime_metadata(metadata_key, metadata_value, created_at) VALUES (?, 'applied', ?)",
        (UPGRADE_MARKER, datetime.now().astimezone().isoformat(timespec="seconds")),
    )
    return result


__all__ = ["reconcile_legacy_runtime"]
