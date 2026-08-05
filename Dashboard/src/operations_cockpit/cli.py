import argparse
from pathlib import Path

from .runtime import CockpitRuntime


def main(argv=None):
    parser = argparse.ArgumentParser(prog="operations-cockpit")
    parser.add_argument("dashboard", nargs="?", default=str(Path(__file__).resolve().parents[3] / "Dashboard"))
    args = parser.parse_args(argv)
    CockpitRuntime(Path(args.dashboard)).build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
