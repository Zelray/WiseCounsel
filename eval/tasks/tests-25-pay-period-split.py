"""Hidden-spec tests for task 25 - T1-pay-period-split.

Stdlib only, no pytest. Usage:
    python tests-25-pay-period-split.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "pay_period_split"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_calendar_days_include_weekends",
    "test_R1_weekend_days_are_payable",
    "test_R2_period_endpoints_inclusive",
    "test_R3_hire_day_is_payable",
    "test_R4_hired_before_period",
    "test_R5_hired_after_period_pays_zero",
    "test_R5_day_after_period_is_zero",
    "test_R6_reversed_period_raises",
    "test_R7_malformed_period_dates_raise",
    "test_R7_malformed_hire_date_raises",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-25-pay-period-split.py <solution.py>\n")
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("solution", SOLUTION_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    _MODULE = _load_solution()
except Exception:
    _MODULE = None
FN = getattr(_MODULE, FUNCTION_NAME, None)
if FN is None:
    sys.stderr.write(
        "NOTE: no function named %r found in the solution; scoring as zero.\n" % FUNCTION_NAME
    )


class PayPeriodSplitTests(unittest.TestCase):
    def test_R1_calendar_days_include_weekends(self):
        # Jan 2024: 1st is a Monday; 6-7 and 13-14 are weekends.
        self.assertEqual(FN("2024-01-01", "2024-01-14", "2024-01-11"), (4, 14))

    def test_R1_weekend_days_are_payable(self):
        # Hired on Saturday the 13th: both weekend days count.
        self.assertEqual(FN("2024-01-01", "2024-01-14", "2024-01-13"), (2, 14))

    def test_R2_period_endpoints_inclusive(self):
        self.assertEqual(FN("2024-01-01", "2024-01-14", "2024-01-01"), (14, 14))
        self.assertEqual(FN("2024-02-26", "2024-03-10", "2024-02-26"), (14, 14))  # leap Feb
        self.assertEqual(FN("2024-01-05", "2024-01-05", "2024-01-05"), (1, 1))    # one-day period

    def test_R3_hire_day_is_payable(self):
        self.assertEqual(FN("2024-01-01", "2024-01-14", "2024-01-14"), (1, 14))
        self.assertEqual(FN("2024-01-01", "2024-01-14", "2024-01-08"), (7, 14))

    def test_R4_hired_before_period(self):
        self.assertEqual(FN("2024-01-01", "2024-01-14", "2023-12-25"), (14, 14))
        self.assertEqual(FN("2024-01-01", "2024-01-14", "2020-06-30"), (14, 14))

    def test_R5_hired_after_period_pays_zero(self):
        self.assertEqual(FN("2024-01-01", "2024-01-14", "2024-01-15"), (0, 14))
        self.assertEqual(FN("2024-01-01", "2024-01-14", "2025-06-01"), (0, 14))

    def test_R5_day_after_period_is_zero(self):
        self.assertEqual(FN("2024-01-01", "2024-01-31", "2024-02-01"), (0, 31))
        self.assertEqual(FN("2024-02-01", "2024-02-29", "2024-03-01"), (0, 29))

    def test_R6_reversed_period_raises(self):
        with self.assertRaises(ValueError):
            FN("2024-01-14", "2024-01-01", "2024-01-05")

    def test_R7_malformed_period_dates_raise(self):
        with self.assertRaises(ValueError):
            FN("15-01-2024", "2024-01-20", "2024-01-16")
        with self.assertRaises(ValueError):
            FN(None, "2024-01-20", "2024-01-16")

    def test_R7_malformed_hire_date_raises(self):
        with self.assertRaises(ValueError):
            FN("2024-01-01", "2024-01-14", "2024/01/10")
        with self.assertRaises(ValueError):
            FN("2024-01-01", "2024-01-14", None)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        PayPeriodSplitTests(name).run(result)
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
