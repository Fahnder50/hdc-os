from enum import StrEnum
from typing import Any, Mapping, Protocol


class SchedulerStatus(StrEnum):
    NOT_INSTALLED = "NOT_INSTALLED"
    INSTALLED = "INSTALLED"
    HEALTHY = "HEALTHY"
    DRIFT = "DRIFT"
    BROKEN = "BROKEN"


class SchedulerPlatform(Protocol):
    def expected(self, definition: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def inspect(self, definition: Mapping[str, Any]) -> Mapping[str, Any] | None: ...
    def apply(self, definition: Mapping[str, Any]) -> None: ...
    def remove(self, definition: Mapping[str, Any]) -> None: ...
