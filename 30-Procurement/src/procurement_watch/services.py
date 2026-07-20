from datetime import datetime, timezone
import uuid

from .database import connect, initialize, schema_status


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_database(config):
    return initialize(config)


def migrate_database(config):
    return initialize(config)


def run_watch(config, simulate_failure=False):
    initialize(config)
    connection = connect(config)
    try:
        run_id = f"WR-{uuid.uuid4().hex[:12]}"
        started_at = utc_now()
        connection.execute(
            "INSERT INTO watch_runs(watch_run_id, started_at, status) VALUES (?, ?, ?)",
            (run_id, started_at, "running"),
        )
        database_run_id = connection.execute("SELECT id FROM watch_runs WHERE watch_run_id = ?", (run_id,)).fetchone()[0]
        ended_at = utc_now()
        result_status = "failed" if simulate_failure else "succeeded"
        result_message = "Controlled foundation failure." if simulate_failure else "No live sources configured; controlled foundation run completed."
        connection.execute(
            "INSERT INTO watch_run_results(watch_run_id, status, message, created_at) VALUES (?, ?, ?, ?)",
            (database_run_id, result_status, result_message, ended_at),
        )
        connection.execute(
            "UPDATE watch_runs SET ended_at = ?, status = ?, error_count = ? WHERE id = ?",
            (ended_at, result_status, int(simulate_failure), database_run_id),
        )
        connection.commit()
        return {"watch_run_id": run_id, "started_at": started_at, "ended_at": ended_at, "status": result_status, "error_count": int(simulate_failure)}
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def procurement_status(config):
    result = schema_status(config)
    required_tables = {"procurement_cases", "events", "watch_runs"}
    if not result["reachable"] or not required_tables.issubset(result["tables"]):
        result.update({"initialized": False, "cases": None, "open_events": None, "last_watch_run": None})
        return result
    connection = connect(config)
    try:
        cases = connection.execute("SELECT COUNT(*) FROM procurement_cases").fetchone()[0]
        open_events = connection.execute("SELECT COUNT(*) FROM events WHERE status = 'open'").fetchone()[0]
        last_run = connection.execute(
            "SELECT watch_run_id, status, started_at, ended_at, error_count FROM watch_runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
    finally:
        connection.close()
    result.update({"initialized": True, "cases": cases, "open_events": open_events, "last_watch_run": dict(last_run) if last_run else None})
    return result
