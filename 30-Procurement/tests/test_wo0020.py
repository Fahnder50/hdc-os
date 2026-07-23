import sqlite3
from pathlib import Path

from procurement_watch.journal import changes_since, record_entry


def test_journal_first_run_and_price_change_are_retained():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript("""
        CREATE TABLE journal_entries (
            id INTEGER PRIMARY KEY, case_id INTEGER, watch_run_id INTEGER, entry_id TEXT UNIQUE,
            observed_at TEXT, recommendation_status TEXT, summary_json TEXT, changes_json TEXT, created_at TEXT
        );
    """)
    first = {"status": {"recommendation_status": "CONDITIONAL_BUY", "active_offers": 1}, "offers": [{"offer_id": "O1", "model_number": "BX750MI", "vendor_name": "Office Partner", "price": "89.00", "delivery_date_latest": "2026-07-27", "delivery_eligibility": "true"}], "events": []}
    second = {"status": {"recommendation_status": "CONDITIONAL_BUY", "active_offers": 1}, "offers": [{"offer_id": "O1", "model_number": "BX750MI", "vendor_name": "Office Partner", "price": "88.00", "delivery_date_latest": "2026-07-27", "delivery_eligibility": "true"}], "events": []}
    record_entry(connection, 1, 1, "2026-07-23T10:00:00+00:00", {"status": first["status"], "offers": first["offers"], "events": [] , "history": [], "evaluations": []})
    changes = changes_since({"offers": [{"offer_id": "O1", "model": "BX750MI", "vendor": "Office Partner", "price": 89.0, "delivery": "2026-07-27", "delivery_eligibility": "true"}], "events": []}, {"offers": [{"offer_id": "O1", "model": "BX750MI", "vendor": "Office Partner", "price": 88.0, "delivery": "2026-07-27", "delivery_eligibility": "true"}], "events": []})
    assert changes["price_changes"][0]["after"] == 88.0
    record_entry(connection, 1, 2, "2026-07-24T10:00:00+00:00", {"status": second["status"], "offers": second["offers"], "events": [] , "history": [], "evaluations": []})
    assert connection.execute("SELECT COUNT(*) FROM journal_entries").fetchone()[0] == 2
