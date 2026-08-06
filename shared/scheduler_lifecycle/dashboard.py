from datetime import datetime, timezone


def scheduler_dashboard_contract(statuses):
    unhealthy = [item for item in statuses if item["installation_state"] != "HEALTHY"]
    return {
        "domain": {"id": "schedulers", "version": "1.0"},
        "health": "CRITICAL" if any(item["installation_state"] in {"DRIFT", "BROKEN"} for item in statuses) else "WARNING" if unhealthy else "HEALTHY",
        "summary": f"{len(statuses)} HDC-OS scheduler verified; {len(unhealthy)} require attention.",
        "status": "HEALTHY" if not unhealthy else "DRIFT" if any(item["installation_state"] == "DRIFT" for item in statuses) else unhealthy[0]["installation_state"],
        "last_update": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "requires_action": bool(unhealthy),
        "recommendations": [{"id": item["scheduler_id"], "text": f"Run hdc-scheduler repair for {item['scheduler_id']}."} for item in unhealthy],
        "links": ["10-Engineering/Architecture/Scheduler-Lifecycle-Management.md"],
        "details": {"registered_schedulers": len(statuses), "scheduler_health": [{"scheduler_id": item["scheduler_id"], "state": item["installation_state"], "last_verification": item["last_verification"]} for item in statuses]},
    }
