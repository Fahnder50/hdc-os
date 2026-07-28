import inspect

import pytest

from shared.infrastructure import (
    CAPABILITIES,
    ROLES,
    STATUSES,
    Infrastructure,
    InfrastructureComponent,
    InfrastructureValidationError,
    render_status,
)


def component(component_id="gateway", **overrides):
    values = {
        "id": component_id,
        "name": "Infrastructure Component",
        "roles": ("Gateway",),
        "capabilities": ("routing",),
        "status": "planned",
        "dependencies": (),
    }
    values.update(overrides)
    return InfrastructureComponent(**values)


def test_valid_roles_capabilities_and_statuses():
    for status in STATUSES:
        model = Infrastructure([component(status=status)])
        assert model.components[0].status == status
    assert "Gateway" in ROLES
    assert "routing" in CAPABILITIES


def test_invalid_role_capability_and_status_are_rejected():
    with pytest.raises(InfrastructureValidationError, match="Invalid roles"):
        Infrastructure([component(roles=("Unknown",))])
    with pytest.raises(InfrastructureValidationError, match="Invalid capabilities"):
        Infrastructure([component(capabilities=("unknown",))])
    with pytest.raises(InfrastructureValidationError, match="Invalid status"):
        Infrastructure([component(status="unknown")])


def test_linear_and_branched_dependencies_are_valid():
    model = Infrastructure([
        component("ups", roles=("Power",), capabilities=("power_backup",)),
        component("switch", roles=("Network",), capabilities=("switching",), dependencies=("ups",)),
        component("firewall", roles=("Gateway",), capabilities=("routing", "firewall"), dependencies=("switch", "ups")),
    ])
    assert model.by_id("firewall").dependencies == ("switch", "ups")


def test_cyclic_and_unknown_dependencies_are_rejected():
    with pytest.raises(InfrastructureValidationError, match="Cyclic dependency"):
        Infrastructure([component("a", dependencies=("b",)), component("b", dependencies=("a",))])
    with pytest.raises(InfrastructureValidationError, match="Unknown dependencies"):
        Infrastructure([component(dependencies=("missing",))])


def test_duplicate_ids_and_multiple_roles_capabilities_are_supported():
    with pytest.raises(InfrastructureValidationError, match="Duplicate component IDs"):
        Infrastructure([component(), component()])
    model = Infrastructure([component(roles=("Gateway", "HomeOffice"), capabilities=("routing", "vpn"))])
    assert len(model.components[0].roles) == 2
    assert len(model.components[0].capabilities) == 2


def test_report_empty_and_complete_model_contains_only_infrastructure_state():
    empty_report = render_status(Infrastructure())
    complete_report = render_status(Infrastructure([
        component("gateway", roles=("Gateway",)),
        component("switch", roles=("Network",)),
        component("nas", roles=("Storage",)),
        component("server", roles=("Compute",)),
        component("ap", roles=("Wireless",)),
        component("ups", roles=("Power",)),
        component("management", roles=("Management",)),
    ]))
    assert "Components: 0" in empty_report
    assert "Components: 7" in complete_report
    assert "Procurement" not in complete_report
    assert "€" not in complete_report
    assert "Gateway\n✓" in complete_report


def test_shared_core_has_no_hdc_service_imports():
    source = inspect.getsource(__import__("shared.infrastructure", fromlist=["Infrastructure"]))
    import_lines = "\n".join(line for line in source.splitlines() if line.startswith(("import ", "from ")))
    assert "procurement_watch" not in import_lines
    assert "monitoring" not in import_lines.lower()
    assert "deployment" not in import_lines.lower()
    assert "backup" not in import_lines.lower()
