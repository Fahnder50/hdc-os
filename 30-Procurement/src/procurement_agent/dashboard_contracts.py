from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from procurement_watch.config import resolve_config
from shared.dashboard_contract import write_dashboard_contract

from shared.scheduler_lifecycle.registry import load_registry


def _latest(directory: Path, pattern: str):
    paths = sorted(directory.glob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)
    return json.loads(paths[0].read_text(encoding="utf-8")) if paths else None


def _next_run(daily_at: str) -> str:
    now = datetime.now().astimezone()
    hour, minute = map(int, daily_at.split(":"))
    result = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if result <= now:
        result += timedelta(days=1)
    return result.isoformat(timespec="minutes")


def publish(contract_directory: Path):
    app = resolve_config()
    scheduler = next(item for item in load_registry(Path(app.repository_root) / "20-Operations" / "config" / "schedulers.yaml") if item["scheduler_id"] == "procurement-agent-daily")
    external_default = Path(os.environ["LOCALAPPDATA"]) / "HDC-OS" / "agent-runtime" / "procurement" if os.environ.get("LOCALAPPDATA") else Path(app.runtime_path) / "agents" / "procurement"
    runtime = Path(os.environ.get("HDC_AGENT_RUNTIME", external_default))
    log = _latest(runtime / "logs", "*.json")
    summary = _latest(runtime / "executive-summaries", "*.json")
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    recommendations = summary.get("recommendations", []) if summary else []
    action_recommendations = [item for item in recommendations if item.get("information_status") == "ACTION_REQUIRED"]
    procurement = {
        "domain": {"id": "procurement", "version": "1.0"},
        "health": "WARNING" if action_recommendations or not summary else "HEALTHY",
        "summary": summary.get("executive_summary", {}).get("summary", "No Procurement Agent summary is available.") if summary else "No Procurement Agent summary is available.",
        "status": log.get("execution_result", "UNKNOWN") if log else "UNKNOWN",
        "last_update": log.get("ended_at", now) if log else now,
        "requires_action": bool(action_recommendations or not summary),
        "recommendations": action_recommendations,
        "links": ["30-Procurement/operations/Procurement-Agent-Scheduler.md"],
        "details": {
            "active_cases": summary.get("dashboard", {}).get("active_procurement_cases", len(recommendations)) if summary else 0,
            "last_run": log.get("ended_at") if log else None,
            "next_run": _next_run(scheduler["schedule"]["at"]),
            "agent_status": log.get("execution_result", "UNKNOWN") if log else "UNKNOWN",
            "current_recommendations": recommendations,
        },
    }
    agents = {
        "domain": {"id": "agents", "version": "1.0"},
        "health": "HEALTHY" if log and log.get("execution_result") == "SUCCESS" else "WARNING",
        "summary": "One registered agent: Procurement Agent v1." if log else "Procurement Agent v1 is registered; no run is available.",
        "status": log.get("execution_result", "NO_RUN") if log else "NO_RUN",
        "last_update": log.get("ended_at", now) if log else now,
        "requires_action": bool(log and log.get("execution_result") == "FAILED"),
        "recommendations": [{"id": "agent-run", "text": "Review the failed Procurement Agent run."}] if log and log.get("execution_result") == "FAILED" else [],
        "links": ["10-Engineering/Architecture/Generic-Agent-Runtime.md"],
        "details": {
            "registered_agents": ["procurement-agent"],
            "last_run": log.get("ended_at") if log else None,
            "next_run": _next_run(scheduler["schedule"]["at"]),
            "result": log.get("execution_result", "NO_RUN") if log else "NO_RUN",
            "duration_seconds": log.get("duration_seconds") if log else None,
            "provider": log.get("analysis", {}).get("provider") if log else None,
            "model": log.get("analysis", {}).get("model") if log else None,
            "fallback_used": log.get("analysis", {}).get("fallback_used") if log else None,
        },
    }
    return [write_dashboard_contract(contract_directory, item) for item in (procurement, agents)]
