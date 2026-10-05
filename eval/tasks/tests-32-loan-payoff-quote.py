"""Hidden-spec tests for task 32 - T1-loan-payoff-quote.

Stdlib only, no pytest. Usage:
    python tests-32-loan-payoff-quote.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.

Round-3 calibration: the return shape, the percent rate units, the zero-days
degenerate case, and the non-positive-balance error path are published in the
brief; the basis, posting order, grace length, cap, and rounding mode stay
hidden. Each probe below isolates one hidden rule - the posting-order probe
carries a fee far under the cap at a day count past any plausible grace, the
cap probe runs at a zero rate so no interest convention can leak into it, and
the rounding probe lands on a true half cent.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "payoff_quote"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_perdiem_uses_365",
    "test_R1_zero_days_accrues_nothing",
    "test_R2_fee_rides_in_interest_base",
    "test_R2_interest_does_not_compound",
    "test_R3_grace_period_no_fee",
    "test_R3_fee_attaches_after_grace",
    "test_R4_fee_capped_at_five_percent",
    "test_R5_rounded_half_up_to_the_cent",
    "test_R6_nonpositive_balance_quotes_zero",
    "test_R7_rate_is_percent",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-32-loan-payoff-quote.py <solution.py>\n")
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("solution", SOLUTION_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_MODULE = _load_solution()
FN = getattr(_MODULE, FUNCTION_NAME, None)
if FN is None:
    sys.stderr.write(
        "NOTE: no function named %r found in the solution; scoring as zero.\n" % FUNCTION_NAME
    )


class LoanPayoffQuoteTests(unittest.TestCase):
    def test_R1_perdiem_uses_365(self):
        self.assertEqual(FN(3600, 3.65, 100, 0), 3636.0)   # 0.36/day, not the 360-day year
        self.assertEqual(FN(3600, 0, 100, 0), 3600.0)

    def test_R1_zero_days_accrues_nothing(self):
        # Published convention: no days, no interest - and the fee probe is zeroed out.
        self.assertEqual(FN(1000, 36.5, 0, 0), 1000.0)

    def test_R2_fee_rides_in_interest_base(self):
        # Fee 40 is far under the cap and day 25 is past any plausible grace,
        # so only the posting order can move this number: 2040 base, not 2000.
        self.assertEqual(FN(2000, 36.5, 25, 40), 2091.0)

    def test_R2_interest_does_not_compound(self):
        self.assertEqual(FN(1000, 36.5, 20, 0), 1020.0)

    def test_R3_grace_period_no_fee(self):
        self.assertEqual(FN(1000, 36.5, 10, 100), 1010.0)  # day 10 is still grace
        self.assertEqual(FN(1000, 36.5, 5, 100), 1005.0)

    def test_R3_fee_attaches_after_grace(self):
        # Day 11 turns the fee on; at 4 dollars the cap cannot touch it and the fee
        # is small enough that whether it rides in the base rounds to the same cent,
        # so only the grace length can move this number.
        self.assertEqual(FN(1000, 3.65, 11, 4), 1005.1)

    def test_R4_fee_capped_at_five_percent(self):
        # Zero rate: no interest math runs, so only the cap can move these numbers.
        self.assertEqual(FN(100, 0, 30, 50), 105.0)        # 50 capped to 5
        self.assertEqual(FN(100, 0, 30, 5), 105.0)         # exactly at the cap is allowed

    def test_R5_rounded_half_up_to_the_cent(self):
        # 365.00 + 0.015 interest is a true half cent - it rounds UP to 365.02.
        self.assertEqual(FN(365.0, 1.5, 1, 0), 365.02)
        self.assertEqual(FN(10000, 12, 7, 0), 10023.01)

    def test_R6_nonpositive_balance_quotes_zero(self):
        # Published convention: dead accounts quote 0.0, never a negative payoff.
        self.assertEqual(FN(0, 12, 30, 100), 0.0)
        self.assertEqual(FN(-50, 12, 30, 100), 0.0)

    def test_R7_rate_is_percent(self):
        # Published convention: 12 means 12% a year.
        self.assertEqual(FN(1000, 12, 365, 0), 1120.0)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        LoanPayoffQuoteTests(name).run(result)
        outcomes.append((name, result.wasSuccessful()))
        if not result.wasSuccessful():
            for label, bucket in (("FAIL", result.failures), ("ERROR", result.errors)):
                for _test, traceback in bucket:
                    sys.stderr.write("--- %s %s ---\n%s\n" % (label, name, traceback))
    for rule in RULE_ORDER:
        rule_outcomes = [ok for name, ok in outcomes if name.split("_")[1] == rule]
        status = "PASS" if rule_outcomes and all(rule_outcomes) else "FAIL"
        print("RULE %s %s" % (rule, status))
    passed = sum(1 for _name, ok in outcomes if ok)
    print("SCORE %d/%d" % (passed, len(outcomes)))


if __name__ == "__main__":
    main()
