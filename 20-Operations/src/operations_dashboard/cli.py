import argparse
from pathlib import Path

from .contracts import publish


def main(argv=None):
    parser = argparse.ArgumentParser(prog="operations-dashboard-contracts")
    parser.add_argument("repository_root")
    parser.add_argument("contract_directory")
    args = parser.parse_args(argv)
    publish(Path(args.repository_root), Path(args.contract_directory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
