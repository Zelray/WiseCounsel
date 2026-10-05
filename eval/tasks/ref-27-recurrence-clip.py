"""Reference solution for task 27 - T1-recurrence-clip."""
import datetime


def _parse_date(value):
    if not isinstance(value, str):
        raise ValueError("date must be a YYYY-MM-DD string")
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("date must be a YYYY-MM-DD string: %r" % (value,))


def recurrence_clip(start_date, count, window_start, window_end):
    """Return the ISO dates of the series' occurrences inside the window."""
    start = _parse_date(start_date)
    window_first = _parse_date(window_start)
    window_last = _parse_date(window_end)
    clipped = []
    for k in range(max(count, 0)):
        occurrence = start + datetime.timedelta(days=7 * k)
        if window_first <= occurrence < window_last:
            clipped.append(occurrence.isoformat())
    return clipped
