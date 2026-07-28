import os
import subprocess
import sys
from pathlib import Path

import pytest

from procurement_watch.config import resolve_config
from procurement_watch.services import add_offer, add_product, import_case, report_case, run_watch


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_shared_import_and_live_all_work_from_src(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    import_case(config, REPO_ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    sources = tmp_path / "sources.yaml"
    sources.write_text("sources: []\n", encoding="utf-8")
    environment = os.environ.copy()
    environment.update({
        "HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db"),
        "HDC_PROCUREMENT_SOURCES": str(sources),
        "HDC_PROCUREMENT_REPORTS": str(tmp_path / "reports"),
    })
    result = subprocess.run(
        [sys.executable, "-m", "procurement_watch", "watch", "live", "--all"],
        cwd=REPO_ROOT / "30-Procurement" / "src",
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Portfolio Summary" in result.stdout


def test_watching_case_without_candidates_fails_with_clear_error(tmp_path):
    source = (REPO_ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml").read_text(encoding="utf-8")
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text(source.replace("candidate_models:\n", "candidate_models_disabled:\n", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="PC-0001 is WATCHING but defines no candidate models"):
        import_case(resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT), invalid)


def test_unknown_offer_is_quarantined_from_report_and_budget(tmp_path):
    config = resolve_config(
        environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db"), "HDC_PROCUREMENT_REPORTS": str(tmp_path / "reports")},
        repository_root=REPO_ROOT,
    )
    import_case(config, REPO_ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    add_product(config, "PROD-UNKNOWN", "Unbewertetes Produkt", model="UNKNOWN-MODEL", case_id="PC-0001")
    add_offer(config, "OFFER-UNKNOWN", "PROD-UNKNOWN", "VENDOR-UNKNOWN", "Händler", "39.99", "0", "EUR", "in_stock", "manual", case_id="PC-0001")
    run_watch(config)
    report = report_case(config, "PC-0001").read_text(encoding="utf-8")
    regular_report = report.split("Technische Details", 1)[0]
    assert "Unbewertetes Produkt" not in regular_report
    assert "OFFER-UNKNOWN" not in regular_report
    assert "Nicht zuordenbare Beobachtung" in report
    assert "39.99" not in report.split("Technische Details", 1)[0]
