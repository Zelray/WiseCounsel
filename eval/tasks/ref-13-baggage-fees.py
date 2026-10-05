"""Reference solution for task 13 - T1-baggage-fees."""
import math

FREE_CARRY_ONS = 1
SECOND_CARRY_ON_CENTS = 3500
MAX_CARRY_ONS = 2
FIRST_CHECKED_CENTS = 4000
SECOND_CHECKED_CENTS = 5500
EXTRA_CHECKED_CENTS = 9000
WEIGHT_LIMIT_KG = 23
WEIGHT_REFUSAL_KG = 32
OVERWEIGHT_FEE_CENTS = 7500
WAIVER_TIERS = {"silver": 1, "gold": 2}
VALID_TIERS = WAIVER_TIERS.keys() | {"none"}
PREPAY_DISCOUNT_NUM = 80
PREPAY_DISCOUNT_DEN = 100


def baggage_fees(carry_ons, checked, heaviest_kg, tier, prepaid):
    """Return the passenger's baggage total in dollars, or -1.0 if refused."""
    if isinstance(carry_ons, bool) or not isinstance(carry_ons, int) or carry_ons < 0:
        return -1.0
    if carry_ons > MAX_CARRY_ONS:
        return -1.0
    if isinstance(checked, bool) or not isinstance(checked, int) or checked < 0:
        return -1.0
    if isinstance(heaviest_kg, bool) or not isinstance(heaviest_kg, (int, float)):
        return -1.0
    if heaviest_kg <= 0:
        return -1.0
    if not isinstance(tier, str) or tier.lower() not in VALID_TIERS:
        return -1.0
    if not isinstance(prepaid, bool):
        return -1.0
    if checked > 0 and heaviest_kg > WEIGHT_REFUSAL_KG:
        return -1.0

    total = 0
    if carry_ons > FREE_CARRY_ONS:
        total += SECOND_CARRY_ON_CENTS

    if checked > 0:
        escalator = [FIRST_CHECKED_CENTS, SECOND_CHECKED_CENTS]
        base_fees = [escalator[i] if i < len(escalator) else EXTRA_CHECKED_CENTS
                     for i in range(checked)]
        waived = WAIVER_TIERS.get(tier.lower(), 0)
        base_total = sum(base_fees[waived:])
        if prepaid:
            base_total = base_total * PREPAY_DISCOUNT_NUM // PREPAY_DISCOUNT_DEN
        if heaviest_kg > WEIGHT_LIMIT_KG:
            base_total += OVERWEIGHT_FEE_CENTS
        total += base_total

    return total / 100
