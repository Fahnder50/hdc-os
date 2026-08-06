from html import escape
from pathlib import Path
from typing import Any, Mapping
import os
import uuid


def _contract_by_id(model, domain_id):
    return next((item for item in model["contracts"] if item["domain"]["id"] == domain_id), None)


def _lines(value, empty="None"):
    return [str(item) for item in value] or [empty]


def _detail(value):
    if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
        return "; ".join(", ".join(f"{key.replace('_', ' ').title()}: {child}" for key, child in item.items()) for item in value)
    if isinstance(value, list):
        return ", ".join(map(str, value))
    return str(value)


def markdown(model: Mapping[str, Any]) -> str:
    changed = _lines([f"**{item['domain']['id'].title()}:** {item['summary']}" for item in model["changed"]], "No important changes since the previous cockpit run.")
    lines = ["# HDC-OS Operations Cockpit", "", "## Overall Health", "", f"**{model['overall_health']}**", "", "## Today's Summary — Daily Briefing", ""]
    lines.extend(f"- {item}" for item in changed)
    refresh = model.get("refresh", {})
    lines.extend(["", "## Cockpit Refresh", "", f"- **Last Refresh:** {refresh.get('last_refresh')}", f"- **Refresh Result:** {refresh.get('result')}", f"- **Refresh Duration Seconds:** {refresh.get('duration_seconds')}"])
    domain_ids = sorted(item["domain"]["id"] for item in model["contracts"])
    for domain_id in domain_ids:
        item = _contract_by_id(model, domain_id)
        lines.extend(["", f"## {domain_id.title()}", ""])
        if not item:
            lines.append("No contract available.")
            continue
        lines.extend([f"**{item['health']} — {item['status']}**", "", item["summary"], ""])
        for key, value in item.get("details", {}).items():
            lines.append(f"- **{key.replace('_', ' ').title()}:** {_detail(value)}")
    lines.extend(["", "## Recommended Actions", ""])
    lines.extend(f"- {item.get('case_id', item.get('id', 'Action'))}: {item.get('recommendation', item.get('text', item))}" for item in model["actions"])
    if not model["actions"]:
        lines.append("- No action currently required.")
    lines.append("")
    return "\n".join(lines)


def html(model: Mapping[str, Any]) -> str:
    md = markdown(model)
    blocks = []
    in_list = False
    for line in md.splitlines():
        if line.startswith("# "):
            blocks.append(f"<h1>{escape(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_list: blocks.append("</ul>"); in_list = False
            blocks.append(f"<h2>{escape(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list: blocks.append("<ul>"); in_list = True
            blocks.append(f"<li>{escape(line[2:])}</li>")
        elif line:
            if in_list: blocks.append("</ul>"); in_list = False
            blocks.append(f"<p>{escape(line)}</p>")
    if in_list: blocks.append("</ul>")
    body = "\n".join(blocks)
    return f"<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><title>HDC-OS Operations Cockpit</title><style>body{{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#17202a}}h1{{border-bottom:4px solid #2463a9}}h2{{margin-top:2rem;color:#193b63}}li{{margin:.4rem 0}}p{{line-height:1.5}}</style></head><body>\n{body}\n</body></html>\n"


def write_views(model: Mapping[str, Any], directory: Path) -> None:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    values = {directory / "Latest.md": markdown(model), directory / "Latest.html": html(model)}
    token = uuid.uuid4().hex
    staged = {}
    backups = {}
    try:
        for destination, content in values.items():
            temporary = destination.with_name(f".{destination.name}.{token}.tmp")
            temporary.write_text(content, encoding="utf-8")
            staged[destination] = temporary
        for destination in values:
            if destination.exists():
                backup = destination.with_name(f".{destination.name}.{token}.bak")
                backup.write_bytes(destination.read_bytes())
                backups[destination] = backup
        for destination, temporary in staged.items():
            os.replace(temporary, destination)
    except Exception:
        for destination, backup in backups.items():
            if backup.exists():
                os.replace(backup, destination)
        raise
    finally:
        for path in (*staged.values(), *backups.values()):
            path.unlink(missing_ok=True)
