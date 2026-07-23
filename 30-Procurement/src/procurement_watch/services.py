from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import uuid

from .config import load_yaml_config
from .adapters import LiveAdapterError, collect_source
from .catalog import evidence_snapshot, product_evidence, technical_json
from .database import connect, initialize, schema_status
from .delivery import apply_purchase_window, normalize_delivery
from .evaluator import evaluate_case
from .events import emit_event
from .logging_utils import log_record
from .reporting import write_case_report


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_database(config):
    return initialize(config)


def migrate_database(config):
    return initialize(config)


def run_watch(config, simulate_failure=False):
    initialize(config)
    connection = connect(config)
    try:
        run_id = f"WR-{uuid.uuid4().hex[:12]}"
        started_at = utc_now()
        connection.execute(
            "INSERT INTO watch_runs(watch_run_id, started_at, status) VALUES (?, ?, ?)",
            (run_id, started_at, "running"),
        )
        database_run_id = connection.execute("SELECT id FROM watch_runs WHERE watch_run_id = ?", (run_id,)).fetchone()[0]
        for case in connection.execute("SELECT case_id FROM procurement_cases WHERE status NOT IN ('closed', 'cancelled')"):
            evaluate_case(connection, case["case_id"], database_run_id)
        ended_at = utc_now()
        result_status = "failed" if simulate_failure else "succeeded"
        result_message = "Controlled foundation failure." if simulate_failure else "No live sources configured; controlled foundation run completed."
        connection.execute(
            "INSERT INTO watch_run_results(watch_run_id, status, message, created_at) VALUES (?, ?, ?, ?)",
            (database_run_id, result_status, result_message, ended_at),
        )
        connection.execute(
            "UPDATE watch_runs SET ended_at = ?, status = ?, error_count = ? WHERE id = ?",
            (ended_at, result_status, int(simulate_failure), database_run_id),
        )
        connection.commit()
        active_cases = [row["case_id"] for row in connection.execute("SELECT case_id FROM procurement_cases WHERE status NOT IN ('closed', 'cancelled')")]
        for case_id in active_cases:
            write_case_report(config, case_report_data(config, case_id))
        log_record(config, "INFO", "Watch run completed", run_id=run_id)
        return {"watch_run_id": run_id, "started_at": started_at, "ended_at": ended_at, "status": result_status, "error_count": int(simulate_failure)}
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _requirement_value(connection, case_db_id, requirement_id, default=None):
    row = connection.execute(
        "SELECT value_json FROM requirements WHERE case_id = ? AND requirement_id = ?",
        (case_db_id, requirement_id),
    ).fetchone()
    return json.loads(row[0]) if row else default


def _save_live_offer(connection, normalized, case_db_id, observed_at, required_by_date, preferred_shipping_purchase_by, shipping_exception_date, watch_run_db_id, repository_root):
    now = observed_at
    product_id = normalized["product_id"]
    evidence = product_evidence(repository_root, normalized.get("model"))
    evidence_json = json.dumps(evidence_snapshot(evidence), sort_keys=True)
    technical = technical_json(evidence) if evidence else json.dumps({}, sort_keys=True)
    connection.execute(
        """
        INSERT INTO products(product_id, manufacturer, model, product_name, technical_reference, technical_json,
            model_number, ean, region_variant, outlet_type, evidence_status, evidence_json, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'candidate', ?, ?)
        ON CONFLICT(product_id) DO UPDATE SET manufacturer = excluded.manufacturer, model = excluded.model,
            product_name = excluded.product_name, technical_json = excluded.technical_json,
            model_number = excluded.model_number, ean = excluded.ean, region_variant = excluded.region_variant,
            outlet_type = excluded.outlet_type, evidence_status = excluded.evidence_status,
            evidence_json = excluded.evidence_json, updated_at = excluded.updated_at
        """,
        (product_id, normalized.get("manufacturer"), normalized.get("model"), normalized["product_name"],
         normalized.get("technical_reference"), technical, normalized.get("model"), evidence.get("ean") if evidence else None,
         evidence.get("region_variant") if evidence else None, evidence.get("outlet_type", "unknown") if evidence else "unknown",
         "curated" if evidence else "unknown", evidence_json, now, now),
    )
    product_db_id = connection.execute("SELECT id FROM products WHERE product_id = ?", (product_id,)).fetchone()[0]
    vendor_id = normalized["vendor_id"]
    connection.execute(
        """
        INSERT INTO vendors(vendor_id, name, created_at, updated_at) VALUES (?, ?, ?, ?)
        ON CONFLICT(vendor_id) DO UPDATE SET name = excluded.name, updated_at = excluded.updated_at
        """,
        (vendor_id, normalized["vendor_name"], now, now),
    )
    vendor_db_id = connection.execute("SELECT id FROM vendors WHERE vendor_id = ?", (vendor_id,)).fetchone()[0]
    delivery = normalize_delivery(normalized.get("delivery_text"), observed_at, required_by_date)
    delivery = apply_purchase_window(delivery, observed_at, preferred_shipping_purchase_by, shipping_exception_date)
    delivery["pickup_location"] = normalized.get("pickup_location")
    shipping = normalized.get("shipping")
    price_cents = _money_to_cents(normalized["price"]) if normalized.get("price") is not None else None
    shipping_cents = _money_to_cents(shipping) if shipping is not None else None
    total_cents = price_cents + shipping_cents if price_cents is not None and shipping_cents is not None else None
    connection.execute(
        """
        INSERT INTO offers(offer_id, product_id, vendor_id, source_type, source_reference, price_cents, shipping_cents,
            total_price_cents, currency, availability, delivery_note, observed_at, created_at, updated_at,
            product_url, delivery_text_raw, delivery_date_earliest, delivery_date_latest, delivery_confidence,
            delivery_eligibility, fulfillment_type, pickup_location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(offer_id) DO UPDATE SET product_id = excluded.product_id, vendor_id = excluded.vendor_id,
            source_type = excluded.source_type, source_reference = excluded.source_reference, price_cents = excluded.price_cents,
            shipping_cents = excluded.shipping_cents, total_price_cents = excluded.total_price_cents, currency = excluded.currency,
            availability = excluded.availability, delivery_note = excluded.delivery_note, observed_at = excluded.observed_at,
            updated_at = excluded.updated_at, product_url = excluded.product_url, delivery_text_raw = excluded.delivery_text_raw,
            delivery_date_earliest = excluded.delivery_date_earliest, delivery_date_latest = excluded.delivery_date_latest,
            delivery_confidence = excluded.delivery_confidence, delivery_eligibility = excluded.delivery_eligibility,
            fulfillment_type = excluded.fulfillment_type, pickup_location = excluded.pickup_location
        """,
        (normalized["offer_id"], product_db_id, vendor_db_id, normalized.get("source_type", "live"), normalized.get("source_reference"),
         price_cents, shipping_cents, total_cents, normalized.get("currency", "EUR"), normalized.get("availability"),
         normalized.get("delivery_text"), observed_at, now, now, normalized.get("product_url"), delivery["delivery_text_raw"],
         delivery["delivery_date_earliest"], delivery["delivery_date_latest"], delivery["delivery_confidence"],
         delivery["delivery_eligibility"], delivery["fulfillment_type"], delivery["pickup_location"]),
    )
    offer_db_id = connection.execute("SELECT id FROM offers WHERE offer_id = ?", (normalized["offer_id"],)).fetchone()[0]
    observation_id = f"OBS-{uuid.uuid4().hex[:12]}"
    connection.execute(
        """
        INSERT INTO price_observations(observation_id, offer_id, price_cents, shipping_cents, total_price_cents,
            currency, availability, observed_at, source_adapter, watch_run_id, validation_status,
            delivery_text_raw, delivery_date_earliest, delivery_date_latest, delivery_confidence,
            delivery_eligibility, fulfillment_type, pickup_location, product_url, product_evidence_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'valid', ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (observation_id, offer_db_id, price_cents, shipping_cents, total_cents, normalized.get("currency", "EUR"),
         normalized.get("availability"), observed_at, normalized.get("source_type", "live"), watch_run_db_id,
         delivery["delivery_text_raw"], delivery["delivery_date_earliest"], delivery["delivery_date_latest"],
         delivery["delivery_confidence"], delivery["delivery_eligibility"], delivery["fulfillment_type"],
         delivery["pickup_location"], normalized.get("product_url"), evidence_json),
    )
    connection.execute(
        "INSERT OR IGNORE INTO case_products(case_id, product_id, status, created_at) VALUES (?, ?, 'proposed', ?)",
        (case_db_id, product_db_id, now),
    )
    return {"offer_id": normalized["offer_id"], "observation_id": observation_id, "delivery": delivery}


def run_live_watch(config, case_id):
    initialize(config)
    sources_document = load_yaml_config(config.sources_path)
    policy_document = load_yaml_config(config.policy_path) if config.policy_path.exists() else {}
    sources = [source for source in sources_document.get("sources", []) if source.get("case_id") in (None, case_id)]
    if not sources:
        raise ValueError(f"No live sources configured for case: {case_id}")
    connection = connect(config)
    run_id = f"WR-{uuid.uuid4().hex[:12]}"
    started_at = utc_now()
    successful_sources = 0
    failed_sources = 0
    offer_count = 0
    observation_count = 0
    try:
        case = connection.execute("SELECT id FROM procurement_cases WHERE case_id = ?", (case_id,)).fetchone()
        if case is None:
            raise ValueError(f"Unknown case: {case_id}")
        required_by_date = _requirement_value(connection, case[0], "required_by_date", "2026-08-03")
        preferred_shipping_purchase_by = _requirement_value(connection, case[0], "preferred_shipping_purchase_by", "2026-07-31")
        shipping_exception_date = _requirement_value(connection, case[0], "shipping_purchase_exception_date", "2026-08-01")
        timeout = float(policy_document.get("watch", {}).get("request_timeout_seconds", config.request_timeout))
        retries = int(policy_document.get("watch", {}).get("max_retries", config.max_retries))
        user_agent = policy_document.get("watch", {}).get("user_agent", config.user_agent)
        connection.execute("INSERT INTO watch_runs(watch_run_id, started_at, status) VALUES (?, ?, 'running')", (run_id, started_at))
        database_run_id = connection.execute("SELECT id FROM watch_runs WHERE watch_run_id = ?", (run_id,)).fetchone()[0]
        for source in sources:
            source_id = source.get("source_id", source.get("url", "source"))
            try:
                records = collect_source(source, timeout=timeout, user_agent=user_agent, retries=retries)
                for normalized in records:
                    saved = _save_live_offer(connection, normalized, case[0], started_at, required_by_date, preferred_shipping_purchase_by, shipping_exception_date, database_run_id, config.repository_root)
                    offer_count += 1
                    observation_count += 1
                connection.execute(
                    "INSERT INTO watch_run_results(watch_run_id, case_id, source_id, status, message, created_at, records_processed) VALUES (?, ?, ?, 'succeeded', ?, ?, ?)",
                    (database_run_id, case[0], source_id, f"Processed {len(records)} live offers.", utc_now(), len(records)),
                )
                successful_sources += 1
                log_record(config, "INFO", "Live source processed", run_id=run_id, case_id=case_id, source_id=source_id)
            except Exception as error:
                failed_sources += 1
                error_class = type(error).__name__
                connection.execute(
                    "INSERT INTO watch_run_results(watch_run_id, case_id, source_id, status, message, created_at, records_processed, error_class) VALUES (?, ?, ?, 'failed', ?, ?, 0, ?)",
                    (database_run_id, case[0], source_id, str(error), utc_now(), error_class),
                )
                emit_event(connection, case[0], "SOURCE_FAILED", f"{run_id}:source:{source_id}", f"Live source {source_id} failed: {error}")
                log_record(config, "ERROR", "Live source failed", run_id=run_id, case_id=case_id, source_id=source_id, error_class=error_class)
        evaluate_case(connection, case_id, database_run_id)
        ended_at = utc_now()
        result_status = "succeeded" if successful_sources else "failed"
        connection.execute(
            "UPDATE watch_runs SET ended_at = ?, status = ?, error_count = ? WHERE id = ?",
            (ended_at, result_status, failed_sources, database_run_id),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    write_case_report(config, case_report_data(config, case_id))
    result = case_status(config, case_id)
    return {
        "watch_run_id": run_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "status": result_status,
        "successful_sources": successful_sources,
        "failed_sources": failed_sources,
        "offers_processed": offer_count,
        "observations_saved": observation_count,
        "recommendation_status": result["recommendation_status"],
        "error_count": failed_sources,
    }


def procurement_status(config):
    result = schema_status(config)
    required_tables = {"procurement_cases", "events", "watch_runs"}
    if not result["reachable"] or not required_tables.issubset(result["tables"]):
        result.update({"initialized": False, "cases": None, "open_events": None, "last_watch_run": None})
        return result
    connection = connect(config)
    try:
        cases = connection.execute("SELECT COUNT(*) FROM procurement_cases").fetchone()[0]
        open_events = connection.execute("SELECT COUNT(*) FROM events WHERE status = 'open'").fetchone()[0]
        last_run = connection.execute(
            "SELECT watch_run_id, status, started_at, ended_at, error_count FROM watch_runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
    finally:
        connection.close()
    result.update({"initialized": True, "cases": cases, "open_events": open_events, "last_watch_run": dict(last_run) if last_run else None})
    return result


def _upsert_requirement(connection, case_db_id, requirement_id, value, status="UNKNOWN"):
    now = utc_now()
    serialized_value = json.dumps(value, default=lambda item: item.isoformat() if hasattr(item, "isoformat") else str(item))
    connection.execute(
        """
        INSERT INTO requirements(case_id, requirement_id, name, value_json, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(case_id, requirement_id) DO UPDATE SET
            name = excluded.name, value_json = excluded.value_json,
            status = excluded.status, updated_at = excluded.updated_at
        """,
        (case_db_id, requirement_id, requirement_id, serialized_value, status, now, now),
    )


def import_case(config, path):
    case_path = Path(path)
    document = load_yaml_config(case_path)
    required = ("case_id", "title", "status", "priority", "need", "budget", "requirements")
    missing = [field for field in required if field not in document]
    if missing:
        raise ValueError(f"Case missing required fields: {', '.join(missing)}")
    if not isinstance(document["requirements"], dict):
        raise ValueError("Case field requirements must be a mapping")
    initialize(config)
    connection = connect(config)
    try:
        now = utc_now()
        connection.execute(
            """
            INSERT INTO procurement_cases(case_id, title, status, priority, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(case_id) DO UPDATE SET title = excluded.title, status = excluded.status,
                priority = excluded.priority, updated_at = excluded.updated_at
            """,
            (document["case_id"], document["title"], document["status"], document["priority"], now, now),
        )
        case_db_id = connection.execute("SELECT id FROM procurement_cases WHERE case_id = ?", (document["case_id"],)).fetchone()[0]
        budget = document["budget"]
        _upsert_requirement(connection, case_db_id, "budget_currency", budget.get("currency"), "PASS")
        for policy_key in ("required_by_date", "preferred_shipping_purchase_by", "shipping_purchase_exception_date"):
            if document.get(policy_key) is not None:
                _upsert_requirement(connection, case_db_id, policy_key, document[policy_key], "PASS")
        _upsert_requirement(connection, case_db_id, "budget_target_price", budget.get("target_price"), "PASS")
        _upsert_requirement(connection, case_db_id, "budget_maximum_total_price", budget.get("maximum_total_price"), "PASS")
        _upsert_requirement(connection, case_db_id, "budget_absolute_maximum_total_price", budget.get("absolute_maximum_total_price"), "PASS")
        for requirement_id, value in document["requirements"].items():
            if isinstance(value, dict) and "value" in value:
                _upsert_requirement(connection, case_db_id, requirement_id, value["value"], value.get("status", "UNKNOWN").upper())
            else:
                _upsert_requirement(connection, case_db_id, requirement_id, value)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {"case_id": document["case_id"], "title": document["title"], "status": "imported", "source": str(case_path)}


def _money_to_cents(value):
    try:
        return int((Decimal(str(value)) * 100).quantize(Decimal("1")))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"Invalid monetary value: {value}") from error


def add_product(config, product_id, product_name, manufacturer=None, model=None, technical_reference=None, technical=None, case_id=None):
    initialize(config)
    connection = connect(config)
    try:
        now = utc_now()
        connection.execute(
            """
            INSERT INTO products(product_id, manufacturer, model, product_name, technical_reference, technical_json, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'candidate', ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET manufacturer = excluded.manufacturer, model = excluded.model,
                product_name = excluded.product_name, technical_reference = excluded.technical_reference,
                technical_json = excluded.technical_json, updated_at = excluded.updated_at
            """,
            (product_id, manufacturer, model, product_name, technical_reference, json.dumps(technical or {}), now, now),
        )
        product_db_id = connection.execute("SELECT id FROM products WHERE product_id = ?", (product_id,)).fetchone()[0]
        if case_id:
            case_db_id = connection.execute("SELECT id FROM procurement_cases WHERE case_id = ?", (case_id,)).fetchone()
            if case_db_id is None:
                raise ValueError(f"Unknown case: {case_id}")
            connection.execute(
                "INSERT OR IGNORE INTO case_products(case_id, product_id, status, created_at) VALUES (?, ?, 'proposed', ?)",
                (case_db_id[0], product_db_id, now),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {"product_id": product_id, "status": "saved"}


def add_offer(config, offer_id, product_id, vendor_id, vendor_name, price, shipping, currency, availability, source_type, source_reference=None, delivery_note=None, observed_at=None, case_id=None):
    initialize(config)
    connection = connect(config)
    try:
        now = observed_at or utc_now()
        product = connection.execute("SELECT id FROM products WHERE product_id = ?", (product_id,)).fetchone()
        if product is None:
            raise ValueError(f"Unknown product: {product_id}")
        connection.execute(
            """
            INSERT INTO vendors(vendor_id, name, created_at, updated_at) VALUES (?, ?, ?, ?)
            ON CONFLICT(vendor_id) DO UPDATE SET name = excluded.name, updated_at = excluded.updated_at
            """,
            (vendor_id, vendor_name, now, now),
        )
        vendor = connection.execute("SELECT id FROM vendors WHERE vendor_id = ?", (vendor_id,)).fetchone()
        price_cents = _money_to_cents(price)
        shipping_cents = _money_to_cents(shipping or 0)
        total_cents = price_cents + shipping_cents
        connection.execute(
            """
            INSERT INTO offers(offer_id, product_id, vendor_id, source_type, source_reference, price_cents, shipping_cents,
                total_price_cents, currency, availability, delivery_note, observed_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(offer_id) DO UPDATE SET product_id = excluded.product_id, vendor_id = excluded.vendor_id,
                source_type = excluded.source_type, source_reference = excluded.source_reference, price_cents = excluded.price_cents,
                shipping_cents = excluded.shipping_cents, total_price_cents = excluded.total_price_cents,
                currency = excluded.currency, availability = excluded.availability, delivery_note = excluded.delivery_note,
                observed_at = excluded.observed_at, updated_at = excluded.updated_at
            """,
            (offer_id, product[0], vendor[0], source_type, source_reference, price_cents, shipping_cents, total_cents, currency, availability, delivery_note, now, now, now),
        )
        offer_db_id = connection.execute("SELECT id FROM offers WHERE offer_id = ?", (offer_id,)).fetchone()[0]
        observation_id = f"OBS-{uuid.uuid4().hex[:12]}"
        connection.execute(
            """
            INSERT INTO price_observations(observation_id, offer_id, price_cents, shipping_cents, total_price_cents,
                currency, availability, observed_at, source_adapter, validation_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'valid')
            """,
            (observation_id, offer_db_id, price_cents, shipping_cents, total_cents, currency, availability, now, source_type),
        )
        if case_id:
            case_db_id = connection.execute("SELECT id FROM procurement_cases WHERE case_id = ?", (case_id,)).fetchone()
            if case_db_id is None:
                raise ValueError(f"Unknown case: {case_id}")
            connection.execute(
                "INSERT OR IGNORE INTO case_products(case_id, product_id, status, created_at) VALUES (?, ?, 'proposed', ?)",
                (case_db_id[0], product[0], now),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {"offer_id": offer_id, "observation_id": observation_id, "total_price": f"{total_cents / 100:.2f}", "currency": currency}


def offers_for_case(config, case_id):
    _require_initialized(config)
    connection = connect(config)
    try:
        rows = connection.execute(
            """
        SELECT offers.offer_id, products.product_id, products.product_name, products.model_number, products.ean,
                products.outlet_type, products.evidence_status, products.evidence_json, vendors.name AS vendor_name,
                offers.price_cents, offers.shipping_cents, offers.total_price_cents, offers.currency, offers.availability,
                offers.delivery_text_raw, offers.delivery_date_earliest, offers.delivery_date_latest,
                offers.delivery_confidence, offers.delivery_eligibility, offers.fulfillment_type,
                offers.pickup_location, offers.product_url, offers.observed_at
            FROM offers
            JOIN products ON products.id = offers.product_id
            JOIN vendors ON vendors.id = offers.vendor_id
            JOIN case_products ON case_products.product_id = products.id
            JOIN procurement_cases ON procurement_cases.id = case_products.case_id
            WHERE procurement_cases.case_id = ? AND offers.status = 'active'
            ORDER BY offers.total_price_cents
            """,
            (case_id,),
        ).fetchall()
        return [dict(row) | {
            "price": f"{row['price_cents'] / 100:.2f}" if row["price_cents"] is not None else None,
            "shipping": f"{row['shipping_cents'] / 100:.2f}" if row["shipping_cents"] is not None else None,
            "total_price": f"{row['total_price_cents'] / 100:.2f}" if row["total_price_cents"] is not None else None,
        } for row in rows]
    finally:
        connection.close()


def history_for_case(config, case_id):
    _require_initialized(config)
    connection = connect(config)
    try:
        rows = connection.execute(
            """
            SELECT offers.offer_id, price_observations.observation_id, price_observations.price_cents,
                price_observations.shipping_cents, price_observations.total_price_cents, price_observations.currency,
                price_observations.availability, price_observations.observed_at, price_observations.source_adapter,
                price_observations.delivery_text_raw, price_observations.delivery_date_earliest,
                price_observations.delivery_date_latest, price_observations.delivery_confidence,
                price_observations.delivery_eligibility, price_observations.fulfillment_type,
                price_observations.pickup_location, price_observations.product_url
            FROM price_observations
            JOIN offers ON offers.id = price_observations.offer_id
            JOIN case_products ON case_products.product_id = offers.product_id
            JOIN procurement_cases ON procurement_cases.id = case_products.case_id
            WHERE procurement_cases.case_id = ?
            ORDER BY price_observations.observed_at
            """,
            (case_id,),
        ).fetchall()
        return [dict(row) | {
            "price": f"{row['price_cents'] / 100:.2f}" if row["price_cents"] is not None else None,
            "shipping": f"{row['shipping_cents'] / 100:.2f}" if row["shipping_cents"] is not None else None,
            "total_price": f"{row['total_price_cents'] / 100:.2f}" if row["total_price_cents"] is not None else None,
        } for row in rows]
    finally:
        connection.close()


def case_status(config, case_id):
    _require_initialized(config)
    connection = connect(config)
    try:
        case = connection.execute("SELECT * FROM procurement_cases WHERE case_id = ?", (case_id,)).fetchone()
        if case is None:
            raise ValueError(f"Unknown case: {case_id}")
        product_count = connection.execute("SELECT COUNT(*) FROM case_products WHERE case_id = ?", (case["id"],)).fetchone()[0]
        offer_count = connection.execute(
            "SELECT COUNT(*) FROM offers JOIN case_products ON case_products.product_id = offers.product_id WHERE case_products.case_id = ? AND offers.status = 'active'",
            (case["id"],),
        ).fetchone()[0]
        budget = connection.execute("SELECT value_json FROM requirements WHERE case_id = ? AND requirement_id = 'budget_maximum_total_price'", (case["id"],)).fetchone()
        budget_cents = int(json.loads(budget[0]) * 100) if budget else None
        cheapest = connection.execute(
            "SELECT MIN(total_price_cents) FROM offers JOIN case_products ON case_products.product_id = offers.product_id WHERE case_products.case_id = ? AND offers.status = 'active' AND offers.availability IN ('available', 'in_stock', 'instock', 'in stock')",
            (case["id"],),
        ).fetchone()[0]
        evaluations = connection.execute(
            """
            SELECT evaluations.offer_id, evaluations.rule_id, evaluations.result
            FROM evaluations
            JOIN offers ON offers.id = evaluations.offer_id
            JOIN case_products ON case_products.product_id = offers.product_id
            WHERE case_products.case_id = ?
            ORDER BY evaluations.evaluated_at
            """,
            (case["id"],),
        ).fetchall()
        latest_evaluations = {(row["offer_id"], row["rule_id"]): row["result"] for row in evaluations}
        offer_results = {}
        for (offer_id, rule_id), result in latest_evaluations.items():
            offer_results.setdefault(offer_id, {})[rule_id] = result
        live_mode = bool(connection.execute(
            "SELECT 1 FROM offers JOIN case_products ON case_products.product_id = offers.product_id WHERE case_products.case_id = ? AND offers.source_type = 'geizhals' LIMIT 1",
            (case["id"],),
        ).fetchone())
        conditional_buy = []
        if live_mode:
            for offer_id, values in offer_results.items():
                if values.get("PRODUCT_AVAILABLE") == "PASS" and values.get("DELIVERY_ELIGIBILITY") == "PASS" and not any(value == "FAIL" for value in values.values()):
                    offer_reference = connection.execute("SELECT offer_id FROM offers WHERE id = ?", (offer_id,)).fetchone()
                    conditional_buy.append(offer_reference[0] if offer_reference else offer_id)
        if product_count == 0:
            recommendation = "NO_CANDIDATE"
        elif offer_count == 0 or not offer_results:
            recommendation = "EVALUATING"
        elif any(result in {"FAIL", "REVIEW"} for values in offer_results.values() for result in values.values()):
            recommendation = "REVIEW"
        elif conditional_buy:
            recommendation = "CONDITIONAL_BUY"
        elif any(result == "UNKNOWN" for values in offer_results.values() for result in values.values()):
            recommendation = "WAIT"
        elif any(set(values.values()) == {"PASS"} and len(values) >= (19 if live_mode else 7) for values in offer_results.values()) and cheapest is not None and (budget_cents is None or cheapest <= budget_cents):
            recommendation = "BUY_CANDIDATE"
        else:
            recommendation = "EVALUATING"
        required_open = [row[0] for row in connection.execute("SELECT requirement_id FROM requirements WHERE case_id = ? AND status IN ('OPEN', 'UNKNOWN')", (case["id"],)).fetchall()]
        warnings = [f"{key[1]}: {value}" for key, value in latest_evaluations.items() if value in {"FAIL", "UNKNOWN"}]
        last_run = connection.execute("SELECT watch_run_id, status, started_at, ended_at, error_count FROM watch_runs ORDER BY started_at DESC LIMIT 1").fetchone()
        budget_compliant = connection.execute(
            "SELECT MIN(total_price_cents) FROM offers JOIN case_products ON case_products.product_id = offers.product_id WHERE case_products.case_id = ? AND offers.status = 'active' AND offers.availability IN ('available', 'in_stock', 'instock', 'in stock') AND (? IS NULL OR total_price_cents <= ?)",
            (case["id"], budget_cents, budget_cents),
        ).fetchone()[0]
        ranking_rows = connection.execute(
            """
            SELECT offers.offer_id, vendors.name AS vendor_name, offers.total_price_cents,
                offers.delivery_eligibility, offers.delivery_date_latest
            FROM offers
            JOIN vendors ON vendors.id = offers.vendor_id
            JOIN case_products ON case_products.product_id = offers.product_id
            WHERE case_products.case_id = ? AND offers.status = 'active'
            """,
            (case["id"],),
        ).fetchall()
        ranking = sorted(
            [dict(row) for row in ranking_rows],
            key=lambda row: (
                {"true": 0, "unknown": 1, "false": 2}.get(row["delivery_eligibility"], 1),
                row["total_price_cents"] if row["total_price_cents"] is not None else 10**12,
                row["delivery_date_latest"] or "9999-12-31",
                row["vendor_name"],
            ),
        )
        for index, row in enumerate(ranking, start=1):
            row["rank"] = index
            row["total_price"] = row["total_price_cents"] / 100 if row["total_price_cents"] is not None else None
        return {
            "case_id": case["case_id"], "title": case["title"], "priority": case["priority"],
            "budget": budget_cents / 100 if budget_cents is not None else None,
            "product_candidates": product_count, "active_offers": offer_count,
            "cheapest_available_offer": cheapest / 100 if cheapest is not None else None,
            "cheapest_budget_compliant_offer": budget_compliant / 100 if budget_compliant is not None else None,
            "open_required_requirements": required_open,
            "warnings": warnings,
            "last_watch_run": dict(last_run) if last_run else None,
            "recommendation_status": recommendation,
            "conditional_buy_offers": conditional_buy,
            "purchase_conditions": [
                "Versandkosten und Endpreis im Checkout bestätigen; unbekannte Versandkosten sind vorläufig.",
                "Für IEC-C13-Varianten je Gerät ein passendes IEC-C13-auf-Schuko-Kabel einplanen.",
                "Die gewünschte Laufzeit von 4 Stunden ist mit den vorliegenden Modellnachweisen noch nicht belegt.",
            ] if recommendation == "CONDITIONAL_BUY" else [],
            "ranking": ranking,
        }
    finally:
        connection.close()


def _require_initialized(config):
    result = schema_status(config)
    required_tables = {"procurement_cases", "offers", "price_observations"}
    if not result["reachable"] or not required_tables.issubset(result["tables"]):
        raise ValueError("Procurement database is not initialized; run 'db init' first.")


def case_report_data(config, case_id):
    _require_initialized(config)
    connection = connect(config)
    try:
        case = connection.execute("SELECT id FROM procurement_cases WHERE case_id = ?", (case_id,)).fetchone()
        if case is None:
            raise ValueError(f"Unknown case: {case_id}")
        evaluations = connection.execute(
            "SELECT rule_id, result, reason, evaluated_at FROM evaluations WHERE case_id = ? ORDER BY evaluated_at DESC",
            (case[0],),
        ).fetchall()
        events = connection.execute(
            "SELECT event_type, severity, status, message, created_at FROM events WHERE case_id = ? ORDER BY created_at DESC",
            (case[0],),
        ).fetchall()
        watch_runs = connection.execute(
            "SELECT watch_run_id, status, started_at, ended_at, error_count FROM watch_runs ORDER BY started_at DESC LIMIT 20"
        ).fetchall()
        return {
            "status": case_status(config, case_id),
            "offers": offers_for_case(config, case_id),
            "history": history_for_case(config, case_id),
            "evaluations": [dict(row) for row in evaluations],
            "events": [dict(row) for row in events],
            "watch_runs": [dict(row) for row in watch_runs],
        }
    finally:
        connection.close()


def report_case(config, case_id):
    return write_case_report(config, case_report_data(config, case_id))


def current_events(config):
    result = schema_status(config)
    if not result["reachable"]:
        return {"initialized": False, "events": []}
    connection = connect(config)
    try:
        rows = connection.execute("SELECT event_id, event_type, severity, status, message, created_at FROM events WHERE status = 'open' ORDER BY created_at DESC").fetchall()
        return {"initialized": True, "events": [dict(row) for row in rows]}
    finally:
        connection.close()


def recent_watch_runs(config):
    result = schema_status(config)
    if not result["reachable"]:
        return {"initialized": False, "runs": []}
    connection = connect(config)
    try:
        rows = connection.execute("SELECT watch_run_id, status, started_at, ended_at, error_count FROM watch_runs ORDER BY started_at DESC LIMIT 20").fetchall()
        return {"initialized": True, "runs": [dict(row) for row in rows]}
    finally:
        connection.close()


def doctor(config):
    import sys

    db = schema_status(config)
    checks = {
        "python": {"ok": sys.version_info >= (3, 12), "detail": sys.version.split()[0]},
        "database": {"ok": db["reachable"], "detail": db["path"]},
        "schema": {"ok": db["schema_version"] == "005", "detail": db["schema_version"]},
        "logs_path": {"ok": config.logs_path.parent.exists(), "detail": str(config.logs_path)},
        "reports_path": {"ok": config.reports_path.parent.exists(), "detail": str(config.reports_path)},
        "sources": {"ok": config.sources_path.exists(), "detail": str(config.sources_path)},
    }
    return {"ok": all(check["ok"] for check in checks.values()), "checks": checks, "database": db}
