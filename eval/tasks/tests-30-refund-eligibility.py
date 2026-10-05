"""Hidden-spec tests for task 30 - T1-refund-eligibility.

Stdlib only, no pytest. Usage:
    python tests-30-refund-eligibility.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.

Round-3 calibration: the two error-path conventions (strict condition enum raised
before every policy door, unknown category answered with the standard treatment)
are published in the brief; the probes below are de-coupled so a wrong guess on
one window value costs only the window tests - the grading probe sits on a day
every plausible window contains, and the opened-does-not-extend probe sits past
every plausible window.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "refund_eligibility"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_standard_window_inclusive",
    "test_R2_electronics_window",
    "test_R2_perishables_and_unknown_category",
    "test_R3_condition_grading",
    "test_R3_opened_never_extends_window",
    "test_R4_not_delivered_denied",
    "test_R5_defective_overrides_window",
    "test_R5_defective_ninety_day_cap",
    "test_R6_clearance_final_sale",
    "test_R7_unknown_condition_raises",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-30-refund-eligibility.py <solution.py>\n")
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


class RefundEligibilityTests(unittest.TestCase):
    def test_R1_standard_window_inclusive(self):
        self.assertEqual(FN("shoes", 30, "new"), "full")
        self.assertEqual(FN("shoes", 31, "new"), "denied")

    def test_R2_electronics_window(self):
        self.assertEqual(FN("electronics", 15, "new"), "full")
        self.assertEqual(FN("electronics", 16, "new"), "denied")

    def test_R2_perishables_and_unknown_category(self):
        self.assertEqual(FN("perishables", 7, "new"), "full")
        self.assertEqual(FN("perishables", 8, "new"), "denied")
        self.assertEqual(FN("furniture", 30, "new"), "full")

    def test_R3_condition_grading(self):
        # Day 3 sits inside every plausible window, so a wrong window guess cannot leak in here.
        self.assertEqual(FN("shoes", 3, "new"), "full")
        self.assertEqual(FN("shoes", 3, "opened"), "partial")

    def test_R3_opened_never_extends_window(self):
        # A year out is past any window guess there might be - opened buys no extension.
        self.assertEqual(FN("shoes", 365, "opened"), "denied")

    def test_R4_not_delivered_denied(self):
        self.assertEqual(FN("shoes", -1, "new"), "denied")
        self.assertEqual(FN("shoes", -5, "defective"), "denied")
        self.assertEqual(FN("shoes", 0, "new"), "full")

    def test_R5_defective_overrides_window(self):
        self.assertEqual(FN("electronics", 20, "defective"), "full")
        self.assertEqual(FN("perishables", 30, "defective"), "full")

    def test_R5_defective_ninety_day_cap(self):
        self.assertEqual(FN("shoes", 90, "defective"), "full")
        self.assertEqual(FN("shoes", 91, "defective"), "denied")

    def test_R6_clearance_final_sale(self):
        self.assertEqual(FN("clearance", 5, "new"), "denied")
        self.assertEqual(FN("clearance", 5, "defective"), "denied")
        self.assertEqual(FN("clearance", 0, "opened"), "denied")

    def test_R7_unknown_condition_raises(self):
        with self.assertRaises(ValueError):
            FN("shoes", 5, "damaged")
        with self.assertRaises(ValueError):
            FN("clearance", 5, "damaged")   # validation precedes the final-sale door
        with self.assertRaises(ValueError):
            FN("shoes", -1, "used")         # and precedes the delivery door


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        RefundEligibilityTests(name).run(result)
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
