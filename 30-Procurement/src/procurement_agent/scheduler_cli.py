"""Compatibility entry point delegated to HDC-OS Scheduler Lifecycle Management."""

from pathlib import Path
import sys

from shared.scheduler_lifecycle.cli import main as lifecycle_main


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    aliases = {"run-now": None, "disable": None}
    if arguments and arguments[0] in aliases:
        raise ValueError(f"'{arguments[0]}' is no longer an unmanaged operation; use hdc-scheduler and the registry")
    root = Path(__file__).resolve().parents[3]
    return lifecycle_main(arguments + ["procurement-agent-daily", "--repository-root", str(root)])


if __name__ == "__main__":
    raise SystemExit(main())
