import json
from pathlib import Path

from .aggregate import aggregate
from .contracts import load_contracts
from .render import write_views


class CockpitRuntime:
    """Reads contracts, aggregates them generically, and renders two views."""

    def __init__(self, dashboard_directory: Path):
        self.directory = Path(dashboard_directory)

    def build(self):
        state_path = self.directory / ".state.json"
        previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
        model = aggregate(load_contracts(self.directory / "contracts"), previous)
        write_views(model, self.directory)
        state_path.write_text(json.dumps(model["state"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return model
