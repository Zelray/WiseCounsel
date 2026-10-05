"""Reference solution for task 32 - T1-loan-payoff-quote."""
from decimal import ROUND_HALF_UP, Decimal

DAYS_PER_YEAR = 365
FEE_GRACE_DAYS = 10
FEE_CAP_RATE = 0.05


def _round_half_up(value, places=2):
    quantum = Decimal(1).scaleb(-places)
    return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))


def payoff_quote(balance, annual_rate, days_accrued, late_fee):
    """Return the dollar payoff that clears the loan as of the quote date."""
    if balance <= 0:
        return 0.0
    fee = 0.0
    if days_accrued > FEE_GRACE_DAYS:
        fee = min(late_fee, balance * FEE_CAP_RATE)
    interest = (balance + fee) * (annual_rate / 100.0) / DAYS_PER_YEAR * days_accrued
    return _round_half_up(balance + fee + interest)
