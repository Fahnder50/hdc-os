from dataclasses import dataclass

from .assets import (
    LIFECYCLE_STATES,
    AcceptanceCheck,
    Asset,
    AssetRegistry,
    AssetValidationError,
    asset_from_mapping,
)


CAPABILITIES = frozenset({
    "routing", "firewall", "vpn", "switching", "wifi", "storage",
    "compute", "virtualization", "backup", "monitoring", "power_backup",
    "management",
})
ROLES = frozenset({"Gateway", "Compute", "Storage", "Network", "Wireless", "Power", "Management", "HomeOffice"})
STATUSES = frozenset({"planned", "ordered", "available", "installed", "active", "maintenance", "offline", "retired"})

VALID_CAPABILITIES = CAPABILITIES
VALID_ROLES = ROLES
VALID_STATUSES = STATUSES


class InfrastructureValidationError(ValueError):
    """Raised when an infrastructure model violates its core contract."""


def _values(values):
    if isinstance(values, str):
        return (values,)
    return tuple(dict.fromkeys(values or ()))


@dataclass(frozen=True)
class InfrastructureComponent:
    id: str
    name: str
    roles: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    status: str = "planned"
    dependencies: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "roles", _values(self.roles))
        object.__setattr__(self, "capabilities", _values(self.capabilities))
        object.__setattr__(self, "dependencies", _values(self.dependencies))


Component = InfrastructureComponent


class Infrastructure:
    def __init__(self, components=()):
        self.components = tuple(components)
        self.validate()

    def validate(self):
        ids = [component.id for component in self.components]
        duplicate_ids = sorted({component_id for component_id in ids if ids.count(component_id) > 1})
        if duplicate_ids:
            raise InfrastructureValidationError(f"Duplicate component IDs: {', '.join(duplicate_ids)}")
        for component in self.components:
            invalid_roles = sorted(set(component.roles) - ROLES)
            if invalid_roles:
                raise InfrastructureValidationError(f"Invalid roles for {component.id}: {', '.join(invalid_roles)}")
            invalid_capabilities = sorted(set(component.capabilities) - CAPABILITIES)
            if invalid_capabilities:
                raise InfrastructureValidationError(f"Invalid capabilities for {component.id}: {', '.join(invalid_capabilities)}")
            if component.status not in STATUSES:
                raise InfrastructureValidationError(f"Invalid status for {component.id}: {component.status}")
        known_ids = set(ids)
        for component in self.components:
            unknown = sorted(set(component.dependencies) - known_ids)
            if unknown:
                raise InfrastructureValidationError(f"Unknown dependencies for {component.id}: {', '.join(unknown)}")
        self._validate_cycles()
        return self

    def _validate_cycles(self):
        dependencies = {component.id: set(component.dependencies) for component in self.components}
        visiting = set()
        visited = set()

        def visit(component_id, path):
            if component_id in visiting:
                cycle = " -> ".join(path[path.index(component_id):] + [component_id])
                raise InfrastructureValidationError(f"Cyclic dependency detected: {cycle}")
            if component_id in visited:
                return
            visiting.add(component_id)
            for dependency in dependencies[component_id]:
                visit(dependency, path + [dependency])
            visiting.remove(component_id)
            visited.add(component_id)

        for component_id in dependencies:
            visit(component_id, [component_id])

    def by_id(self, component_id):
        return next((component for component in self.components if component.id == component_id), None)


def render_status(infrastructure):
    infrastructure.validate()
    lines = ["Infrastructure Summary", "", f"Components: {len(infrastructure.components)}", ""]
    present_roles = {role for component in infrastructure.components for role in component.roles}
    for role in ("Gateway", "Network", "Storage", "Compute", "Wireless", "Power", "Management"):
        lines.extend((role, "✓" if role in present_roles else "—", ""))
    return "\n".join(lines).rstrip()


__all__ = [
    "CAPABILITIES", "ROLES", "STATUSES", "VALID_CAPABILITIES", "VALID_ROLES", "VALID_STATUSES",
    "Component", "InfrastructureComponent", "Infrastructure", "InfrastructureValidationError", "render_status",
    "LIFECYCLE_STATES", "AcceptanceCheck", "Asset", "AssetRegistry",
    "AssetValidationError", "asset_from_mapping",
]
