from pathlib import Path

from shared.decision_summary import DecisionDimension, create_decision_summary, render_decision_summary
from procurement_watch.config import resolve_config
from procurement_watch.services import import_case, report_case


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_decision_summary_supports_five_procurement_dimensions():
    dimensions = [DecisionDimension(name, "ok", "detail") for name in ("Markt", "Budget", "Technik", "Zeit", "Risiko")]
    summary = create_decision_summary(dimensions, "NOCH WARTEN", ["Ein Faktor"], ["Eine Bedingung"])
    rendered = render_decision_summary(summary)
    assert rendered.count("<tr>") == 5
    assert "Handlungsempfehlung: NOCH WARTEN" in rendered
    assert "Ein Faktor" in rendered
    assert "Eine Bedingung" in rendered


def test_decision_summary_is_extensible_without_procurement_import():
    dimensions = [
        DecisionDimension("Market", "observed", "offers available"),
        DecisionDimension("Budget", "within", "target respected"),
        DecisionDimension("Custom", "open", "future module dimension"),
    ]
    summary = create_decision_summary(dimensions, "WAIT", ["Custom factor"], ["Custom factor resolved"])
    rendered = render_decision_summary(summary)
    assert "Custom" in rendered
    assert "procurement_watch" not in summary.__class__.__module__


def test_decision_summary_rejects_duplicate_dimension():
    dimensions = [DecisionDimension(name, "ok", "detail") for name in ("Markt", "Budget", "Budget")]
    try:
        create_decision_summary(dimensions, "KAUFEN", [], [])
    except ValueError as error:
        assert "uniquely named" in str(error)
    else:
        raise AssertionError("duplicate decision dimension was accepted")


def test_decision_summary_is_first_class_report_section(tmp_path):
    config = resolve_config(
        environ={
            "HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db"),
            "HDC_PROCUREMENT_REPORTS": str(tmp_path / "reports"),
        },
        repository_root=REPO_ROOT,
    )
    import_case(config, REPO_ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    report = report_case(config, "PC-0001").read_text(encoding="utf-8")
    assert report.index("Decision Summary") < report.index("Kurzübersicht")
    assert report.count("<th>Markt</th>") == 1
    assert report.count("<th>Budget</th>") == 1
    assert report.count("<th>Technik</th>") == 1
    assert report.count("<th>Zeit</th>") == 1
    assert report.count("<th>Risiko</th>") == 1
    assert "Handlungsempfehlung:" in report
    assert "Die Empfehlung würde sich ändern wenn" in report
    assert "{{" not in report
