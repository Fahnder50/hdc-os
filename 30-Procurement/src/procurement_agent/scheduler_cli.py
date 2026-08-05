import argparse
import json
from pathlib import Path
import subprocess
import sys

from procurement_watch.config import resolve_config

from .config import load_agent_config


def _run(arguments, check=True):
    return subprocess.run(arguments, check=check, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _task_command(repository_root: Path) -> str:
    script = repository_root / "30-Procurement" / "scripts" / "run-procurement-agent.ps1"
    return f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{script}" -PythonPath "{sys.executable}"'


def install(config):
    command = [
        "schtasks.exe", "/Create", "/F", "/SC", "DAILY", "/ST", config.daily_at,
        "/TN", config.task_name, "/TR", _task_command(config.source_path.parents[2]),
    ]
    _run(command)
    return status(config) | {"operation": "installed", "daily_at": config.daily_at}


def status(config):
    result = _run(["schtasks.exe", "/Query", "/TN", config.task_name, "/FO", "LIST", "/V"], check=False)
    return {
        "task_name": config.task_name,
        "installed": result.returncode == 0,
        "details": result.stdout.strip() if result.returncode == 0 else None,
    }


def disable(config):
    _run(["schtasks.exe", "/Change", "/TN", config.task_name, "/Disable"])
    return status(config) | {"operation": "disabled"}


def remove(config):
    before = status(config)
    if before["installed"]:
        _run(["schtasks.exe", "/Delete", "/F", "/TN", config.task_name])
    return {"task_name": config.task_name, "installed": False, "operation": "removed"}


def run_now(config):
    _run(["schtasks.exe", "/Run", "/TN", config.task_name])
    return status(config) | {"operation": "started"}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="procurement-agent-scheduler")
    parser.add_argument("command", choices=("install", "status", "disable", "remove", "run-now"))
    args = parser.parse_args(argv)
    app_config = resolve_config()
    config = load_agent_config(app_config.repository_root)
    operations = {"install": install, "status": status, "disable": disable, "remove": remove, "run-now": run_now}
    try:
        result = operations[args.command](config)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except subprocess.CalledProcessError as error:
        print(json.dumps({"operation": args.command, "exit_status": "FAILED", "message": error.stderr.strip()}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
