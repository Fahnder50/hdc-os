from datetime import date, datetime, timedelta
import re


DATE_PATTERN = re.compile(r"(?P<day>\d{1,2})[./](?P<month>\d{1,2})[./](?P<year>\d{4})")
ISO_DATE_PATTERN = re.compile(r"(?P<year>20\d{2})-(?P<month>\d{2})-(?P<day>\d{2})")
WORKDAY_PATTERN = re.compile(r"(?P<low>\d+)\s*[-–]\s*(?P<high>\d+)\s*Werktage", re.IGNORECASE)


def _as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()


def add_workdays(start, days):
    current = _as_date(start)
    remaining = int(days)
    while remaining:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def _find_date(text):
    match = ISO_DATE_PATTERN.search(text)
    if match:
        return date(int(match["year"]), int(match["month"]), int(match["day"]))
    match = DATE_PATTERN.search(text)
    if match:
        return date(int(match["year"]), int(match["month"]), int(match["day"]))
    return None


def normalize_delivery(text, observed_at, required_by_date):
    raw = (text or "").strip()
    observed_date = _as_date(observed_at)
    deadline = _as_date(required_by_date)
    lowered = raw.lower()
    if not raw:
        return _result(raw, None, None, "unknown", "unknown", "unknown", None, deadline)

    explicit = _find_date(raw)
    if explicit:
        latest = explicit
        earliest = explicit
        confidence = "confirmed"
        fulfillment = "shipping"
    elif "morgen" in lowered:
        earliest = observed_date + timedelta(days=1)
        latest = earliest
        confidence = "estimated"
        fulfillment = "shipping"
    else:
        workdays = WORKDAY_PATTERN.search(raw)
        if workdays:
            earliest = add_workdays(observed_date, workdays["low"])
            latest = add_workdays(observed_date, workdays["high"])
            confidence = "estimated"
            fulfillment = "shipping"
        elif "abholung" in lowered or "pickup" in lowered:
            earliest = observed_date if any(token in lowered for token in ("möglich", "moeglich", "verfügbar", "verfuegbar", "lagernd")) else None
            latest = earliest
            confidence = "confirmed" if earliest else "unknown"
            fulfillment = "pickup"
        else:
            return _result(raw, None, None, "unknown", "unknown", "unknown", None, deadline)

    eligible = latest <= deadline if latest else None
    return _result(raw, earliest, latest, confidence, "true" if eligible else "false", fulfillment, None, deadline)


def apply_purchase_window(result, observed_at, preferred_shipping_purchase_by, shipping_exception_date):
    if result["fulfillment_type"] != "shipping":
        return result
    observed_date = _as_date(observed_at)
    exception_date = _as_date(shipping_exception_date)
    if observed_date > exception_date:
        result["delivery_eligibility"] = "false"
    elif observed_date == exception_date and result["delivery_confidence"] != "confirmed":
        result["delivery_eligibility"] = "unknown"
    return result


def _result(raw, earliest, latest, confidence, eligible, fulfillment, pickup_location, deadline):
    return {
        "delivery_text_raw": raw or None,
        "delivery_date_earliest": earliest.isoformat() if earliest else None,
        "delivery_date_latest": latest.isoformat() if latest else None,
        "delivery_confidence": confidence,
        "delivery_eligibility": eligible,
        "fulfillment_type": fulfillment,
        "pickup_location": pickup_location,
    }
