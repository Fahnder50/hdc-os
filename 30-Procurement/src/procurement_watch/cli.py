import argparse
import json
import sys

from .config import resolve_config
from .database import schema_status
from .services import init_database, migrate_database, procurement_status, run_watch


def _parser():
    parser = argparse.ArgumentParser(prog="procurement_watch")
    commands = parser.add_subparsers(dest="command", required=True)
    db = commands.add_parser("db")
    db_commands = db.add_subparsers(dest="db_command", required=True)
    db_commands.add_parser("init")
    db_commands.add_parser("status")
    commands.add_parser("migrate")
    watch = commands.add_parser("watch")
    watch_commands = watch.add_subparsers(dest="watch_command", required=True)
    watch_commands.add_parser("run")
    commands.add_parser("status")
    return parser


def _print_json(value):
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def main(argv=None):
    args = _parser().parse_args(argv)
    config = resolve_config()
    try:
        if args.command == "db" and args.db_command == "init":
            _print_json(init_database(config))
        elif args.command == "db" and args.db_command == "status":
            _print_json(schema_status(config))
        elif args.command == "migrate":
            _print_json(migrate_database(config))
        elif args.command == "watch" and args.watch_command == "run":
            result = run_watch(config)
            _print_json(result)
            return 0 if result.get("status") == "succeeded" else 1
        elif args.command == "status":
            _print_json(procurement_status(config))
    except Exception as error:
        print(f"procurement_watch: {error}", file=sys.stderr)
        return 1
    return 0
