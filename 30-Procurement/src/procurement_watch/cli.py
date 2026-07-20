import argparse
import json
from pathlib import Path
import sys

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
    run_watch,
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
    case = commands.add_parser("case")
    case_commands = case.add_subparsers(dest="case_command", required=True)
    case_import = case_commands.add_parser("import")
    case_import.add_argument("path")
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
        elif args.command == "case" and args.case_command == "import":
            _print_json(import_case(config, args.path))
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
    except Exception as error:
        print(f"procurement_watch: {error}", file=sys.stderr)
        return 1
    return 0
