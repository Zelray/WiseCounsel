"""Reference solution for task 12 - T1-hotel-stay-total."""
import math

PEAK_MONTHS = (6, 7, 8)
SHOULDER_MONTHS = (4, 5, 9, 10)
PEAK_NIGHT_CENTS = 18000
SHOULDER_NIGHT_CENTS = 14500
OFF_SEASON_NIGHT_CENTS = 11000
INCLUDED_GUESTS = 2
EXTRA_GUEST_CENTS = 1250
CLEANING_FEE_CENTS = 6000
LONG_STAY_MIN_NIGHTS = 7
LONG_STAY_DISCOUNT_NUM = 88
LONG_STAY_DISCOUNT_DEN = 100
TAX_RATE_NUM = 9
TAX_RATE_DEN = 100


def stay_total(nights, guests, month):
    """Return the total stay price in dollars, or -1.0 for an unusable request."""
    if isinstance(nights, bool) or not isinstance(nights, int) or nights < 1:
        return -1.0
    if isinstance(guests, bool) or not isinstance(guests, int) or guests < 1:
        return -1.0
    if isinstance(month, bool) or not isinstance(month, int) or not 1 <= month <= 12:
        return -1.0

    if month in PEAK_MONTHS:
        night_cents = PEAK_NIGHT_CENTS
    elif month in SHOULDER_MONTHS:
        night_cents = SHOULDER_NIGHT_CENTS
    else:
        night_cents = OFF_SEASON_NIGHT_CENTS

    extra_guests = max(0, guests - INCLUDED_GUESTS)
    room_cents = (night_cents + EXTRA_GUEST_CENTS * extra_guests) * nights
    if nights >= LONG_STAY_MIN_NIGHTS:
        room_cents = room_cents * LONG_STAY_DISCOUNT_NUM // LONG_STAY_DISCOUNT_DEN

    tax_cents = math.floor(room_cents * TAX_RATE_NUM / TAX_RATE_DEN + 0.5)
    return (room_cents + CLEANING_FEE_CENTS + tax_cents) / 100
