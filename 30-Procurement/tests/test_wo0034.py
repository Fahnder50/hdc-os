from pathlib import Path

import yaml

from procurement_watch.procurement_decision import automatic_order_allowed, procurement_state


ROOT = Path(__file__).resolve().parents[2]


def _case():
    return yaml.safe_load((ROOT / "30-Procurement/cases/PC-0004-Managed-Switch.yaml").read_text(encoding="utf-8"))


def _complete_offer():
    return {
        "exact_model": "TL-SG2008P V3", "new_condition": True,
        "availability": "in_stock", "item_price": 89.0, "shipping": 5.0,
        "total_price": 114.0, "vendor": "Example", "warranty": "documented",
        "power_supply": "included", "rack_accessory": "20 EUR shelf included in total",
        "poe_configuration": "4x 802.3af/at, 62 W",
    }


def test_all_architecture_gates_are_individually_present():
    profile = yaml.safe_load((ROOT / "30-Procurement/profiles/PC-0004.yaml").read_text(encoding="utf-8"))
    requirements = {item["id"]: item for item in profile["requirements"]}
    assert set(f"AG{number:02d}" for number in range(1, 11)).issubset(requirements)
    assert all(requirements[f"AG{number:02d}"]["status"] == "CONFIRMED" for number in range(1, 11))


def test_port_derivation_and_poe_decision_are_closed():
    case = _case()
    plan = case["port_plan"]
    assert sum(plan[key] for key in ("firewall_uplink", "ps5", "sky_box", "access_point", "hdc_os_host", "maintenance", "reserve")) == 8
    assert plan["minimum_physical_rj45_ports"] == 8
    assert case["poe_decision"]["option"] == "A"
    assert case["poe_decision"]["minimum_per_port_watts"] >= 30


def test_four_required_candidate_classes_and_horizon_one_recommendation():
    case = _case()
    classes = {item["decision_class"] for item in case["candidate_models"]}
    assert classes == {"economic_omada", "omada_poe", "economic_other_vendor", "stronger_reference"}
    assert case["current_horizon"] == "Horizon 1"
    assert case["decision_policy"]["recommended_model"] == "TL-SG2008P-V3"


def test_price_limits_and_manual_status_transitions():
    case = _case()
    gates = {f"AG{number:02d}": True for number in range(1, 11)}
    offer = _complete_offer()
    hard = case["budget"]["decision_hard_total_price"]
    assert procurement_state(architecture_gates={**gates, "AG03": False}, offer=offer, hard_total_price=hard) == "REJECT"
    assert procurement_state(architecture_gates=gates, offer={**offer, "shipping": None}, hard_total_price=hard) == "WAIT"
    assert procurement_state(architecture_gates=gates, offer={**offer, "total_price": hard + 1}, hard_total_price=hard) == "WAIT"
    assert procurement_state(architecture_gates=gates, offer=offer, hard_total_price=hard) == "REVIEW"
    assert procurement_state(architecture_gates=gates, offer=offer, hard_total_price=hard, owner_approved=True) == "BUY_CANDIDATE"


def test_watch_sources_cover_recommendation_and_economic_alternative():
    sources = yaml.safe_load((ROOT / "30-Procurement/config/sources.yaml").read_text(encoding="utf-8"))["sources"]
    models = {item.get("canonical_model_id") for item in sources if item.get("case_id") == "PC-0004"}
    assert {"TL-SG2008P-V3", "TL-SG2008", "GS1900-8", "SG2218"}.issubset(models)


def test_no_automatic_order_is_possible():
    assert automatic_order_allowed() is False
    assert _case()["decision_policy"]["no_automatic_order"] is True


def test_r1_access_point_cross_case_gate_is_binding():
    gate = _case()["poe_decision"]["access_point_cross_case_gate"]
    assert gate["required_standard"] == "IEEE 802.3af/at"
    assert gate["maximum_per_port_watts"] == 30
    assert gate["failure_action"] == "Re-evaluate PC-0004 before access point purchase"


def test_r1_rack_shelf_is_in_total_offer_and_asset_list():
    case = _case()
    shelf = case["budget"]["rack_shelf"]
    assert shelf["required_in_complete_offer"] is True
    assert shelf["asset_registration_required"] is True
    assert "rack_shelf_or_mounting_accessory" in case["budget"]["included_costs"]


def test_review_acceptance_metadata_is_complete():
    case = _case()
    assert case["document_status"] == "ACCEPTED"
    assert case["reviewed_by"] == "Lead Architect"
    assert str(case["last_review"]) == "2026-07-31"
