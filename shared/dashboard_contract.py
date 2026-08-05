import json
from pathlib import Path
from typing import Any, Mapping


def write_dashboard_contract(directory: Path, contract: Mapping[str, Any]) -> Path:
    destination = Path(directory) / f"{contract['domain']['id']}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(contract, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return destination
