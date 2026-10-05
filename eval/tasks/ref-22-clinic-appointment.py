"""Reference solution for task 22 - T1-clinic-appointment."""

CHECKIN_OPENS_MINUTES = 30
LATE_GRACE_MINUTES = 15


def update_appointment(state, event, minutes_until_appointment=0):
    """Return the appointment status after `event` hits `state`."""
    if state == "booked":
        if event == "check_in":
            if minutes_until_appointment > CHECKIN_OPENS_MINUTES:
                return state
            if minutes_until_appointment < -LATE_GRACE_MINUTES:
                return "no_show"
            return "checked_in"
        if event == "mark_no_show":
            return "no_show" if minutes_until_appointment <= 0 else state
        if event == "cancel":
            return "cancelled" if minutes_until_appointment > 0 else state
        return state
    if state == "checked_in" and event == "start_visit":
        return "in_room"
    if state == "in_room" and event == "complete":
        return "completed"
    return state
