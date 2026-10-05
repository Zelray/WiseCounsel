"""Reference solution for task 19 - T1-subscription-lifecycle."""

TRIAL = "trial"
ACTIVE = "active"
PAST_DUE = "past_due"
CANCELED = "canceled"
EXPIRED = "expired"

GRACE_DAYS = 30
REACTIVATION_DAYS = 14


def advance_subscription(state, event, days_in_state=0):
    """Return the subscription state after `event` hits `state`."""
    if state == TRIAL and event == "convert":
        return ACTIVE
    if state in (TRIAL, ACTIVE) and event == "cancel":
        return CANCELED
    if state == ACTIVE and event == "payment_failed":
        return PAST_DUE
    if state == PAST_DUE and event == "payment_succeeded":
        return ACTIVE if days_in_state <= GRACE_DAYS else EXPIRED
    if state == PAST_DUE and event == "payment_failed":
        return PAST_DUE if days_in_state <= GRACE_DAYS else EXPIRED
    if state == CANCELED and event == "reactivate":
        return ACTIVE if days_in_state <= REACTIVATION_DAYS else EXPIRED
    return state
