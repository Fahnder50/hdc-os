import json
from datetime import datetime, timezone
from html import unescape
import re
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class AdapterError(ValueError):
    pass


class LiveAdapterError(AdapterError):
    pass


def _json_ld_blocks(document):
    pattern = r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>"
    blocks = re.findall(pattern, document, flags=re.IGNORECASE | re.DOTALL)
    if not blocks:
        raise AdapterError("No JSON-LD script block found")
    values = []
    for block in blocks:
        try:
            values.append(json.loads(block.strip()))
        except json.JSONDecodeError as error:
            raise AdapterError(f"Invalid JSON-LD: {error.msg}") from error
    return values


def _flatten(values):
    for value in values:
        if isinstance(value, list):
            yield from _flatten(value)
        elif isinstance(value, dict) and "@graph" in value:
            yield from _flatten(value["@graph"])
        else:
            yield value


def _type_matches(value, expected):
    types = value.get("@type", []) if isinstance(value, dict) else []
    if isinstance(types, str):
        types = [types]
    return expected in types


def parse_json_ld(document, source_reference=None):
    products = [value for value in _flatten(_json_ld_blocks(document)) if _type_matches(value, "Product")]
    if not products:
        raise AdapterError("No Product JSON-LD object found")
    product = products[0]
    offers = product.get("offers") or {}
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    seller = offers.get("seller") or {}
    seller_name = seller.get("name") if isinstance(seller, dict) else seller
    availability = offers.get("availability")
    if isinstance(availability, str):
        availability = availability.rsplit("/", 1)[-1].lower()
    return {
        "product_name": product.get("name"),
        "technical_reference": product.get("mpn") or product.get("sku"),
        "sku": product.get("sku"),
        "mpn": product.get("mpn"),
        "source_reference": source_reference or product.get("url"),
        "price": offers.get("price"),
        "currency": offers.get("priceCurrency"),
        "availability": availability,
        "vendor_name": seller_name,
        "source_type": "json-ld",
        "product_url": product.get("url") or source_reference,
    }


def parse_json_ld_file(path):
    file_path = Path(path)
    return parse_json_ld(file_path.read_text(encoding="utf-8"), str(file_path))


def fetch_url(url, timeout=20, user_agent="HDC-Procurement-Watch/0.1", retries=1):
    request = Request(url, headers={"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"})
    last_error = None
    for attempt in range(retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < retries:
                sleep(0.25)
    raise LiveAdapterError(f"Source request failed for {url}: {last_error}") from last_error


def _extract_balanced_json(text, marker):
    start = text.find(marker)
    if start < 0:
        raise LiveAdapterError(f"Live source marker not found: {marker}")
    start = text.find("[", start)
    if start < 0:
        raise LiveAdapterError(f"Live source array not found: {marker}")
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        character = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character == "[":
            depth += 1
        elif character == "]":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise LiveAdapterError(f"Live source array is incomplete: {marker}")


def _plain_text(value):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def _shipping_cost(offer):
    text = _plain_text(offer.get("availability_text_el"))
    if "gratisversand" in text.lower() or "kostenfrei" in text.lower():
        return 0
    return None


def parse_geizhals(document, source_reference=None, max_offers=5):
    try:
        offers = json.loads(_extract_balanced_json(document, "offers: [{"))
    except json.JSONDecodeError as error:
        raise LiveAdapterError(f"Invalid Geizhals offer data: {error.msg}") from error
    mpn_match = re.search(r"\bmpn:\s*'([^']+)'", document)
    name_match = re.search(r"product:\s*\{.*?name:\s*'([^']+)'", document, re.DOTALL)
    model = mpn_match.group(1) if mpn_match else None
    product_name = name_match.group(1).replace("\\u002d", "-") if name_match else "Unknown UPS product"
    normalized = []
    for index, offer in enumerate(offers):
        price = offer.get("raw_price")
        merchant = offer.get("merchant_name") or offer.get("merchant_link_data", {}).get("name")
        if price is None or not merchant:
            continue
        delivery_text = _plain_text(offer.get("delivery_time"))
        shipping = _shipping_cost(offer)
        normalized.append({
            "offer_id": f"LIVE-{re.sub(r'[^A-Za-z0-9]+', '-', model or product_name).strip('-').upper()}-{index + 1:03d}",
            "product_id": f"LIVE-{re.sub(r'[^A-Za-z0-9]+', '-', model or product_name).strip('-').upper()}",
            "product_name": product_name,
            "manufacturer": product_name.split()[0] if product_name else None,
            "model": model,
            "vendor_id": f"LIVE-{re.sub(r'[^A-Za-z0-9]+', '-', merchant).strip('-').upper()}",
            "vendor_name": merchant,
            "product_url": source_reference,
            "source_reference": source_reference,
            "source_type": "geizhals",
            "price": price,
            "shipping": shipping,
            "total_price": price + shipping if shipping is not None else None,
            "currency": "EUR",
            "availability": "in_stock" if delivery_text else "unknown",
            "delivery_text": delivery_text,
            "fulfillment_type": "shipping",
            "technical": {},
        })
        if len(normalized) >= max_offers:
            break
    if not normalized:
        raise LiveAdapterError("Geizhals source returned no usable offers")
    return normalized


def collect_source(source, timeout=20, user_agent="HDC-Procurement-Watch/0.1", retries=1):
    adapter = source.get("adapter", "geizhals")
    document = fetch_url(source["url"], timeout=timeout, user_agent=user_agent, retries=retries)
    if adapter == "geizhals":
        return parse_geizhals(document, source["url"], int(source.get("max_offers", 5)))
    if adapter == "json-ld":
        return [parse_json_ld(document, source["url"])]
    raise LiveAdapterError(f"Unknown live adapter: {adapter}")
