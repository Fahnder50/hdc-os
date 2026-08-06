from datetime import datetime, timezone
from typing import Any, Mapping

from .contracts import SchedulerPlatform, SchedulerStatus
from .registry import configuration_hash


class SchedulerLifecycleManager:
    def __init__(self, platform: SchedulerPlatform):
        self.platform = platform

    def install(self, definition: Mapping[str, Any]):
        self.platform.apply(definition)
        return self.verify(definition)

    def update(self, definition: Mapping[str, Any]):
        self.platform.apply(definition)
        return self.verify(definition)

    def verify(self, definition: Mapping[str, Any]):
        verified_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        try:
            actual = self.platform.inspect(definition)
            if actual is None:
                status, drift = SchedulerStatus.NOT_INSTALLED, ["scheduler is not installed"]
            else:
                expected = self.platform.expected(definition)
                drift = [key for key, value in expected.items() if actual.get(key) != value]
                if drift:
                    status = SchedulerStatus.DRIFT
                elif not actual.get("enabled"):
                    status = SchedulerStatus.INSTALLED
                else:
                    status = SchedulerStatus.HEALTHY
        except Exception as error:
            status, drift = SchedulerStatus.BROKEN, [str(error)]
            actual = None
        return {
            "scheduler_id": definition["scheduler_id"], "name": definition["name"], "version": definition["version"],
            "owner": definition["owner"], "trigger": definition["trigger"], "schedule": definition["schedule"],
            "runtime": definition["runtime"], "configuration_hash": configuration_hash(definition),
            "installation_state": status.value, "last_verification": verified_at, "drift": drift, "actual": actual,
            "health": "HEALTHY" if status == SchedulerStatus.HEALTHY else "WARNING" if status in {SchedulerStatus.INSTALLED, SchedulerStatus.NOT_INSTALLED} else "CRITICAL",
        }

    def repair(self, definition: Mapping[str, Any]):
        before = self.verify(definition)
        if before["installation_state"] in {SchedulerStatus.DRIFT.value, SchedulerStatus.BROKEN.value, SchedulerStatus.NOT_INSTALLED.value, SchedulerStatus.INSTALLED.value}:
            self.platform.apply(definition)
        return {"before": before, "after": self.verify(definition)}

    def remove(self, definition: Mapping[str, Any]):
        self.platform.remove(definition)
        return self.verify(definition)
