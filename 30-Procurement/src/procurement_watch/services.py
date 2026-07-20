from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import uuid

from .config import load_yaml_config
from .database import connect, initialize, schema_status
from .evaluator import evaluate_case


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
        return {"watch_run_id": run_id, "started_at": started_at, "ended_at": ended_at, "status": result_status, "error_count": int(simulate_failure)}
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


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
    connection.execute(
        """
        INSERT INTO requirements(case_id, requirement_id, name, value_json, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(case_id, requirement_id) DO UPDATE SET
            name = excluded.name, value_json = excluded.value_json,
            status = excluded.status, updated_at = excluded.updated_at
        """,
        (case_db_id, requirement_id, requirement_id, json.dumps(value), status, now, now),
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
        _upsert_requirement(connection, case_db_id, "budget_maximum_total_price", budget.get("maximum_total_price"), "PASS")
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
            SELECT offers.offer_id, products.product_id, products.product_name, vendors.name AS vendor_name,
                offers.total_price_cents, offers.currency, offers.availability, offers.observed_at
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
        return [dict(row) | {"total_price": f"{row['total_price_cents'] / 100:.2f}"} for row in rows]
    finally:
        connection.close()


def history_for_case(config, case_id):
    _require_initialized(config)
    connection = connect(config)
    try:
        rows = connection.execute(
            """
            SELECT offers.offer_id, price_observations.observation_id, price_observations.total_price_cents,
                price_observations.currency, price_observations.availability, price_observations.observed_at,
                price_observations.source_adapter
            FROM price_observations
            JOIN offers ON offers.id = price_observations.offer_id
            JOIN case_products ON case_products.product_id = offers.product_id
            JOIN procurement_cases ON procurement_cases.id = case_products.case_id
            WHERE procurement_cases.case_id = ?
            ORDER BY price_observations.observed_at
            """,
            (case_id,),
        ).fetchall()
        return [dict(row) | {"total_price": f"{row['total_price_cents'] / 100:.2f}"} for row in rows]
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
        if product_count == 0:
            recommendation = "NO_CANDIDATE"
        elif offer_count == 0 or not offer_results:
            recommendation = "EVALUATING"
        elif any(result == "FAIL" for values in offer_results.values() for result in values.values()):
            recommendation = "REVIEW"
        elif any(result == "UNKNOWN" for values in offer_results.values() for result in values.values()):
            recommendation = "WAIT"
        elif any(set(values.values()) == {"PASS"} and len(values) >= 7 for values in offer_results.values()) and cheapest is not None and (budget_cents is None or cheapest <= budget_cents):
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
        }
    finally:
        connection.close()


def _require_initialized(config):
    result = schema_status(config)
    required_tables = {"procurement_cases", "offers", "price_observations"}
    if not result["reachable"] or not required_tables.issubset(result["tables"]):
        raise ValueError("Procurement database is not initialized; run 'db init' first.")
