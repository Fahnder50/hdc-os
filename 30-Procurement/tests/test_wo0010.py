from pathlib import Path

from procurement_watch.catalog import load_product_catalog, product_evidence
from procurement_watch.events import emit_evaluation_events


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_product_catalog_keeps_region_variants_separate():
    catalog = load_product_catalog(REPO_ROOT)
    assert catalog["BX750MI"]["outlet_type"] == "IEC C13"
    assert catalog["BX750MI-GR"]["outlet_type"] == "Schuko"
    assert catalog["BX750MI"]["ean"] != catalog["BX750MI-GR"]["ean"]
    assert product_evidence(REPO_ROOT, "BX750MI")["model_number"] == "BX750MI"


def test_unknown_catalog_values_are_not_positive_evidence():
    catalog = load_product_catalog(REPO_ROOT)
    assert catalog["BX500MI"]["technical"]["linux_monitoring"] == "unknown"
    assert catalog["BX500MI"]["technical"]["nut_compatible"] == "unknown"


def test_requirement_unknown_events_are_aggregated():
    import sqlite3

    connection = sqlite3.connect(":memory:")
    connection.executescript(
        "CREATE TABLE events (event_id TEXT, case_id INTEGER, event_type TEXT, severity TEXT, deduplication_key TEXT UNIQUE, status TEXT, message TEXT, created_at TEXT);"
    )
    for offer_id in ("offer-a", "offer-b", "offer-c"):
        emit_evaluation_events(connection, 1, offer_id, [{"rule_id": "NUT_COMPATIBLE_DOCUMENTED", "result": "UNKNOWN"}])
    assert connection.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1
