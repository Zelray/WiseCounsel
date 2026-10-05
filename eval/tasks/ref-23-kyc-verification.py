"""Reference solution for task 23 - T1-kyc-verification."""

RESUBMIT_CAP = 2

_REVIEW_OUTCOMES = {
    "approve": "approved",
    "reject": "rejected",
    "request_docs": "resubmit",
}


def advance_kyc(state, event, resubmission_count=0):
    """Return the pipeline state after `event` hits `state`."""
    if state == "pending" and event == "screen":
        return "review"
    if state == "review" and event in _REVIEW_OUTCOMES:
        return _REVIEW_OUTCOMES[event]
    if state == "resubmit" and event == "resubmit":
        return "pending" if resubmission_count < RESUBMIT_CAP else "rejected"
    return state
