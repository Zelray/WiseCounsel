"""Reference solution for task 37 - T1-dryclean-order."""
from decimal import ROUND_HALF_UP, Decimal

RATE_CARD_CENTS = {
    "shirt": 350,
    "pants": 450,
    "coat": 900,
    "dress": 700,
    "blouse": 425,
    "sweater": 575,
    "tie": 250,
    "bedsheet": 600,
    "pillowcase": 225,
    "duvet": 1250,
    "tablecloth": 525,
    "leather jacket": 1500,
    "wedding gown": 2750,
}
LINEN_TYPES = ("bedsheet", "pillowcase", "duvet", "tablecloth")
BUNDLE_SIZE = 5
BUNDLE_PRICE_CENTS = 1800
VOLUME_MIN_PIECES = 12
MIN_CHARGE_CENTS = 1000
EXPRESS_EXCLUDED = ("leather jacket", "wedding gown")
CANNOT_PRICE = -1.0


def _round_half_up_cents(units):
    """units counts hundredths of a cent; snap to whole cents, ties upward."""
    return int((Decimal(units) / Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def price_order(items, express):
    """Return the dollar total for a cleaning ticket, or -1.0 when it cannot be priced."""
    subtotal_cents = 0
    excluded_cents = 0
    pieces = 0
    linen_prices = []  # per-piece linen cost in cents, in ticket order
    for line in items:
        try:
            garment, quantity = line
        except (TypeError, ValueError):
            return CANNOT_PRICE
        if not isinstance(garment, str) or garment not in RATE_CARD_CENTS:
            return CANNOT_PRICE
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            return CANNOT_PRICE
        price_cents = RATE_CARD_CENTS[garment]
        pieces += quantity
        if garment in LINEN_TYPES:
            linen_prices.extend([price_cents] * quantity)
        else:
            subtotal_cents += price_cents * quantity
            if garment in EXPRESS_EXCLUDED:
                excluded_cents += price_cents * quantity

    # Household-linen bundles: each complete group of five linen pieces swaps its
    # per-piece pricing for one flat line; the leftover pieces stay on the card.
    bundle_pieces = (len(linen_prices) // BUNDLE_SIZE) * BUNDLE_SIZE
    bundled_cents = sum(linen_prices[:bundle_pieces])
    subtotal_cents += (
        sum(linen_prices) - bundled_cents + (bundle_pieces // BUNDLE_SIZE) * BUNDLE_PRICE_CENTS
    )

    units = subtotal_cents * 100  # hundredths of a cent; every step stays exact
    if pieces >= VOLUME_MIN_PIECES:
        units = units * 9 // 10
    if express:
        excluded_units = excluded_cents * 100
        if pieces >= VOLUME_MIN_PIECES:
            excluded_units = excluded_units * 9 // 10
        units += (units - excluded_units) // 2
    if units < MIN_CHARGE_CENTS * 100:
        units = MIN_CHARGE_CENTS * 100
    return _round_half_up_cents(units) / 100.0
