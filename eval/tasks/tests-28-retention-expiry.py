"""Hidden-spec tests for task 28 - T1-retention-expiry.

Stdlib only, no pytest. Usage:
    python tests-28-retention-expiry.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "retention_expiry"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
TEST_ORDER = [
    "test_R1_logs_ttl",
    "test_R2_backups_ttl",
    "test_R3_customer_ttl",
    "test_R4_financial_ttl",
    "test_R5_legal_hold_returns_none",
    "test_R5_hold_applies_to_any_category",
    "test_R6_saturday_rolls_forward",
    "test_R6_sunday_rolls_forward",
    "test_R7_unknown_category_raises",
    "test_R8_malformed_created_date_raises",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-28-retention-expiry.py <solution.py>\n")
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


class RetentionExpiryTests(unittest.TestCase):
    def test_R1_logs_ttl(self):
        self.assertEqual(FN("2024-03-05", "logs"), "2024-06-03")   # +90 days, no roll

    def test_R2_backups_ttl(self):
        self.assertEqual(FN("2024-01-08", "backups"), "2025-01-07")  # +365 days, no roll

    def test_R3_customer_ttl(self):
        self.assertEqual(FN("2024-01-02", "customer"), "2027-01-01")  # +1095 days, no roll

    def test_R4_financial_ttl(self):
        # Flat day count: NOT seven calendar years (leap days are not inserted).
        self.assertEqual(FN("2020-01-15", "financial"), "2027-01-13")

    def test_R5_legal_hold_returns_none(self):
        self.assertIsNone(FN("2024-03-05", "logs", True))
        self.assertIsNone(FN("2020-01-15", "financial", True))

    def test_R5_hold_applies_to_any_category(self):
        # Even records whose expiry would land on a weekend stay frozen.
        self.assertIsNone(FN("2024-01-05", "backups", True))
        self.assertIsNone(FN("2024-01-08", "logs", True))

    def test_R6_saturday_rolls_forward(self):
        # 2024-01-05 + 365 days lands on Saturday 2025-01-04.
        self.assertEqual(FN("2024-01-05", "backups"), "2025-01-06")

    def test_R6_sunday_rolls_forward(self):
        # 2024-01-08 + 90 days lands on Sunday 2024-04-07.
        self.assertEqual(FN("2024-01-08", "logs"), "2024-04-08")

    def test_R7_unknown_category_raises(self):
        with self.assertRaises(ValueError):
            FN("2024-01-01", "emails")
        # Validation happens before the hold is honoured.
        with self.assertRaises(ValueError):
            FN("2024-01-01", "temp", True)

    def test_R8_malformed_created_date_raises(self):
        for bad in ("not-a-date", "2024/01/01", None, 20240101):
            with self.assertRaises(ValueError):
                FN(bad, "logs")


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        RetentionExpiryTests(name).run(result)
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
