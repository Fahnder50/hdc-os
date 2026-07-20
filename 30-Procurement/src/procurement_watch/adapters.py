import json
import re
from pathlib import Path


class AdapterError(ValueError):
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
    }


def parse_json_ld_file(path):
    file_path = Path(path)
    return parse_json_ld(file_path.read_text(encoding="utf-8"), str(file_path))
