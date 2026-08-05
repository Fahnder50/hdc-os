import argparse
from pathlib import Path

from .dashboard_contracts import publish


def main(argv=None):
    parser = argparse.ArgumentParser(prog="procurement-dashboard-contracts")
    parser.add_argument("directory")
    args = parser.parse_args(argv)
    publish(Path(args.directory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
