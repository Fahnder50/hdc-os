import sqlite3

from procurement_watch.services import import_case


def activate_case_for_engine_test(config, case_id="PC-0001"):
    """Replace a completed fixture with a fresh active test case."""
    connection = sqlite3.connect(config.database_path)
    connection.execute("DELETE FROM procurement_cases WHERE case_id = ?", (case_id,))
    connection.commit()
    connection.close()
    source = config.repository_root / "30-Procurement/cases" / "PC-0001-Router-USV.yaml"
    document = source.read_text(encoding="utf-8").replace("status: PURCHASED", "status: WATCHING", 1)
    fixture = config.runtime_path / f"{case_id}-active-test.yaml"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text(document, encoding="utf-8")
    import_case(config, fixture)
