import sqlite3
from pathlib import Path

import pytest

from procurement_watch.config import resolve_config
from procurement_watch.requirements import RequirementProfileError, load_requirement_profile, parse_requirement_profile
from procurement_watch.services import case_status, import_case, report_case, run_watch


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_pc001_has_one_approved_requirement_profile(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    import_case(config, REPO_ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    connection = sqlite3.connect(config.database_path)
    profile = load_requirement_profile(connection, 1)
    count = connection.execute("SELECT COUNT(*) FROM requirement_profiles WHERE case_id = 1").fetchone()[0]
    connection.close()
    assert profile is not None
    assert profile.is_approved
    assert profile.name == "Internet Gateway UPS"
    assert len(profile.requirements) >= 13
    assert case_status(config, "PC-0001")["requirement_profile_confirmed_count"] > 0
    assert count == 1
    assert case_status(config, "PC-0001")["requirement_profile_status"] == "Freigegeben"


def test_missing_profile_is_explicitly_reported_without_technical_evaluation(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    case_path = tmp_path / "missing.yaml"
    case_path.write_text((REPO_ROOT / "30-Procurement/cases/PC-0002-Rollbarer-Netzwerkschrank.yaml").read_text(encoding="utf-8").replace("requirement_profile: profiles/PC-0002.yaml\n", ""), encoding="utf-8")
    import_case(config, case_path)
    status = case_status(config, "PC-0002")
    report = report_case(config, "PC-0002").read_text(encoding="utf-8")
    assert status["requirement_profile_status"] == "Nicht definiert"
    assert status["requirement_profile_criteria_count"] == 0
    assert "Für diesen Beschaffungsfall wurde noch kein Requirement Profile freigegeben." in report
    assert "Eine technische Bewertung ist derzeit nicht möglich." in report


def test_invalid_and_foreign_profiles_are_rejected():
    with pytest.raises(RequirementProfileError, match="invalid status"):
        parse_requirement_profile({"profile_id": "p", "name": "Profile", "status": "draft", "criteria": {"x": 1}}, "PC-0001")
    with pytest.raises(RequirementProfileError, match="another case"):
        parse_requirement_profile({"case_id": "PC-0004", "profile_id": "p", "name": "Profile", "status": "approved", "criteria": {"x": 1}}, "PC-0001")


def test_profile_storage_allows_only_one_profile_per_case(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    import_case(config, REPO_ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    connection = sqlite3.connect(config.database_path)
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO requirement_profiles(case_id, profile_id, name, status, criteria_json, created_at, updated_at) VALUES (1, 'second', 'Second', 'approved', '{}', 'now', 'now')"
        )
    connection.close()


def test_cases_do_not_share_requirement_profiles(tmp_path):
    config = resolve_config(environ={"HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db")}, repository_root=REPO_ROOT)
    import_case(config, REPO_ROOT / "30-Procurement/cases/PC-0001-Router-USV.yaml")
    import_case(config, REPO_ROOT / "30-Procurement/cases/PC-0004-Managed-Switch.yaml")
    run_watch(config)
    assert case_status(config, "PC-0001")["requirement_profile_name"] == "Internet Gateway UPS"
    assert case_status(config, "PC-0004")["requirement_profile_name"] == "Managed Switch"
