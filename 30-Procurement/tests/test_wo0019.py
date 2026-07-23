import json
from pathlib import Path

import procurement_watch.services as services_module
from procurement_watch.adapters import parse_geizhals
from procurement_watch.config import resolve_config
from procurement_watch.delivery import apply_purchase_window, normalize_delivery
from procurement_watch.services import import_case, run_live_watch


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_delivery_normalization_covers_deadline_relative_range_and_unknown():
    assert normalize_delivery("Lieferung bis 03.08.2026", "2026-07-23T10:00:00+00:00", "2026-08-03")["delivery_eligibility"] == "true"
    assert normalize_delivery("Lieferung bis 04.08.2026", "2026-07-23T10:00:00+00:00", "2026-08-03")["delivery_eligibility"] == "false"
    relative = normalize_delivery("Lieferung morgen", "2026-07-23T10:00:00+00:00", "2026-08-03")
    assert relative["delivery_date_earliest"] == "2026-07-24"
    date_range = normalize_delivery("Lieferzeit 1-2 Werktage", "2026-07-23T10:00:00+00:00", "2026-08-03")
    assert date_range["delivery_date_latest"] == "2026-07-27"
    assert normalize_delivery("Auf Lager", "2026-07-23T10:00:00+00:00", "2026-08-03")["delivery_eligibility"] == "unknown"


def test_pickup_is_an_eligible_alternative():
    result = normalize_delivery("Abholung möglich, lagernd", "2026-08-02T10:00:00+00:00", "2026-08-03")
    assert result["fulfillment_type"] == "pickup"
    assert result["delivery_eligibility"] == "true"


def test_shipping_purchase_window_is_conservative_on_august_first():
    confirmed = normalize_delivery("Lieferung bis 03.08.2026", "2026-08-01T10:00:00+00:00", "2026-08-03")
    assert apply_purchase_window(confirmed, "2026-08-01T10:00:00+00:00", "2026-07-31", "2026-08-01")["delivery_eligibility"] == "true"
    estimated = normalize_delivery("Lieferzeit 1-2 Werktage", "2026-08-01T10:00:00+00:00", "2026-08-03")
    assert apply_purchase_window(estimated, "2026-08-01T10:00:00+00:00", "2026-07-31", "2026-08-01")["delivery_eligibility"] == "unknown"


def test_geizhals_adapter_normalizes_multiple_real_offer_shapes():
    document = """
    <script>const page={product: {name: 'APC Back-UPS',}, mpn: 'BX500MI', offers: [{"raw_price":70.68,"merchant_name":"shop-a.de","delivery_time":"Lieferzeit 1-2 Werktage"},
      {"raw_price":80.00,"merchant_name":"shop-b.de","delivery_time":"Auf Lager"}
    ]}</script>
    """
    offers = parse_geizhals(document, "https://example.test/product", max_offers=5)
    assert len(offers) == 2
    assert offers[0]["vendor_name"] == "shop-a.de"
    assert offers[1]["shipping"] is None


def test_live_watch_isolates_one_source_failure_and_writes_report(monkeypatch, tmp_path):
    sources = tmp_path / "sources.yaml"
    sources.write_text(
        "sources:\n  - source_id: good\n    adapter: fixture\n    case_id: PC-0001\n    url: https://fixture/good\n  - source_id: bad\n    adapter: fixture\n    case_id: PC-0001\n    url: https://fixture/bad\n",
        encoding="utf-8",
    )
    policy = tmp_path / "policy.yaml"
    policy.write_text("watch:\n  request_timeout_seconds: 1\n  max_retries: 0\n", encoding="utf-8")
    config = resolve_config(
        environ={
            "HDC_PROCUREMENT_DB": str(tmp_path / "procurement.db"),
            "HDC_PROCUREMENT_LOGS": str(tmp_path / "logs"),
            "HDC_PROCUREMENT_REPORTS": str(tmp_path / "reports"),
            "HDC_PROCUREMENT_SOURCES": str(sources),
            "HDC_PROCUREMENT_POLICY": str(policy),
        },
        repository_root=REPO_ROOT,
    )
    import_case(config, "30-Procurement/cases/PC-0001-Router-USV.yaml")

    def collect(source, **kwargs):
        if source["source_id"] == "bad":
            raise RuntimeError("fixture timeout")
        return [{
            "offer_id": "FIXTURE-OFFER-001",
            "product_id": "FIXTURE-PRODUCT-001",
            "product_name": "Fixture UPS",
            "manufacturer": "Fixture",
            "model": "F-001",
            "vendor_id": "FIXTURE-VENDOR-001",
            "vendor_name": "Fixture Vendor",
            "product_url": "https://fixture/good",
            "source_reference": "https://fixture/good",
            "source_type": "fixture",
            "price": 79.00,
            "shipping": 0,
            "currency": "EUR",
            "availability": "in_stock",
            "delivery_text": "Lieferung bis 03.08.2026",
            "technical": {},
        }]

    monkeypatch.setattr(services_module, "collect_source", collect)
    result = run_live_watch(config, "PC-0001")
    assert result["status"] == "succeeded"
    assert result["successful_sources"] == 1
    assert result["failed_sources"] == 1
    assert result["observations_saved"] == 1
    assert (config.reports_path / "PC-0001.html").exists()
