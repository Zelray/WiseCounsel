"""Reference solution for eval task 02 - T1-parking.

Posted-rate rules for one commercial garage:

    stay of 15 minutes or less            -> free (grace window)
    after grace                           -> 2.75 per STARTED half-hour,
                                             counted from the entry minute
    never more than                       -> 25.00 daily cap
    exit_minute None                      -> lost ticket, flat 40.00
                                             (no grace, no cap)
    exit_minute < entry_minute            -> ValueError (no overnight wrap)
    minutes not whole numbers in 0..1439  -> ValueError

The fee comes back as a plain float at two decimals.
"""

from decimal import Decimal

_GRACE_MINUTES = 15
_UNIT_MINUTES = 30
_UNIT_RATE = Decimal("2.75")
_DAILY_CAP = Decimal("25.00")
_LOST_TICKET_FEE = Decimal("40.00")
_MIN_MINUTE = 0
_MAX_MINUTE = 1439


def _whole_minute(value, allow_none, name):
    if value is None:
        if allow_none:
            return None
        raise ValueError("%s is required" % (name,))
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s must be whole minutes since midnight" % (name,))
    if value != int(value):
        raise ValueError("%s must be whole minutes since midnight" % (name,))
    minute = int(value)
    if minute < _MIN_MINUTE or minute > _MAX_MINUTE:
        raise ValueError("%s must be minutes since midnight (0-1439)" % (name,))
    return minute


def parking_fee(entry_minute, exit_minute):
    entry = _whole_minute(entry_minute, allow_none=False, name="entry_minute")
    leave = _whole_minute(exit_minute, allow_none=True, name="exit_minute")

    if leave is None:  # lost ticket
        return float(_LOST_TICKET_FEE)

    if leave < entry:
        raise ValueError("exit_minute cannot be before entry_minute")

    duration = leave - entry
    if duration <= _GRACE_MINUTES:
        return 0.0

    units = -(-duration // _UNIT_MINUTES)  # started half-hours, no proration
    fee = _UNIT_RATE * units
    if fee > _DAILY_CAP:
        fee = _DAILY_CAP
    return float(fee)
