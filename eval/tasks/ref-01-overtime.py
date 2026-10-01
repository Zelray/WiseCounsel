"""Reference solution for eval task 01 - T1-overtime.

Weekly hourly pay with overtime:

    hours <= 40        -> all regular time
    40 < hours <= 50   -> hours past 40 paid at 1.5x
    50 < hours <= 60   -> hours past 50 paid at 2.0x
    hours > 60         -> ValueError
    rate < 12.00       -> ValueError
    negative / non-numeric input -> ValueError

Money is rounded HALF-UP to cents (never Python's banker's rounding)
before it leaves the function, and total == regular_pay + overtime_pay.
"""

from decimal import Decimal, ROUND_HALF_UP

_OT_TRIGGER = Decimal(40)
_OT_BAND_TOP = Decimal(50)
_WEEK_CAP = Decimal(60)
_RATE_FLOOR = Decimal("12.00")
_TIME_AND_HALF = Decimal("1.5")
_DOUBLE_TIME = Decimal(2)
_CENTS = Decimal("0.01")
_BAD_HOURS_MESSAGE = "hours must be non-negative"


def _as_decimal(value, is_hours=False):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        if is_hours:
            raise ValueError(_BAD_HOURS_MESSAGE)
        raise ValueError("rate must be a number")
    return Decimal(str(value))


def _cents(value):
    return value.quantize(_CENTS, rounding=ROUND_HALF_UP)


def calc_pay(hours, rate):
    worked = _as_decimal(hours, is_hours=True)
    if worked < 0:
        raise ValueError(_BAD_HOURS_MESSAGE)

    pay_rate = _as_decimal(rate)
    if pay_rate < _RATE_FLOOR:
        raise ValueError("rate must be at least 12.00")
    if worked > _WEEK_CAP:
        raise ValueError("hours must not exceed 60 per week")

    if worked <= _OT_TRIGGER:
        regular = _cents(worked * pay_rate)
        overtime = _cents(Decimal(0))
    elif worked <= _OT_BAND_TOP:
        regular = _cents(_OT_TRIGGER * pay_rate)
        overtime = _cents((worked - _OT_TRIGGER) * pay_rate * _TIME_AND_HALF)
    else:
        regular = _cents(_OT_TRIGGER * pay_rate)
        overtime = _cents(
            (_OT_BAND_TOP - _OT_TRIGGER) * pay_rate * _TIME_AND_HALF
            + (worked - _OT_BAND_TOP) * pay_rate * _DOUBLE_TIME
        )

    total = _cents(regular + overtime)
    return {
        "regular_pay": float(regular),
        "overtime_pay": float(overtime),
        "total": float(total),
    }
