"""Reference solution for task 18 - T1-seat-map."""
import re

_NOTATION = re.compile(r"\A([A-Z])([1-9][0-9]*)\Z")
SKIPPED_ROWS = frozenset("IO")
LAST_ROW = "T"
FRONT_ROWS = frozenset("ABCD")
FRONT_CAPACITY = 14
REAR_CAPACITY = 22
SKIPPED_SEAT = 13


def parse_seat(notation):
    """Return (row, seat) for a sellable Marlowe seat, else None. Never raises."""
    if not isinstance(notation, str):
        return None
    match = _NOTATION.match(notation)
    if match is None:
        return None
    row, seat = match.group(1), int(match.group(2))
    if row > LAST_ROW or row in SKIPPED_ROWS:
        return None
    capacity = FRONT_CAPACITY if row in FRONT_ROWS else REAR_CAPACITY
    if seat > capacity or seat == SKIPPED_SEAT or seat == capacity:
        return None
    return (row, seat)
