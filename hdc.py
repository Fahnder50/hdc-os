import argparse

from shared.infrastructure import Infrastructure, render_status


def main(argv=None):
    parser = argparse.ArgumentParser(prog="hdc.py")
    commands = parser.add_subparsers(dest="command", required=True)
    infrastructure = commands.add_parser("infrastructure")
    infrastructure_commands = infrastructure.add_subparsers(dest="infrastructure_command", required=True)
    infrastructure_commands.add_parser("status")
    args = parser.parse_args(argv)
    if args.command == "infrastructure" and args.infrastructure_command == "status":
        print(render_status(Infrastructure()))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
