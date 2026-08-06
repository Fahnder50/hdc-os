import base64
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping
import xml.etree.ElementTree as ET


NS = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}


class WindowsTaskScheduler:
    def __init__(self, repository_root: Path):
        self.repository_root = Path(repository_root)
        self.script = Path(__file__).with_name("windows_task.ps1")

    def _resolved(self, definition):
        value = json.loads(json.dumps(definition))
        runtime = value["runtime"]
        runtime["arguments"] = runtime["arguments"].format(repository_root=str(self.repository_root), python_path=sys.executable)
        runtime["user"] = os.environ.get("USERNAME", runtime["user"])
        return value

    @staticmethod
    def _current_sid():
        result = subprocess.run(["whoami.exe", "/user", "/fo", "csv", "/nh"], check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        fields = next(__import__("csv").reader([result.stdout.strip()]))
        return fields[1]

    def expected(self, definition):
        value = self._resolved(definition)
        return {
            "name": value["name"], "trigger": value["trigger"], "at": value["schedule"]["at"],
            "start_when_available": value["schedule"]["start_when_available"], "wake_to_run": value["schedule"]["wake_to_run"],
            "allow_start_on_batteries": value["runtime"]["allow_start_on_batteries"], "stop_on_batteries": value["runtime"]["stop_on_batteries"],
            "user": self._current_sid(), "logon_type": value["runtime"]["logon_type"], "command": value["runtime"]["command"],
            "arguments": value["runtime"]["arguments"], "enabled": value["runtime"]["enabled"],
        }

    def _invoke(self, operation, definition, check=True):
        encoded = base64.b64encode(json.dumps(self._resolved(definition)).encode("utf-8")).decode("ascii")
        return subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(self.script), "-Operation", operation, "-Definition", encoded], check=check, capture_output=True, text=True, encoding="utf-8", errors="replace")

    def apply(self, definition):
        self._invoke("Apply", definition)

    def remove(self, definition):
        self._invoke("Remove", definition)

    def inspect(self, definition):
        result = self._invoke("Export", definition, check=False)
        if result.returncode == 3:
            return None
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        root = ET.fromstring(result.stdout.lstrip("\ufeff"))
        text = lambda path, default=None: (node.text if (node := root.find(path, NS)) is not None else default)
        boolean = lambda path, default=False: str(text(path, str(default))).lower() == "true"
        start = text(".//t:CalendarTrigger/t:StartBoundary", "")
        return {
            "name": definition["name"], "trigger": "DAILY" if root.find(".//t:ScheduleByDay", NS) is not None else "UNKNOWN",
            "at": start[11:16], "start_when_available": boolean(".//t:StartWhenAvailable"), "wake_to_run": boolean(".//t:WakeToRun"),
            "allow_start_on_batteries": not boolean(".//t:DisallowStartIfOnBatteries", True), "stop_on_batteries": boolean(".//t:StopIfGoingOnBatteries", True),
            "user": text(".//t:Principal/t:UserId"), "logon_type": text(".//t:LogonType"), "command": text(".//t:Exec/t:Command"),
            "arguments": text(".//t:Exec/t:Arguments", ""), "enabled": boolean(".//t:Enabled", True),
        }
