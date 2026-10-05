"""Reference solution for task 20 - T1-vending-session."""

IDLE = "idle"
COLLECTING = "collecting"
EXACT_CHANGE = "exact_change"
DISPENSING = "dispensing"


def _is_valid_coin(amount_cents):
    return (
        isinstance(amount_cents, int)
        and not isinstance(amount_cents, bool)
        and amount_cents > 0
        and amount_cents % 5 == 0
    )


def vend_step(state, event, amount_cents=0, credit_cents=0, price_cents=0):
    """Return (next_state, credit_cents) after one vending-machine event."""
    if state not in (IDLE, COLLECTING, EXACT_CHANGE, DISPENSING):
        return (state, credit_cents)
    if state == DISPENSING:
        return (DISPENSING, 0)
    if event == "coin" and _is_valid_coin(amount_cents):
        if state == EXACT_CHANGE and credit_cents + amount_cents > price_cents:
            return (state, credit_cents)
        next_state = COLLECTING if state == IDLE else state
        return (next_state, credit_cents + amount_cents)
    if event == "select":
        if state == EXACT_CHANGE:
            if credit_cents == price_cents:
                return (DISPENSING, 0)
            return (state, credit_cents)
        if state == COLLECTING and credit_cents >= price_cents:
            return (DISPENSING, 0)
        return (state, credit_cents)
    if event == "refund" and state in (IDLE, COLLECTING, EXACT_CHANGE):
        return (IDLE, 0)
    return (state, credit_cents)
