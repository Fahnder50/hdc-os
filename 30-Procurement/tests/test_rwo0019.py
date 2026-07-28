from pathlib import Path

from procurement_watch.config import load_yaml_config
from procurement_watch.requirements import parse_requirement_profile
from procurement_watch.decision_summary_adapter import build_procurement_decision_summary
from procurement_watch.services import add_offer, add_product, case_status, import_all_cases, import_case, report_case, run_watch


ROOT = Path(__file__).resolve().parents[2]


def _profile(case_id):
    document = load_yaml_config(ROOT / "30-Procurement" / "profiles" / f"{case_id}.yaml")
    base = load_yaml_config(ROOT / "30-Procurement" / "profiles" / "base.yaml")
    document["requirements"] = base["requirements"] + document["requirements"]
    return parse_requirement_profile(document, case_id)


def test_all_cases_have_approved_isolated_profiles():
    profiles = {case_id: _profile(case_id) for case_id in ("PC-0001", "PC-0002", "PC-0003", "PC-0004", "PC-0005")}
    assert all(profile.is_approved for profile in profiles.values())
    assert len({profile.profile_id for profile in profiles.values()}) == 5
    assert "target_runtime_hours" not in profiles["PC-0005"].confirmed_engine_keys
    assert "target_runtime_hours" in profiles["PC-0001"].confirmed_engine_keys


def test_profile_statuses_are_countable_and_non_evaluating_statuses_are_retained():
    profile = _profile("PC-0003")
    statuses = {status: sum(item["status"] == status for item in profile.requirements)
                for status in ("CONFIRMED", "PROPOSED", "OPEN", "REJECTED")}
    assert statuses["CONFIRMED"] > 0
    assert statuses["PROPOSED"] > 0
    assert statuses["OPEN"] > 0


def test_invalid_profile_requirements_are_rejected():
    try:
        parse_requirement_profile({"profile_id": "x", "name": "x", "status": "approved", "requirements": [{"id": "x"}]}, "PC-0001")
    except ValueError:
        return
    raise AssertionError("incomplete requirement profile was accepted")


def _runtime_config(tmp_path):
    from procurement_watch.config import resolve_config
    return resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=ROOT)


def test_zero_price_never_ranked_or_budgeted(tmp_path):
    config = _runtime_config(tmp_path)
    import_case(config, ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    add_product(config, "ZERO-PRODUCT", "Zero", model="BX500MI", case_id="PC-0001")
    result = add_offer(config, "ZERO-OFFER", "ZERO-PRODUCT", "ZERO-VENDOR", "Zero", "0", "0", "EUR", "in_stock", "manual", case_id="PC-0001")
    status = case_status(config, "PC-0001")
    assert result["validation_status"] == "quarantined"
    assert status["active_offers"] == 0
    assert status["best_observed_price"] is None


def test_missing_price_never_recommended(tmp_path):
    config = _runtime_config(tmp_path)
    import_case(config, ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    add_product(config, "MISSING-PRODUCT", "Missing", model="BX500MI", case_id="PC-0001")
    result = add_offer(config, "MISSING-OFFER", "MISSING-PRODUCT", "MISSING-VENDOR", "Missing", None, "0", "EUR", "in_stock", "manual", case_id="PC-0001")
    assert result["validation_status"] == "quarantined"
    assert case_status(config, "PC-0001")["recommendation_status"] != "BUY_CANDIDATE"


def test_pc0001_runtime_not_verified_blocks_technical_clearance(tmp_path):
    config = _runtime_config(tmp_path)
    import_case(config, ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    add_product(config, "NO-RUNTIME", "No runtime", model="BX500MI", technical={"automatic_failover": True, "standalone_operation": True, "cloud_free_operation": True, "monitoring_capability": "local"}, case_id="PC-0001")
    add_offer(config, "NO-RUNTIME-OFFER", "NO-RUNTIME", "RUNTIME-VENDOR", "Runtime", "39.99", "0", "EUR", "in_stock", "manual", case_id="PC-0001")
    run_watch(config)
    status = case_status(config, "PC-0001")
    assert any("RUNTIME_TARGET_DOCUMENTED: NOT_VERIFIED" in warning for warning in status["warnings"])
    assert status["recommendation_status"] != "BUY_CANDIDATE"


def test_open_requirements_visible_but_not_blocking():
    summary = build_procurement_decision_summary({
        "case_id": "PC-0001", "recommendation_status": "BUY_CANDIDATE", "active_offers": 1,
        "budget_status": "WITHIN_TARGET_BUDGET", "best_observed_price": 40, "target_date": "2026-08-04",
        "requirement_facts": [{"title": "Lastprofil", "description": "Tatsächliche Last ist offen.", "status": "OPEN"}],
    })
    assert "Lastprofil" in summary
    assert "offene Sachverhalte" in summary


def test_unverified_confirmed_requirement_is_reported():
    summary = build_procurement_decision_summary({
        "case_id": "PC-0001", "recommendation_status": "WAIT", "active_offers": 1,
        "budget_status": "WITHIN_TARGET_BUDGET", "best_observed_price": 40,
        "warnings": ["RUNTIME_TARGET_DOCUMENTED: NOT_VERIFIED"], "target_date": "2026-08-04",
    })
    assert "Ziel-Laufzeit" in summary
    assert "Kaufkritische Technik bleibt offen" in summary


def test_missing_target_date_has_no_before_or_after_classification():
    summary = build_procurement_decision_summary({
        "case_id": "PC-0001", "recommendation_status": "WAIT", "active_offers": 1,
        "budget_status": "NO_OFFER", "best_observed_price": None, "ranking": [{"delivery_date_latest": "2026-08-01"}],
    })
    assert "Zeitbewertung nicht möglich" in summary
    assert "Puffer nicht berechenbar" in summary
    assert "BEFORE_TARGET" not in summary and "AFTER_TARGET" not in summary


def test_report_never_renders_none_days(tmp_path):
    config = _runtime_config(tmp_path)
    import_case(config, ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    report = report_case(config, "PC-0001").read_text(encoding="utf-8")
    assert "None Tage" not in report


def test_pc0002_profile_survives_runtime_rebuild(tmp_path):
    config = _runtime_config(tmp_path)
    assert import_all_cases(config)["count"] == 5
    assert case_status(config, "PC-0002")["requirement_profile_status"] == "Freigegeben"
    assert "PC-0002-rolling-network-cabinet" in report_case(config, "PC-0002").read_text(encoding="utf-8")


def test_all_five_reports_have_approved_profile(tmp_path):
    config = _runtime_config(tmp_path)
    import_all_cases(config)
    for case_id in ("PC-0001", "PC-0002", "PC-0003", "PC-0004", "PC-0005"):
        report = report_case(config, case_id).read_text(encoding="utf-8")
        assert "Requirement Profile: Freigegeben" in report


def test_pc0001_four_hour_requirement_rendered_not_verified(tmp_path):
    config = _runtime_config(tmp_path)
    import_case(config, ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    add_product(config, "NO-RUNTIME-REPORT", "No runtime", model="BX500MI", case_id="PC-0001")
    add_offer(config, "NO-RUNTIME-REPORT-OFFER", "NO-RUNTIME-REPORT", "RUNTIME-REPORT-VENDOR", "Runtime", "39.99", "0", "EUR", "in_stock", "manual", case_id="PC-0001")
    run_watch(config)
    report = report_case(config, "PC-0001").read_text(encoding="utf-8")
    assert "NOT_VERIFIED" in report


def test_pc0001_missing_runtime_evidence_is_blocking(tmp_path):
    config = _runtime_config(tmp_path)
    import_case(config, ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    add_product(config, "NO-RUNTIME-BLOCK", "No runtime", model="BX500MI", case_id="PC-0001")
    add_offer(config, "NO-RUNTIME-BLOCK-OFFER", "NO-RUNTIME-BLOCK", "RUNTIME-BLOCK-VENDOR", "Runtime", "39.99", "0", "EUR", "in_stock", "manual", case_id="PC-0001")
    run_watch(config)
    report = report_case(config, "PC-0001").read_text(encoding="utf-8")
    assert "kaufblockierend" in report
    assert case_status(config, "PC-0001")["recommendation_status"] != "BUY_CANDIDATE"


def test_no_candidate_report_explains_candidate_exclusion(tmp_path):
    config = _runtime_config(tmp_path)
    import_case(config, ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    report = report_case(config, "PC-0001").read_text(encoding="utf-8")
    assert case_status(config, "PC-0001")["recommendation_status"] == "NO_CANDIDATE"
    assert "Kein passendes Kandidatenangebot" in report
