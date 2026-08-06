import json
from pathlib import Path
from datetime import datetime, timezone
from time import perf_counter

from .aggregate import aggregate
from .contracts import load_contracts
from .render import write_views


class CockpitRuntime:
    """Reads contracts, aggregates them generically, and renders two views."""

    def __init__(self, dashboard_directory: Path):
        self.directory = Path(dashboard_directory)

    def build(self):
        started = perf_counter()
        state_path = self.directory / ".state.json"
        status_path = self.directory / ".refresh-status.json"
        log_path = self.directory / ".refresh.log"
        previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
        try:
            model = aggregate(load_contracts(self.directory / "contracts"), previous)
            model["refresh"] = {"last_refresh": datetime.now(timezone.utc).isoformat(timespec="seconds"), "result": "SUCCESS", "duration_seconds": round(perf_counter() - started, 6)}
            write_views(model, self.directory)
            state_path.write_text(json.dumps(model["state"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            status_path.write_text(json.dumps(model["refresh"], indent=2) + "\n", encoding="utf-8")
            return model
        except Exception as error:
            failure = {"last_refresh": datetime.now(timezone.utc).isoformat(timespec="seconds"), "result": "FAILED", "duration_seconds": round(perf_counter() - started, 6), "error": str(error)}
            status_path.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
            with log_path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(failure, ensure_ascii=False) + "\n")
            raise
