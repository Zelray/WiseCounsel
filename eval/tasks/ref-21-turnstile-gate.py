"""Reference solution for task 21 - T1-turnstile-gate."""

LOCKED = "locked"
UNLOCKED = "unlocked"
RELOCK_AFTER_SECONDS = 30


def turnstile_step(state, event, idle_seconds=0):
    """Return the gate's next state after one controller event."""
    if state == UNLOCKED:
        if event == "push":
            return LOCKED
        if event == "timeout" and idle_seconds >= RELOCK_AFTER_SECONDS:
            return LOCKED
        return state
    if state == LOCKED and event in ("coin", "swipe"):
        return UNLOCKED
    return state
