"""Reference solution for task 26 - T1-invoice-aging."""
import datetime

BUCKET_LABELS = ("current", "1-30", "31-60", "61-90", "91+")


def _parse_date(value):
    if not isinstance(value, str):
        raise ValueError("date must be a YYYY-MM-DD string")
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("date must be a YYYY-MM-DD string: %r" % (value,))


def _bucket_for(days_late):
    if days_late <= 0:
        return "current"
    if days_late <= 30:
        return "1-30"
    if days_late <= 60:
        return "31-60"
    if days_late <= 90:
        return "61-90"
    return "91+"


def _amount(invoice):
    if "amount" not in invoice:
        raise ValueError("invoice row is missing 'amount'")
    try:
        return float(invoice["amount"])
    except (TypeError, ValueError):
        raise ValueError("'amount' must be a number: %r" % (invoice["amount"],))


def invoice_aging(invoices, as_of):
    """Return the five-bucket aging totals for a list of invoice dicts."""
    as_of_date = _parse_date(as_of)
    totals = {label: 0.0 for label in BUCKET_LABELS}
    for invoice in invoices:
        due = _parse_date(invoice["due_date"])
        days_late = (as_of_date - due).days
        totals[_bucket_for(days_late)] += _amount(invoice)
    return {label: round(totals[label], 2) for label in BUCKET_LABELS}
