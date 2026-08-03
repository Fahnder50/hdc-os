"""Generic infrastructure asset lifecycle and registry.

The module is intentionally independent from procurement and device-specific code.
Asset classes are data supplied to :class:`AssetRegistry`, not core constants.
"""

from dataclasses import dataclass, replace
from datetime import date


LIFECYCLE_STATES = (
    "PLANNED", "ORDERED", "DELIVERED", "ACCEPTANCE", "PRODUCTION",
    "MAINTENANCE", "RETIRED",
)
_NEXT_STATE = dict(zip(LIFECYCLE_STATES, LIFECYCLE_STATES[1:]))
PENDING_VALUE = "PENDING_ACCEPTANCE"


class AssetValidationError(ValueError):
    """Raised when an asset or registry violates the lifecycle contract."""


def _unique(values):
    if isinstance(values, str):
        values = (values,)
    return tuple(dict.fromkeys(values or ()))


@dataclass(frozen=True)
class AcceptanceCheck:
    model_correct: bool = False
    packaging_undamaged: bool = False
    serial_present: bool = False
    accessories_complete: bool = False
    documentation_present: bool = False
    functional_tests: tuple[str, ...] = ()
    functional_test_passed: bool = False
    accepted_by: str | None = None
    accepted_on: str | None = None

    @property
    def passed(self):
        return all((
            self.model_correct, self.packaging_undamaged, self.serial_present,
            self.accessories_complete, self.documentation_present,
            bool(self.functional_tests), self.functional_test_passed,
            bool(self.accepted_by), bool(self.accepted_on),
        ))


@dataclass(frozen=True)
class Asset:
    asset_id: str
    asset_class: str
    manufacturer: str
    model: str
    serial_number: str
    purchase_date: str
    warranty_end: str
    location: str
    room: str
    infrastructure: str
    mounted_in_rack: bool
    status: str = "PLANNED"
    acceptance_date: str | None = None
    production_date: str | None = None
    retirement_date: str | None = None
    powers: tuple[str, ...] = ()
    powered_by: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    procurement_case: str | None = None
    acceptance: AcceptanceCheck | None = None

    def __post_init__(self):
        object.__setattr__(self, "powers", _unique(self.powers))
        object.__setattr__(self, "powered_by", _unique(self.powered_by))
        object.__setattr__(self, "depends_on", _unique(self.depends_on))
        if self.status not in LIFECYCLE_STATES:
            raise AssetValidationError(f"Invalid lifecycle state for {self.asset_id}: {self.status}")
        required = (
            "asset_id", "asset_class", "manufacturer", "model", "serial_number",
            "purchase_date", "warranty_end", "location", "room", "infrastructure",
        )
        missing = [field for field in required if not getattr(self, field)]
        if missing:
            raise AssetValidationError(f"Missing asset attributes for {self.asset_id}: {', '.join(missing)}")
        if self.infrastructure == "gateway" and self.mounted_in_rack:
            raise AssetValidationError("Gateway infrastructure cannot be marked as rack-mounted.")
        if self.infrastructure == "rack" and not self.mounted_in_rack:
            raise AssetValidationError("Rack infrastructure must be marked as rack-mounted.")

    @property
    def identity_complete(self):
        values = (self.manufacturer, self.model, self.serial_number, self.purchase_date, self.warranty_end)
        return all(value != PENDING_VALUE for value in values)

    def transition(self, target_status, *, acceptance=None, transition_date=None):
        expected = _NEXT_STATE.get(self.status)
        if target_status != expected:
            raise AssetValidationError(
                f"Invalid lifecycle transition for {self.asset_id}: {self.status} -> {target_status}"
            )
        effective_date = transition_date or date.today().isoformat()
        changes = {"status": target_status}
        if self.status == "ACCEPTANCE" and target_status == "PRODUCTION":
            check = acceptance or self.acceptance
            if not self.identity_complete:
                raise AssetValidationError("Production requires complete asset identity and warranty data.")
            if check is None or not check.passed:
                raise AssetValidationError("Production requires successful asset acceptance.")
            changes.update(acceptance=check, acceptance_date=check.accepted_on, production_date=effective_date)
        if target_status == "RETIRED":
            changes["retirement_date"] = effective_date
        return replace(self, **changes)


class AssetRegistry:
    def __init__(self, *, asset_classes=(), external_components=(), assets=()):
        self.asset_classes = frozenset(asset_classes)
        self.external_components = frozenset(external_components)
        self.assets = tuple(assets)
        self.validate()

    def validate(self):
        ids = [asset.asset_id for asset in self.assets]
        duplicates = sorted({asset_id for asset_id in ids if ids.count(asset_id) > 1})
        if duplicates:
            raise AssetValidationError(f"Duplicate asset IDs: {', '.join(duplicates)}")
        unknown_classes = sorted({asset.asset_class for asset in self.assets} - self.asset_classes)
        if unknown_classes:
            raise AssetValidationError(f"Unknown asset classes: {', '.join(unknown_classes)}")
        known_targets = set(ids) | set(self.external_components)
        for asset in self.assets:
            related = set(asset.powers) | set(asset.powered_by) | set(asset.depends_on)
            unknown = sorted(related - known_targets)
            if unknown:
                raise AssetValidationError(f"Unknown relationships for {asset.asset_id}: {', '.join(unknown)}")
        self._validate_dependency_cycles()
        return self

    def _validate_dependency_cycles(self):
        asset_ids = {asset.asset_id for asset in self.assets}
        graph = {asset.asset_id: set(asset.depends_on) & asset_ids for asset in self.assets}
        visiting, visited = set(), set()

        def visit(asset_id, path):
            if asset_id in visiting:
                raise AssetValidationError(f"Cyclic asset dependency: {' -> '.join(path + [asset_id])}")
            if asset_id in visited:
                return
            visiting.add(asset_id)
            for dependency in graph[asset_id]:
                visit(dependency, path + [asset_id])
            visiting.remove(asset_id)
            visited.add(asset_id)

        for asset_id in graph:
            visit(asset_id, [])

    def lookup(self, asset_id):
        return next((asset for asset in self.assets if asset.asset_id == asset_id), None)

    def relationships(self, asset_id):
        asset = self.lookup(asset_id)
        if asset is None:
            raise KeyError(asset_id)
        return {"powers": asset.powers, "powered_by": asset.powered_by, "depends_on": asset.depends_on}

    def dependency_graph(self):
        return {asset.asset_id: asset.depends_on for asset in self.assets}

    def power_graph(self):
        graph = {asset.asset_id: asset.powers for asset in self.assets}
        for asset in self.assets:
            for supplier in asset.powered_by:
                graph.setdefault(supplier, ())
                graph[supplier] = _unique((*graph[supplier], asset.asset_id))
        return graph

    def with_asset(self, asset):
        existing = [item for item in self.assets if item.asset_id != asset.asset_id]
        return AssetRegistry(
            asset_classes=self.asset_classes,
            external_components=self.external_components,
            assets=(*existing, asset),
        )


def asset_from_mapping(data):
    acceptance_data = data.get("acceptance")
    acceptance = AcceptanceCheck(**acceptance_data) if acceptance_data else None
    return Asset(**{**data, "acceptance": acceptance})


__all__ = [
    "LIFECYCLE_STATES", "PENDING_VALUE", "AcceptanceCheck", "Asset", "AssetRegistry",
    "AssetValidationError", "asset_from_mapping",
]
