"""Reference solution for task 30 - T1-refund-eligibility."""

STANDARD_WINDOW = 30
CATEGORY_WINDOWS = {"electronics": 15, "perishables": 7}
DEFECT_WINDOW = 90
CONDITIONS = ("new", "opened", "defective")


def refund_eligibility(category, days_since_delivery, condition):
    """Return 'full', 'partial', or 'denied' under the house return policy."""
    if condition not in CONDITIONS:
        raise ValueError("unknown condition: %r" % (condition,))
    if category == "clearance":
        return "denied"
    if days_since_delivery < 0:
        return "denied"
    if condition == "defective":
        return "full" if days_since_delivery <= DEFECT_WINDOW else "denied"
    window = CATEGORY_WINDOWS.get(category, STANDARD_WINDOW)
    if days_since_delivery > window:
        return "denied"
    return "partial" if condition == "opened" else "full"
