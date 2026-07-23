from datetime import datetime, timedelta, timezone
import json
import uuid


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _price(value):
    if value is None:
        return None
    return round(float(value), 2)


def snapshot_from_report(data):
    status = data["status"]
    offers = []
    for offer in data["offers"]:
        offers.append({
            "offer_id": offer.get("offer_id"),
            "model": offer.get("model_number") or offer.get("product_name"),
            "vendor": offer.get("vendor_name"),
            "price": _price(offer.get("price")),
            "delivery": offer.get("delivery_date_latest"),
            "delivery_eligibility": offer.get("delivery_eligibility"),
        })
    return {
        "recommendation_status": status.get("recommendation_status"),
        "offers": offers,
        "active_offers": status.get("active_offers", 0),
        "events": [event.get("event_id") for event in data.get("events", [])],
    }


def changes_since(previous, current):
    if not previous:
        return {"first_run": True, "price_changes": [], "delivery_changes": [], "new_offers": [], "new_events": []}
    old_offers = {item["offer_id"]: item for item in previous.get("offers", [])}
    price_changes = []
    delivery_changes = []
    new_offers = []
    for offer in current.get("offers", []):
        old = old_offers.get(offer["offer_id"])
        if old is None:
            new_offers.append(offer["offer_id"])
            continue
        if old.get("price") != offer.get("price"):
            price_changes.append({"model": offer["model"], "vendor": offer["vendor"], "before": old.get("price"), "after": offer.get("price")})
        if old.get("delivery") != offer.get("delivery") or old.get("delivery_eligibility") != offer.get("delivery_eligibility"):
            delivery_changes.append({"model": offer["model"], "vendor": offer["vendor"], "before": old.get("delivery"), "after": offer.get("delivery")})
    return {
        "first_run": False,
        "price_changes": price_changes,
        "delivery_changes": delivery_changes,
        "new_offers": new_offers,
        "new_events": [event_id for event_id in current.get("events", []) if event_id not in previous.get("events", [])],
    }


def record_entry(connection, case_db_id, watch_run_db_id, observed_at, data):
    current = snapshot_from_report(data)
    previous_row = connection.execute(
        "SELECT summary_json FROM journal_entries WHERE case_id = ? ORDER BY observed_at DESC LIMIT 1",
        (case_db_id,),
    ).fetchone()
    previous = json.loads(previous_row[0]) if previous_row else None
    changes = changes_since(previous, current)
    connection.execute(
        """
        INSERT INTO journal_entries(entry_id, case_id, watch_run_id, observed_at,
            recommendation_status, summary_json, changes_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (f"JRN-{uuid.uuid4().hex[:12]}", case_db_id, watch_run_db_id, observed_at,
         current["recommendation_status"], _json(current), _json(changes), observed_at),
    )
    connection.commit()
    return changes


def entries_for_case(connection, case_db_id, limit=30):
    rows = connection.execute(
        "SELECT * FROM journal_entries WHERE case_id = ? ORDER BY observed_at DESC LIMIT ?",
        (case_db_id, limit),
    ).fetchall()
    return [{
        "entry_id": row["entry_id"],
        "watch_run_id": row["watch_run_id"],
        "observed_at": row["observed_at"],
        "recommendation_status": row["recommendation_status"],
        "summary": json.loads(row["summary_json"]),
        "changes": json.loads(row["changes_json"]),
    } for row in rows]


def next_observation(observed_at):
    try:
        value = datetime.fromisoformat(observed_at.replace("Z", "+00:00")) + timedelta(days=1)
        return value.isoformat(timespec="minutes")
    except (AttributeError, ValueError):
        return None
