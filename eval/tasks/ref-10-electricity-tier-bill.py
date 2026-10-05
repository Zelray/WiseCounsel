"""Reference solution for task 10 - T1-electricity-tier-bill."""
import math

BLOCK1_MAX_KWH = 500
BLOCK2_MAX_KWH = 1000
BLOCK1_RATE_CENTS = 12
BLOCK2_RATE_CENTS = 15
BLOCK3_RATE_CENTS = 20
FIXED_CHARGE_CENTS = 975
STANDARD_PERIOD_DAYS = 30
TAX_RATE = 0.06


def electricity_bill(kwh, days):
    """Return the bill in dollars for a billing period, or raise ValueError."""
    _validate(kwh, days)

    energy_cents = BLOCK1_RATE_CENTS * min(kwh, BLOCK1_MAX_KWH)
    if kwh > BLOCK1_MAX_KWH:
        energy_cents += BLOCK2_RATE_CENTS * (min(kwh, BLOCK2_MAX_KWH) - BLOCK1_MAX_KWH)
    if kwh > BLOCK2_MAX_KWH:
        energy_cents += BLOCK3_RATE_CENTS * (kwh - BLOCK2_MAX_KWH)

    fixed_cents = _round_half_up(FIXED_CHARGE_CENTS * days / STANDARD_PERIOD_DAYS)

    subtotal_cents = energy_cents + fixed_cents
    tax_cents = _round_half_up(subtotal_cents * TAX_RATE)
    return (subtotal_cents + tax_cents) / 100


def _validate(kwh, days):
    if isinstance(kwh, bool) or not isinstance(kwh, (int, float)) or kwh < 0:
        raise ValueError("kwh must be a non-negative number")
    if isinstance(days, bool) or not isinstance(days, int) or days < 1:
        raise ValueError("days must be a whole number of at least 1")


def _round_half_up(amount_cents):
    """Round to the nearest whole cent, ties upward."""
    return math.floor(amount_cents + 0.5)
