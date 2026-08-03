from pathlib import Path
import inspect

import pytest
import yaml

from shared.assets import (
    LIFECYCLE_STATES,
    PENDING_VALUE,
    AcceptanceCheck,
    Asset,
    AssetRegistry,
    AssetValidationError,
    asset_from_mapping,
)


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "20-Operations/assets"


def make_asset(asset_id="A", **overrides):
    values = dict(
        asset_id=asset_id, asset_class="custom", manufacturer="Vendor",
        model="Model", serial_number="S1", purchase_date="2026-08-03",
        warranty_end="2028-08-03", location="Site", room="Room",
        infrastructure="network", mounted_in_rack=False,
    )
    values.update(overrides)
    return Asset(**values)


def passed_acceptance():
    return AcceptanceCheck(
        model_correct=True, packaging_undamaged=True, serial_present=True,
        accessories_complete=True, documentation_present=True,
        functional_tests=("battery_transfer",), functional_test_passed=True,
        accepted_by="Lead Architect", accepted_on="2026-08-03",
    )


def test_lifecycle_has_exact_states_and_only_forward_transitions():
    assert LIFECYCLE_STATES == (
        "PLANNED", "ORDERED", "DELIVERED", "ACCEPTANCE", "PRODUCTION",
        "MAINTENANCE", "RETIRED",
    )
    asset = make_asset()
    for state in LIFECYCLE_STATES[1:4]:
        asset = asset.transition(state, transition_date="2026-08-03")
    asset = asset.transition("PRODUCTION", acceptance=passed_acceptance(), transition_date="2026-08-03")
    asset = asset.transition("MAINTENANCE")
    asset = asset.transition("RETIRED", transition_date="2029-01-01")
    assert asset.retirement_date == "2029-01-01"
    with pytest.raises(AssetValidationError, match="Invalid lifecycle transition"):
        make_asset().transition("PRODUCTION")


def test_registry_lookup_and_generic_classes():
    registry = AssetRegistry(asset_classes={"custom"}, assets=[make_asset()])
    assert registry.lookup("A").model == "Model"
    assert registry.lookup("missing") is None
    extra = make_asset("B", asset_class="new_class")
    expanded = AssetRegistry(asset_classes={"custom", "new_class"}, assets=[*registry.assets, extra])
    assert expanded.lookup("B") == extra


def test_relationships_dependency_graph_and_power_graph():
    ups = make_asset("ups", powers=("router",))
    router = make_asset("router", powered_by=("ups",), depends_on=("ups",))
    registry = AssetRegistry(asset_classes={"custom"}, assets=[ups, router])
    assert registry.relationships("router")["powered_by"] == ("ups",)
    assert registry.dependency_graph() == {"ups": (), "router": ("ups",)}
    assert registry.power_graph()["ups"] == ("router",)


def test_unknown_relationships_and_dependency_cycles_are_rejected():
    with pytest.raises(AssetValidationError, match="Unknown relationships"):
        AssetRegistry(asset_classes={"custom"}, assets=[make_asset(depends_on=("missing",))])
    with pytest.raises(AssetValidationError, match="Cyclic asset dependency"):
        AssetRegistry(asset_classes={"custom"}, assets=[
            make_asset("a", depends_on=("b",)), make_asset("b", depends_on=("a",)),
        ])


def test_gateway_and_rack_infrastructure_are_strictly_separated():
    gateway = make_asset(infrastructure="gateway", mounted_in_rack=False)
    rack = make_asset("rack", infrastructure="rack", mounted_in_rack=True)
    assert not gateway.mounted_in_rack and rack.mounted_in_rack
    with pytest.raises(AssetValidationError, match="Gateway infrastructure"):
        make_asset(infrastructure="gateway", mounted_in_rack=True)
    with pytest.raises(AssetValidationError, match="Rack infrastructure"):
        make_asset(infrastructure="rack", mounted_in_rack=False)


def test_acceptance_blocks_production_until_every_phase_passes():
    asset = make_asset(status="ACCEPTANCE")
    with pytest.raises(AssetValidationError, match="successful asset acceptance"):
        asset.transition("PRODUCTION", acceptance=AcceptanceCheck())
    production = asset.transition("PRODUCTION", acceptance=passed_acceptance(), transition_date="2026-08-03")
    assert production.status == "PRODUCTION"
    assert production.acceptance_date == "2026-08-03"
    assert production.production_date == "2026-08-03"


def test_router_ups_is_registered_in_acceptance_and_not_rack_infrastructure():
    registry_doc = yaml.safe_load((ASSETS / "registry.yaml").read_text(encoding="utf-8"))
    record_ref = registry_doc["assets"][0]["record"]
    record = yaml.safe_load((ASSETS / record_ref).read_text(encoding="utf-8"))
    record.pop("schema_version")
    blockers = record.pop("acceptance_blockers")
    asset = asset_from_mapping(record)
    classes_doc = yaml.safe_load((ASSETS / "asset-classes.yaml").read_text(encoding="utf-8"))
    classes = {item["id"] for item in classes_doc["asset_classes"]}
    registry = AssetRegistry(
        asset_classes=classes,
        external_components=registry_doc["external_components"],
        assets=[asset],
    )
    assert registry.lookup("UPS-RTR-01").status == "ACCEPTANCE"
    assert asset.infrastructure == "gateway" and asset.mounted_in_rack is False
    assert asset.powers == ("Speedport-Smart-4", "Telephone", "Elspet-Automatic-Litter-Box")
    assert blockers and not asset.acceptance.passed
    with pytest.raises(AssetValidationError, match="complete asset identity"):
        asset.transition("PRODUCTION", acceptance=passed_acceptance())
    assert PENDING_VALUE in {asset.manufacturer, asset.model, asset.serial_number}


def test_core_has_no_procurement_or_device_dependency_and_creates_no_runtime_files():
    import shared.assets as module
    source = inspect.getsource(module)
    import_lines = "\n".join(line for line in source.splitlines() if line.startswith(("import ", "from ")))
    assert "procurement_watch" not in import_lines
    assert "Eaton" not in source and "Speedport" not in source
    assert not any(path.name in {"runtime", "data", "logs"} for path in (ROOT / "20-Operations").iterdir())


def test_registry_acceptance_metadata_is_complete():
    registry = yaml.safe_load((ASSETS / "registry.yaml").read_text(encoding="utf-8"))
    assert registry["status"] == "ACCEPTED"
    assert registry["reviewed_by"] == "Lead Architect"
    assert str(registry["last_review"]) == "2026-08-03"
