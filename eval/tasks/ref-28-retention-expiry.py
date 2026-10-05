"""Reference solution for task 28 - T1-retention-expiry."""
import datetime

TTL_DAYS = {
    "logs": 90,
    "backups": 365,
    "customer": 1095,
    "financial": 2555,
}


def _parse_date(value):
    if not isinstance(value, str):
        raise ValueError("date must be a YYYY-MM-DD string")
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("date must be a YYYY-MM-DD string: %r" % (value,))


def retention_expiry(created_date, category, legal_hold=False):
    """Return the earliest ISO destruction date for a record, or None on hold."""
    created = _parse_date(created_date)
    if category not in TTL_DAYS:
        raise ValueError("unknown retention category: %r" % (category,))
    if legal_hold:
        return None
    expiry = created + datetime.timedelta(days=TTL_DAYS[category])
    if expiry.weekday() == 5:  # Saturday
        expiry = expiry + datetime.timedelta(days=2)
    elif expiry.weekday() == 6:  # Sunday
        expiry = expiry + datetime.timedelta(days=1)
    return expiry.isoformat()
