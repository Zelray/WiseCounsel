"""Reference solution for eval task 06 - T1-cutoff-dates.

Fulfilment rule: "orders ship next business day."

  * orders placed before 14:00 local  -> first business day after the order date
  * orders placed at/after 14:00      -> the business day after that one
  * business day = Monday-Friday that is not in ``holidays``
  * the answer is always a business day (roll forward past weekends/holidays)
  * a bare ``datetime.date`` counts as noon that day (comfortably pre-cutoff)

Stdlib only (``datetime``).
"""
from datetime import date, datetime, timedelta

CUTOFF_HOUR = 14
NOON_HOUR = 12


def _as_moment(value):
    """Normalise the input to a datetime; a bare date counts as noon."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, NOON_HOUR, 0, 0)
    raise TypeError("order_datetime must be a datetime.date or datetime.datetime, got %r" % (type(value).__name__,))


def _is_business_day(day, holidays):
    return day.weekday() < 5 and day not in holidays


def _next_business_day(day, holidays):
    candidate = day + timedelta(days=1)
    while not _is_business_day(candidate, holidays):
        candidate += timedelta(days=1)
    return candidate


def ship_date(order_datetime, holidays):
    """Return the datetime.date on which the order leaves the warehouse."""
    moment = _as_moment(order_datetime)
    dark_days = set(holidays)

    ship_on = _next_business_day(moment.date(), dark_days)
    if moment.hour >= CUTOFF_HOUR:
        # Missed the cutoff: the truck already left, so one more business day.
        ship_on = _next_business_day(ship_on, dark_days)
    return ship_on
