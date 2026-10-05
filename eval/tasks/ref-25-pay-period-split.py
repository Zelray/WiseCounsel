"""Reference solution for task 25 - T1-pay-period-split."""
import datetime


def _parse_date(value):
    if not isinstance(value, str):
        raise ValueError("date must be a YYYY-MM-DD string")
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("date must be a YYYY-MM-DD string: %r" % (value,))


def pay_period_split(period_start, period_end, hire_date):
    """Return (payable_days, total_days) for an employee joining a pay period."""
    start = _parse_date(period_start)
    end = _parse_date(period_end)
    hire = _parse_date(hire_date)
    if end < start:
        raise ValueError("period_end is before period_start")
    total = (end - start).days + 1
    if hire > end:
        return (0, total)
    first_payable = max(hire, start)
    payable = (end - first_payable).days + 1
    return (payable, total)
