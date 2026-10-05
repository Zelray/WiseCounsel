"""Reference solution for task 31 - T1-badge-eligibility."""

ROLES = ("employee", "contractor", "senior", "admin")
ZONES = ("general", "lab", "server")
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
WEEKEND = {"saturday", "sunday"}
EMPLOYEE_HOURS = range(6, 20)
CONTRACTOR_HOURS = range(8, 18)


def badge_access(role, zone, weekday, hour):
    """Return True when the badge opens the door under the house access policy."""
    if role not in ROLES or zone not in ZONES:
        return False
    day = weekday.lower()
    if day not in DAYS or not 0 <= hour <= 23:
        return False
    if role == "admin":
        return True
    if zone == "server":
        return False
    if role == "senior":
        return True
    if day in WEEKEND:
        return False
    if role == "contractor":
        return hour in CONTRACTOR_HOURS and zone == "general"
    return hour in EMPLOYEE_HOURS and zone == "general"
