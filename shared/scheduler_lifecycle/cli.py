import argparse
import json
from pathlib import Path

from .manager import SchedulerLifecycleManager
from .registry import load_registry, persist_dynamic_state
from .windows import WindowsTaskScheduler
from .dashboard import scheduler_dashboard_contract
from shared.dashboard_contract import write_dashboard_contract


def execute(command: str, repository_root: Path, scheduler_id: str | None = None):
    root = Path(repository_root)
    entries = load_registry(root / "20-Operations" / "config" / "schedulers.yaml")
    if scheduler_id:
        entries = [entry for entry in entries if entry["scheduler_id"] == scheduler_id]
        if not entries:
            raise ValueError(f"Unknown scheduler_id: {scheduler_id}")
    manager = SchedulerLifecycleManager(WindowsTaskScheduler(root))
    operation = {"install": manager.install, "update": manager.update, "verify": manager.verify, "status": manager.verify, "repair": manager.repair, "remove": manager.remove}[command]
    results = []
    statuses = []
    registry_path = root / "20-Operations" / "config" / "schedulers.yaml"
    for entry in entries:
        result = operation(entry)
        final_status = result["after"] if command == "repair" else result
        persist_dynamic_state(registry_path, entry["scheduler_id"], final_status)
        results.append(result)
        statuses.append(final_status)
    write_dashboard_contract(root / "Dashboard" / "contracts", scheduler_dashboard_contract(statuses))
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(prog="hdc-scheduler")
    parser.add_argument("command", choices=("install", "update", "verify", "status", "repair", "remove"))
    parser.add_argument("scheduler_id", nargs="?")
    parser.add_argument("--repository-root", default=str(Path(__file__).resolve().parents[2]))
    args = parser.parse_args(argv)
    try:
        print(json.dumps(execute(args.command, Path(args.repository_root), args.scheduler_id), indent=2, ensure_ascii=False, default=str))
        return 0
    except Exception as error:
        print(json.dumps({"status": "BROKEN", "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
