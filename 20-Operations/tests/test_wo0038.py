from pathlib import Path

import yaml

from shared.assets import AssetRegistry, asset_from_mapping


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "20-Operations/assets"
ASSET = ASSETS / "records/UPS-RTR-01.yaml"
ACCEPTANCE = ASSETS / "acceptance/UPS-RTR-01.yaml"
CASE = ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml"


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_asset_identity_purchase_and_warranty_are_documented():
    asset = load_yaml(ASSET)
    protocol = load_yaml(ACCEPTANCE)
    assert asset["serial_number"] == "GE67V13292"
    assert str(asset["purchase_date"]) == "2026-07-29"
    assert protocol["known_data"]["purchase_price"] == {"amount": 127.12, "currency": "EUR"}
    assert protocol["known_data"]["product_series"] == "Eaton 3S"
    assert protocol["known_data"]["catalog_number"] == "3S850D"
    assert protocol["known_data"]["mfg_id"] == "9400-A303 Rev. 00"
    assert protocol["warranty"] == {
        "status": "Manufacturer Warranty",
        "scope": "Herstellergarantie",
        "end_date": "PENDING_CONFIRMATION",
    }


def test_acceptance_tests_pass_and_asset_is_in_production():
    asset_data = load_yaml(ASSET)
    protocol = load_yaml(ACCEPTANCE)
    core_data = {key: value for key, value in asset_data.items() if key not in {"schema_version", "acceptance_blockers"}}
    asset = asset_from_mapping(core_data)
    assert asset.status == "PRODUCTION"
    assert asset.acceptance.passed
    assert asset.acceptance_date == asset.production_date == "2026-08-04"
    assert protocol["acceptance"]["completed"] is True
    assert protocol["acceptance"]["result"] == "PASS"
    assert {test["status"] for test in protocol["tests"].values()} == {"PASS"}
    assert protocol["acceptance_blockers"] == []


def test_external_loads_remain_external_and_registry_contains_only_the_ups():
    registry_data = load_yaml(ASSETS / "registry.yaml")
    protocol = load_yaml(ACCEPTANCE)
    asset_data = load_yaml(ASSET)
    core_data = {key: value for key, value in asset_data.items() if key not in {"schema_version", "acceptance_blockers"}}
    asset = asset_from_mapping(core_data)
    classes = {item["id"] for item in load_yaml(ASSETS / "asset-classes.yaml")["asset_classes"]}
    registry = AssetRegistry(
        asset_classes=classes,
        external_components=registry_data["external_components"],
        assets=[asset],
    )
    assert {item["name"] for item in protocol["external_loads"]} == {
        "Speedport Smart 4", "Telefon", "Elspet Automatic Litter Box",
    }
    assert all(item["registered_asset"] is False for item in protocol["external_loads"])
    assert [item.asset_id for item in registry.assets] == ["UPS-RTR-01"]


def test_procurement_source_remains_purchased_and_disabled():
    case = load_yaml(CASE)
    assert case["status"] == "PURCHASED"
    assert case["watch_enabled"] is False
    assert case["recommendations_enabled"] is False
