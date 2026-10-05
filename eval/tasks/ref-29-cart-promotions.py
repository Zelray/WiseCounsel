"""Reference solution for task 29 - T1-cart-promotions."""
from decimal import ROUND_HALF_UP, Decimal

CATALOG = {
    "WELCOME15": {"kind": "percent", "value": 15},
    "TAKE20": {"kind": "percent", "value": 20},
    "FIVE5": {"kind": "percent", "value": 5},
    "SAVE15": {"kind": "flat", "value": 15, "threshold": 25},
}
PERCENT_ELIGIBLE = {"apparel", "home"}
MAX_DISCOUNT_RATE = 0.50


def _round_half_up(value, places=2):
    quantum = Decimal(1).scaleb(-places)
    return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))


def apply_promotions(cart, codes):
    """Return the final charge after the house promo rules, in dollars."""
    if not cart:
        return 0.0
    subtotal = sum(item["price"] for item in cart)

    seen = set()
    ordered = []
    for code in codes:
        key = code.strip().upper()
        if key in CATALOG and key not in seen:
            seen.add(key)
            ordered.append(key)

    best_percent = None
    flat_codes = []
    for key in ordered:
        entry = CATALOG[key]
        if entry["kind"] == "percent":
            if best_percent is None or entry["value"] > CATALOG[best_percent]["value"]:
                best_percent = key
        else:
            flat_codes.append(key)

    discount = 0.0
    if best_percent is not None:
        rate = CATALOG[best_percent]["value"] / 100.0
        for item in cart:
            if item["category"] in PERCENT_ELIGIBLE:
                discount += item["price"] * rate

    running = subtotal - discount
    for key in flat_codes:
        entry = CATALOG[key]
        if running >= entry["threshold"]:
            discount += entry["value"]
            running -= entry["value"]

    discount = min(discount, subtotal * MAX_DISCOUNT_RATE)
    return _round_half_up(subtotal - discount)
