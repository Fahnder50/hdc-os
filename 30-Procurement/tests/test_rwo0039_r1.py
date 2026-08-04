from pathlib import Path
import sqlite3

import pytest
import yaml

from procurement_watch.config import resolve_config
from procurement_watch.lifecycle import CASE_STATUSES, transition_case_status, validate_case_status
from procurement_watch.services import (
    add_offer,
    add_product,
    case_status,
    history_for_case,
    import_case,
    portfolio_watch,
    transition_case,
)


ROOT = Path(__file__).resolve().parents[2]
BASE_CASE = ROOT / "30-Procurement/cases/PC-0002-Rollbarer-Netzwerkschrank.yaml"


def config(tmp_path):
    return resolve_config(
        environ={"HDC_PROCUREMENT_RUNTIME": str(tmp_path / "runtime")},
        repository_root=ROOT,
    )


def generic_case(tmp_path, case_id, *, external_reference=None):
    source = BASE_CASE.read_text(encoding="utf-8")
    source = source.replace("PC-0002", case_id, 1)
    source = "\n".join(line for line in source.splitlines() if not line.startswith("requirement_profile:")) + "\n"
    if external_reference:
        source += "external_reference:\n"
        for key, value in external_reference.items():
            source += f"  {key}: {value}\n"
    path = tmp_path / f"{case_id}.yaml"
    path.write_text(source, encoding="utf-8")
    return path


def test_closed_is_runtime_only_and_never_persistable(tmp_path):
    assert CASE_STATUSES == (
        "WATCHING", "QUALIFYING", "READY_FOR_REVIEW", "BUY_CANDIDATE",
        "PURCHASED", "CANCELLED",
    )
    with pytest.raises(ValueError):
        validate_case_status("CLOSED")
    path = generic_case(tmp_path, "TEST-CLOSED")
    path.write_text(path.read_text(encoding="utf-8").replace("status: WATCHING", "status: CLOSED", 1), encoding="utf-8")
    with pytest.raises(ValueError):
        import_case(config(tmp_path), path)

    runtime = config(tmp_path / "database-contract")
    import_case(runtime, generic_case(tmp_path, "TEST-DATABASE-CONTRACT"))
    connection = sqlite3.connect(runtime.database_path)
    with pytest.raises(sqlite3.IntegrityError, match="invalid procurement lifecycle"):
        connection.execute("UPDATE procurement_cases SET status = 'CLOSED' WHERE case_id = 'TEST-DATABASE-CONTRACT'")
    with pytest.raises(sqlite3.IntegrityError, match="invalid procurement lifecycle transition"):
        connection.execute("UPDATE procurement_cases SET status = 'BUY_CANDIDATE' WHERE case_id = 'TEST-DATABASE-CONTRACT'")
    connection.close()


@pytest.mark.parametrize(("current", "target"), [
    ("WATCHING", "BUY_CANDIDATE"),
    ("PURCHASED", "WATCHING"),
    ("CANCELLED", "WATCHING"),
    ("PURCHASED", "QUALIFYING"),
    ("CANCELLED", "BUY_CANDIDATE"),
    ("READY_FOR_REVIEW", "PURCHASED"),
])
def test_forbidden_transitions_are_rejected(current, target):
    with pytest.raises(ValueError, match="Invalid procurement lifecycle transition"):
        transition_case_status(current, target)


def test_complete_positive_and_cancellation_transition_paths():
    assert transition_case_status("WATCHING", "QUALIFYING") == "QUALIFYING"
    assert transition_case_status("QUALIFYING", "READY_FOR_REVIEW") == "READY_FOR_REVIEW"
    assert transition_case_status("READY_FOR_REVIEW", "BUY_CANDIDATE") == "BUY_CANDIDATE"
    assert transition_case_status("BUY_CANDIDATE", "PURCHASED") == "PURCHASED"
    for state in ("WATCHING", "QUALIFYING", "READY_FOR_REVIEW", "BUY_CANDIDATE"):
        assert transition_case_status(state, "CANCELLED") == "CANCELLED"


def test_swimming_goggles_complete_without_any_asset_or_operations(tmp_path):
    runtime = config(tmp_path)
    import_case(runtime, generic_case(tmp_path, "TEST-SWIMMING-GOGGLES"))
    add_product(runtime, "GOGGLES-01", "Schwimmbrille", model="GENERIC-GOGGLES", case_id="TEST-SWIMMING-GOGGLES")
    add_offer(runtime, "GOGGLES-OFFER-01", "GOGGLES-01", "SPORT-SHOP", "Sport Shop", "19.99", "0", "EUR", "in_stock", "manual", case_id="TEST-SWIMMING-GOGGLES")
    transition_case(runtime, "TEST-SWIMMING-GOGGLES", "QUALIFYING")
    transition_case(runtime, "TEST-SWIMMING-GOGGLES", "READY_FOR_REVIEW")
    transition_case(runtime, "TEST-SWIMMING-GOGGLES", "CANCELLED")
    status = case_status(runtime, "TEST-SWIMMING-GOGGLES")
    assert status["case_status"] == "CANCELLED" and status["lifecycle_status"] == "CLOSED"
    assert status["external_reference"] is None
    assert len(history_for_case(runtime, "TEST-SWIMMING-GOGGLES")) == 1
    assert portfolio_watch(runtime)["case_count"] == 0
    runtime_paths = [str(path.relative_to(tmp_path / "runtime")).lower() for path in (tmp_path / "runtime").rglob("*")]
    assert not any(token in path for path in runtime_paths for token in ("asset", "acceptance", "registry", "operations"))


def test_router_ups_asset_flow_is_external_to_procurement_core(tmp_path):
    runtime = config(tmp_path)
    reference = {"type": "external", "reference": "UPS-RTR-01"}
    import_case(runtime, generic_case(tmp_path, "TEST-ROUTER-UPS", external_reference=reference))
    for target in ("QUALIFYING", "READY_FOR_REVIEW", "BUY_CANDIDATE", "PURCHASED"):
        transition_case(runtime, "TEST-ROUTER-UPS", target)
    status = case_status(runtime, "TEST-ROUTER-UPS")
    assert status["external_reference"] == reference
    assert status["case_status"] == "PURCHASED" and status["lifecycle_status"] == "CLOSED"

    asset = yaml.safe_load((ROOT / "20-Operations/assets/records/UPS-RTR-01.yaml").read_text(encoding="utf-8"))
    assert asset["status"] == "PRODUCTION"
    assert asset["procurement_case"] == "PC-0001"
    core_source = (ROOT / "30-Procurement/src/procurement_watch/lifecycle.py").read_text(encoding="utf-8").lower()
    assert not any(word in core_source for word in ("asset", "operations", "infrastructure", "acceptance"))
