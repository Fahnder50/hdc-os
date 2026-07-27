from pathlib import Path

from procurement_watch.config import resolve_config
from procurement_watch.services import import_case, report_case, case_status
from procurement_watch.decision_summary_adapter import build_procurement_decision_summary


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_decision_summary_shows_target_date_and_delivery_buffer():
    rendered = build_procurement_decision_summary({
        "recommendation_status": "CONDITIONAL_BUY",
        "active_offers": 1,
        "best_observed_price": 49.0,
        "budget_status": "WITHIN_TARGET_BUDGET",
        "target_date": "2026-08-04",
        "earliest_observed_delivery": "2026-07-29",
        "ranking": [],
        "warnings": [],
    })
    assert "04.08.2026" in rendered
    assert "29.07.2026" in rendered
    assert "Puffer: 6 Tage" in rendered
    assert "Lieferpuffer unter 2 Tage" in rendered


def test_decision_summary_deduplicates_technical_facts_and_risks():
    rendered = build_procurement_decision_summary({
        "recommendation_status": "REVIEW",
        "warnings": [
            "RUNTIME_TARGET_DOCUMENTED: UNKNOWN",
            "RUNTIME_TARGET_DOCUMENTED: UNKNOWN",
            "NUT_COMPATIBLE_DOCUMENTED: UNKNOWN",
            "NUT_COMPATIBLE_DOCUMENTED: UNKNOWN",
            "DELIVERY_ELIGIBILITY: UNKNOWN",
            "DELIVERY_ELIGIBILITY: UNKNOWN",
        ],
        "ranking": [],
    })
    assert "2 offene Sachverhalte" in rendered
    assert "2 offene Sachverhalte" in rendered
    assert rendered.count("Die Ziel-Laufzeit") == 1
    assert rendered.count("Die Lieferbarkeit") == 1


def test_decision_summary_separates_engine_status_and_action():
    rendered = build_procurement_decision_summary({
        "recommendation_status": "CONDITIONAL_BUY",
        "warnings": [],
        "ranking": [],
    })
    assert "Engine-Status:</strong> CONDITIONAL_BUY" in rendered
    assert "Handlungsempfehlung: NOCH WARTEN" in rendered


def test_decision_summary_keeps_budget_codes_out_of_risk_dimension():
    rendered = build_procurement_decision_summary({
        "recommendation_status": "CONDITIONAL_BUY",
        "budget_status": "WITHIN_TARGET_BUDGET",
        "active_offers": 1,
        "warnings": [
            "WITHIN_TARGET_BUDGET: PASS",
            "WITHIN_MAXIMUM_BUDGET: PASS",
            "OVER_MAXIMUM_BUDGET: UNKNOWN",
            "RUNTIME_TARGET_DOCUMENTED: UNKNOWN",
        ],
        "target_date": "2026-08-04",
        "earliest_observed_delivery": "2026-07-29",
    })
    risk_section = rendered.split("<th>Risiko</th>", 1)[1].split("</tr>", 1)[0]
    assert "WITHIN_TARGET_BUDGET" not in risk_section
    assert "WITHIN_MAXIMUM_BUDGET" not in risk_section
    assert "OVER_MAXIMUM_BUDGET" not in risk_section
    assert "Budget: Innerhalb Zielbudget." in rendered


def test_decision_summary_reasons_match_change_conditions():
    rendered = build_procurement_decision_summary({
        "recommendation_status": "CONDITIONAL_BUY",
        "budget_status": "WITHIN_MAXIMUM_BUDGET",
        "active_offers": 1,
        "warnings": ["RUNTIME_TARGET_DOCUMENTED: UNKNOWN"],
        "target_date": "2026-08-04",
        "earliest_observed_delivery": "2026-07-29",
    })
    assert "Budget: Über Zielbudget, aber zulässig." in rendered
    assert "Kaufkritische Technik bleibt offen" in rendered
    assert "Lieferung vor Zieltermin" in rendered
    assert "Zeit: Früheste Lieferung vor dem Zieltermin mit 6 Tagen Puffer." in rendered
    assert "Wenn der Endpreis innerhalb des Zielbudgets liegt" in rendered
    assert "Wenn die offenen kaufkritischen technischen Sachverhalte" in rendered
    assert "Wenn der Lieferpuffer unter 2 Tage fällt" in rendered


def test_decision_summary_shows_checkout_and_runtime_risks():
    rendered = build_procurement_decision_summary({
        "recommendation_status": "CONDITIONAL_BUY",
        "budget_status": "WITHIN_TARGET_BUDGET",
        "warnings": ["RUNTIME_TARGET_DOCUMENTED: UNKNOWN"],
        "purchase_conditions": ["Versandkosten und Endpreis im Checkout bestätigen."],
        "target_date": "2026-08-04",
        "earliest_observed_delivery": "2026-07-29",
    })
    risk_section = rendered.split("<th>Risiko</th>", 1)[1].split("</tr>", 1)[0]
    assert "Keine bekannten Risiken" not in risk_section
    assert "Ziel-Laufzeit" in risk_section
    assert "Versandkosten und Endpreis" in risk_section
    assert "auswertbare Angebote" not in rendered.split("<h3>Warum?</h3>", 1)[1].split("<h3>", 1)[0]


def test_pc001_productive_report_contains_all_decision_dimensions(tmp_path):
    config = resolve_config(
        environ={
            "HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db"),
            "HDC_PROCUREMENT_REPORTS": str(tmp_path / "reports"),
        },
        repository_root=REPO_ROOT,
    )
    import_case(config, REPO_ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    status = case_status(config, "PC-0001")
    assert status["target_date"] == "2026-08-04"
    report = report_case(config, "PC-0001").read_text(encoding="utf-8")
    assert all(f"<th>{dimension}</th>" in report for dimension in ("Markt", "Budget", "Technik", "Zeit", "Risiko"))
    assert "04.08.2026" in report
    assert "{{" not in report
