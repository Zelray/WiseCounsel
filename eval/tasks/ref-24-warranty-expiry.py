"""Reference solution for task 24 - T1-warranty-expiry."""
import calendar
import datetime


def _parse_date(value):
    if not isinstance(value, str):
        raise ValueError("date must be a YYYY-MM-DD string")
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("date must be a YYYY-MM-DD string: %r" % (value,))


def _month_end(year, month):
    return calendar.monthrange(year, month)[1]


def warranty_expiry(purchase_date, months, repair_days=0):
    """Return the ISO date the warranty runs out, as a YYYY-MM-DD string."""
    start = _parse_date(purchase_date)
    year = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    last_day = _month_end(year, month)
    if start.day == _month_end(start.year, start.month):
        # Month-end purchases anchor to month ends forever after.
        day = last_day
    else:
        # Other purchases keep their day, clamped to the target month's length.
        day = min(start.day, last_day)
    expiry = datetime.date(year, month, day)
    if repair_days:
        expiry = expiry + datetime.timedelta(days=repair_days)
    return expiry.isoformat()
