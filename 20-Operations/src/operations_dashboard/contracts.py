from datetime import datetime
from pathlib import Path
import re

import yaml

from shared.dashboard_contract import write_dashboard_contract


def _deployment_contract(root: Path):
    source = root / "20-Operations" / "WO-0041-First-Deployment-Readiness.md"
    text = source.read_text(encoding="utf-8")
    status_match = re.search(r"Aktueller Gate-Status: `([^`]+)`", text)
    gate_rows = re.findall(r"^\| ([^|]+) \| ([^|]+) \| \*\*([^*]+)\*\*", text, re.MULTILINE)
    gates = [{"gate": row[0].strip(), "status": "PASS" if row[2].strip().startswith("PASS") else "FAIL"} for row in gate_rows if row[0].strip() in {"Hardware Ready", "Configuration Ready", "Installation Ready", "Test Ready", "Rollback Ready", "Architecture Conformity"}]
    passed = sum(item["status"].startswith("PASS") for item in gates)
    missing = ["OPNsense Firewall", "Managed Switch"]
    status = status_match.group(1) if status_match else "UNKNOWN"
    now = datetime.fromtimestamp(source.stat().st_mtime).astimezone().isoformat(timespec="seconds")
    return {
        "domain": {"id": "deployment", "version": "1.0"},
        "health": "CRITICAL" if status == "NOT_READY" else "HEALTHY",
        "summary": "First Deployment is blocked by missing firewall, managed switch, and open readiness evidence.",
        "status": status,
        "last_update": now,
        "requires_action": status != "READY_FOR_FIRST_DEPLOYMENT",
        "recommendations": [
            {"id": "deployment-hardware", "text": "Procure and qualify the Horizon-1 firewall and managed switch."},
            {"id": "deployment-gates", "text": "Close the remaining WO-0041 readiness evidence before deployment."},
        ] if status != "READY_FOR_FIRST_DEPLOYMENT" else [],
        "links": ["20-Operations/WO-0041-First-Deployment-Readiness.md"],
        "details": {"gates": gates, "bottleneck": "Firewall and Managed Switch are missing; further WO-0041 evidence is open.", "missing_hardware": missing, "first_deployment_progress": f"{passed}/{len(gates)} gates PASS ({round(100 * passed / len(gates)) if gates else 0}%)"},
    }


def _asset_contract(root: Path):
    registry_path = root / "20-Operations" / "assets" / "registry.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    records = []
    for item in registry.get("assets", []):
        path = registry_path.parent / item["record"]
        records.append(yaml.safe_load(path.read_text(encoding="utf-8")))
    productive = [item for item in records if item.get("status") == "PRODUCTION"]
    critical = [item["asset_id"] for item in productive if item.get("asset_class") in {"gateway_power", "firewall", "gateway"}]
    unhealthy = [item["asset_id"] for item in productive if item.get("acceptance_blockers")]
    latest = max(records, key=lambda item: item.get("acceptance_date") or "") if records else None
    now = datetime.fromtimestamp(registry_path.stat().st_mtime).astimezone().isoformat(timespec="seconds")
    return {
        "domain": {"id": "assets", "version": "1.0"},
        "health": "CRITICAL" if unhealthy else "HEALTHY",
        "summary": f"{len(productive)} productive asset; no known acceptance blockers." if not unhealthy else f"{len(unhealthy)} productive asset requires attention.",
        "status": "OPERATIONAL" if productive and not unhealthy else "ATTENTION_REQUIRED",
        "last_update": now,
        "requires_action": bool(unhealthy),
        "recommendations": [{"id": asset_id, "text": "Review asset acceptance blockers."} for asset_id in unhealthy],
        "links": ["20-Operations/assets/registry.yaml"],
        "details": {"productive_assets": len(productive), "asset_health": "HEALTHY" if not unhealthy else "CRITICAL", "critical_assets": critical, "last_acceptance_status": f"{latest['asset_id']}: {latest['status']} on {latest.get('acceptance_date')}" if latest else "No acceptance available"},
    }


def publish(root: Path, contract_directory: Path):
    return [write_dashboard_contract(contract_directory, item) for item in (_deployment_contract(root), _asset_contract(root))]
