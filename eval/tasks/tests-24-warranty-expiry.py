"""Hidden-spec tests for task 24 - T1-warranty-expiry.

Stdlib only, no pytest. Usage:
    python tests-24-warranty-expiry.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "warranty_expiry"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_same_day_addition",
    "test_R1_multi_month_span",
    "test_R2_day_clamps_to_month_end",
    "test_R3_month_end_anchor",
    "test_R3_anchor_only_for_month_ends",
    "test_R4_leap_day_is_month_end",
    "test_R5_repair_days_extend",
    "test_R5_repair_added_after_clamping",
    "test_R6_iso_string_format",
    "test_R7_malformed_purchase_date_raises",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-24-warranty-expiry.py <solution.py>\n")
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


class WarrantyExpiryTests(unittest.TestCase):
    def test_R1_same_day_addition(self):
        self.assertEqual(FN("2024-01-15", 12), "2025-01-15")   # a year out, same day
        self.assertEqual(FN("2023-03-10", 6), "2023-09-10")    # mid-month stays put

    def test_R1_multi_month_span(self):
        self.assertEqual(FN("2024-05-20", 30), "2026-11-20")   # two and a half years out
        self.assertEqual(FN("2022-07-04", 7), "2023-02-04")    # across a year boundary

    def test_R2_day_clamps_to_month_end(self):
        self.assertEqual(FN("2023-01-30", 1), "2023-02-28")    # Feb has no 30th
        self.assertEqual(FN("2023-05-31", 1), "2023-06-30")    # June has no 31st
        self.assertEqual(FN("2024-03-31", 1), "2024-04-30")    # April has no 31st

    def test_R3_month_end_anchor(self):
        self.assertEqual(FN("2023-02-28", 1), "2023-03-31")    # month-end rides to Mar 31
        self.assertEqual(FN("2023-04-30", 1), "2023-05-31")    # ...and to May 31
        self.assertEqual(FN("2023-02-28", 12), "2024-02-29")   # ...picking up leap day

    def test_R3_anchor_only_for_month_ends(self):
        self.assertEqual(FN("2023-02-27", 1), "2023-03-27")    # one day short: keeps its day
        self.assertEqual(FN("2023-04-29", 1), "2023-05-29")    # one day short: keeps its day

    def test_R4_leap_day_is_month_end(self):
        self.assertEqual(FN("2024-02-29", 6), "2024-08-31")    # Aug 31, not Aug 29
        self.assertEqual(FN("2024-02-29", 12), "2025-02-28")   # back to a non-leap Feb

    def test_R5_repair_days_extend(self):
        self.assertEqual(FN("2024-01-15", 12, 10), "2025-01-25")  # ten depot days tacked on
        self.assertEqual(FN("2024-01-15", 12), "2025-01-15")      # no repairs, no extension

    def test_R5_repair_added_after_clamping(self):
        self.assertEqual(FN("2023-01-31", 1, 1), "2023-03-01")    # Feb 28 first, then +1
        self.assertEqual(FN("2024-02-29", 6, 1), "2024-09-01")    # Aug 31 first, then +1

    def test_R6_iso_string_format(self):
        result = FN("2024-06-15", 3)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "2024-09-15")
        self.assertRegex(result, r"\A\d{4}-\d{2}-\d{2}\Z")

    def test_R7_malformed_purchase_date_raises(self):
        for bad in ("not-a-date", "2024/01/15", "", "2024-02-30", None, 20240115):
            with self.assertRaises(ValueError):
                FN(bad, 12)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        WarrantyExpiryTests(name).run(result)
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
