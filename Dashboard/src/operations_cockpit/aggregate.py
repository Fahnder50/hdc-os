from typing import Any, Mapping


HEALTH_ORDER = {"HEALTHY": 0, "WARNING": 1, "CRITICAL": 2}


def aggregate(contracts: list[Mapping[str, Any]], previous: Mapping[str, Any]) -> Mapping[str, Any]:
    if not contracts:
        raise ValueError("At least one dashboard contract is required")
    overall = max((item["health"] for item in contracts), key=HEALTH_ORDER.__getitem__)
    current = {item["domain"]["id"]: {"status": item["status"], "summary": item["summary"], "last_update": item["last_update"]} for item in contracts}
    changed = [item for item in contracts if previous.get(item["domain"]["id"]) != current[item["domain"]["id"]]]
    actions = []
    for item in contracts:
        if item["requires_action"]:
            actions.extend(item["recommendations"])
    return {"overall_health": overall, "contracts": contracts, "changed": changed, "actions": actions, "state": current}
