from datetime import datetime, timezone
import json
from pathlib import Path


def log_record(config, level, message, run_id=None, case_id=None, source_id=None, error_class=None):
    config.logs_path.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "level": level,
        "watch_run_id": run_id,
        "case_id": case_id,
        "source_id": source_id,
        "message": message,
        "error_class": error_class,
    }
    with (config.logs_path / "procurement-watch.jsonl").open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
