import argparse
from datetime import datetime
import json
from pathlib import Path
import sys

from .backup import backup_database, restore_database
from .config import resolve_config
from .database import schema_status
from .services import (
    add_offer,
    add_product,
    case_status,
    history_for_case,
    import_case,
    init_database,
    migrate_database,
    offers_for_case,
    procurement_status,
    current_events,
    doctor,
    recent_watch_runs,
    report_case,
    run_watch,
    run_live_watch,
    import_all_cases,
    portfolio_watch,
    portfolio_status,
)


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
    live = watch_commands.add_parser("live")
    live.add_argument("case_id", nargs="?")
    live.add_argument("--all", action="store_true")
    watch_commands.add_parser("runs")
    case = commands.add_parser("case")
    case_commands = case.add_subparsers(dest="case_command", required=True)
    case_import = case_commands.add_parser("import")
    case_import.add_argument("path")
    portfolio_import = commands.add_parser("import")
    portfolio_import.add_argument("--all", action="store_true", required=True)
    portfolio = commands.add_parser("portfolio")
    portfolio_commands = portfolio.add_subparsers(dest="portfolio_command", required=True)
    portfolio_commands.add_parser("status")
    product = commands.add_parser("product")
    product_commands = product.add_subparsers(dest="product_command", required=True)
    product_add = product_commands.add_parser("add")
    product_add.add_argument("--product-id", required=True)
    product_add.add_argument("--product-name", required=True)
    product_add.add_argument("--manufacturer")
    product_add.add_argument("--model")
    product_add.add_argument("--technical-reference")
    product_add.add_argument("--technical-json", default="{}")
    product_add.add_argument("--technical-json-file")
    product_add.add_argument("--case-id")
    offer = commands.add_parser("offer")
    offer_commands = offer.add_subparsers(dest="offer_command", required=True)
    offer_add = offer_commands.add_parser("add")
    offer_add.add_argument("--offer-id", required=True)
    offer_add.add_argument("--product-id", required=True)
    offer_add.add_argument("--vendor-id", required=True)
    offer_add.add_argument("--vendor-name", required=True)
    offer_add.add_argument("--price", required=True)
    offer_add.add_argument("--shipping", default="0")
    offer_add.add_argument("--currency", default="EUR")
    offer_add.add_argument("--availability", default="unknown")
    offer_add.add_argument("--source-type", default="manual")
    offer_add.add_argument("--source-reference")
    offer_add.add_argument("--delivery-note")
    offer_add.add_argument("--observed-at")
    offer_add.add_argument("--case-id")
    offers = commands.add_parser("offers")
    offers.add_argument("case_id")
    history = commands.add_parser("history")
    history.add_argument("case_id")
    status = commands.add_parser("status")
    status.add_argument("case_id", nargs="?")
    report = commands.add_parser("report")
    report.add_argument("case_id")
    commands.add_parser("doctor")
    commands.add_parser("events")
    backup = commands.add_parser("backup")
    backup.add_argument("destination")
    restore = commands.add_parser("restore")
    restore.add_argument("source")
    restore.add_argument("--overwrite", action="store_true")
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
        elif args.command == "watch" and args.watch_command == "live":
            if args.all:
                result = portfolio_watch(config)
                _print_portfolio_summary(result)
                return 0 if result["status"] == "completed" else 1
            if not args.case_id:
                raise ValueError("watch live requires a case_id or --all")
            result = run_live_watch(config, args.case_id)
            _print_json(result)
            return 0 if result.get("status") == "succeeded" else 1
        elif args.command == "watch" and args.watch_command == "runs":
            _print_json(recent_watch_runs(config))
        elif args.command == "case" and args.case_command == "import":
            _print_json(import_case(config, args.path))
        elif args.command == "import":
            result = import_all_cases(config)
            _print_json(result)
        elif args.command == "portfolio" and args.portfolio_command == "status":
            _print_portfolio_status(portfolio_status(config))
        elif args.command == "product" and args.product_command == "add":
            try:
                technical_source = Path(args.technical_json_file).read_text(encoding="utf-8-sig") if args.technical_json_file else args.technical_json
                technical = json.loads(technical_source)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid --technical-json: {error.msg}") from error
            _print_json(add_product(config, args.product_id, args.product_name, args.manufacturer, args.model, args.technical_reference, technical, args.case_id))
        elif args.command == "offer" and args.offer_command == "add":
            _print_json(add_offer(config, args.offer_id, args.product_id, args.vendor_id, args.vendor_name, args.price, args.shipping, args.currency, args.availability, args.source_type, args.source_reference, args.delivery_note, args.observed_at, args.case_id))
        elif args.command == "offers":
            _print_json(offers_for_case(config, args.case_id))
        elif args.command == "history":
            _print_json(history_for_case(config, args.case_id))
        elif args.command == "status":
            _print_json(case_status(config, args.case_id) if args.case_id else procurement_status(config))
        elif args.command == "report":
            _print_json({"path": str(report_case(config, args.case_id))})
        elif args.command == "doctor":
            result = doctor(config)
            _print_json(result)
            return 0 if result["ok"] else 1
        elif args.command == "events":
            _print_json(current_events(config))
        elif args.command == "backup":
            _print_json({"path": str(backup_database(config, args.destination))})
        elif args.command == "restore":
            _print_json({"path": str(restore_database(config, args.source, args.overwrite))})
    except Exception as error:
        print(f"procurement_watch: {error}", file=sys.stderr)
        return 1
    return 0


def _print_portfolio_summary(result):
    print("=" * 50)
    print("Portfolio Summary")
    print("=" * 50)
    for case in result["cases"]:
        print(f"\n{case['case_id']}  {case['status']}")
        print(f"{case['offers']} Angebote")
        source_label = "Quelle" if case["sources"] == 1 else "Quellen"
        print(f"{case['sources']} {source_label}")
        if case.get("error"):
            print(f"Fehler: {case['error']}")
    print("\n" + "=" * 50)
    print("Portfolio")
    print(f"\n{result['case_count']} Cases")
    print(f"\n{result['offer_count']} Angebote")
    print(f"\n{result['source_count']} Quellen")
    print(f"\n{result['error_count']} Fehler")
    print(f"\n{result['duration_seconds']:.3f} Sekunden")
    health = result["health"]
    print(f"\nWATCHING: {health['watching']}")
    print(f"CONDITIONAL_BUY: {health['conditional_buy']}")
    print(f"REVIEW: {health['review']}")
    print(f"BLOCKED: {health['blocked']}")
    print("\n" + "=" * 50)
    if result["status"] == "completed_with_warnings":
        print("Portfolio completed with warnings.")
    else:
        print("Portfolio completed.")


def _print_portfolio_status(result):
    print("Portfolio\n")
    print(f"{result['active_cases']} aktive Cases\n")
    print(f"{result['statuses'].get('CONDITIONAL_BUY', 0)} CONDITIONAL_BUY")
    print(f"{result['statuses'].get('REVIEW', 0)} REVIEW")
    print(f"{result['statuses'].get('BLOCKED', 0)} BLOCKED")
    last_run = result.get("last_run")
    print("\nLetzter Lauf:")
    if last_run and last_run.get("ended_at"):
        timestamp = datetime.fromisoformat(last_run["ended_at"].replace("Z", "+00:00"))
        print(timestamp.strftime("%d.%m.%Y %H:%M"))
    else:
        print("—")
    print("\nNächster Lauf:\n—")
