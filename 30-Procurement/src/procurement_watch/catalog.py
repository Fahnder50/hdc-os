import json
from pathlib import Path

import yaml


ALLOWED_OUTLETS = {"Schuko", "IEC C13", "Universal", "mixed", "unknown"}
ALLOWED_STATES = {"verified_true", "verified_false", "unknown"}


def load_product_catalog(repository_root):
    directory = Path(repository_root) / "30-Procurement" / "catalog" / "products"
    catalog = {}
    for path in sorted(directory.glob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        model = document.get("model_number")
        if not model or document.get("outlet_type") not in ALLOWED_OUTLETS:
            raise ValueError(f"Invalid product evidence: {path}")
        if model in catalog:
            raise ValueError(f"Duplicate product model: {model}")
        for evidence in document.get("evidence", []):
            if evidence.get("confidence") not in ALLOWED_STATES:
                raise ValueError(f"Invalid evidence state in {path}")
        document["technical"] = document.get("technical", {})
        catalog[model] = document
    return catalog


def product_evidence(repository_root, model_number):
    return load_product_catalog(repository_root).get(model_number)


def evidence_snapshot(document):
    if document is None:
        return {"status": "unknown", "evidence": []}
    return {"status": "curated", "evidence": document.get("evidence", [])}


def technical_json(document):
    return json.dumps(document.get("technical", {}) if document else {}, sort_keys=True)
