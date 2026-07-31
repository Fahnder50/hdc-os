"""Deterministic, non-ordering procurement approval gate."""


REQUIRED_OFFER_FIELDS = frozenset({
    "exact_model", "new_condition", "availability", "item_price",
    "shipping", "total_price", "vendor", "warranty", "power_supply",
    "rack_accessory", "poe_configuration",
})


def procurement_state(*, architecture_gates, offer, hard_total_price, owner_approved=False):
    """Return the review state; this function never places an order."""
    if not architecture_gates or not all(architecture_gates.values()):
        return "REJECT"
    if not REQUIRED_OFFER_FIELDS.issubset(offer) or any(
        offer.get(field) in (None, "", "unknown") for field in REQUIRED_OFFER_FIELDS
    ):
        return "WAIT"
    if offer["total_price"] > hard_total_price:
        return "WAIT"
    return "BUY_CANDIDATE" if owner_approved else "REVIEW"


def automatic_order_allowed():
    """Ordering is deliberately outside the procurement watch scope."""
    return False
