"""Hidden-spec tests for task 20 - T1-vending-session.

Stdlib only, no pytest. Usage:
    python tests-20-vending-session.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "vend_step"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
TEST_ORDER = [
    "test_R1_coin_accumulates",
    "test_R1_coin_in_exact_mode",
    "test_R2_coin_slot_rejects_slop",
    "test_R2_nickel_is_smallest_coin",
    "test_R3_select_vends",
    "test_R4_select_insufficient",
    "test_R5_exact_mode_coin_gate",
    "test_R6_exact_mode_select",
    "test_R7_refund_path",
    "test_R8_dead_ends",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-20-vending-session.py <solution.py>\n")
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


class VendingSessionTests(unittest.TestCase):
    def test_R1_coin_accumulates(self):
        self.assertEqual(FN("idle", "coin", 25, 0, 100), ("collecting", 25))
        self.assertEqual(FN("collecting", "coin", 10, 25, 100), ("collecting", 35))
        self.assertEqual(FN("collecting", "coin", 25, 35, 100), ("collecting", 60))

    def test_R1_coin_in_exact_mode(self):
        self.assertEqual(FN("exact_change", "coin", 5, 50, 100), ("exact_change", 55))
        self.assertEqual(FN("exact_change", "coin", 10, 55, 100), ("exact_change", 65))

    def test_R2_coin_slot_rejects_slop(self):
        self.assertEqual(FN("collecting", "coin", 0, 50, 100), ("collecting", 50))
        self.assertEqual(FN("collecting", "coin", -25, 50, 100), ("collecting", 50))
        self.assertEqual(FN("collecting", "coin", 3, 50, 100), ("collecting", 50))

    def test_R2_nickel_is_smallest_coin(self):
        self.assertEqual(FN("idle", "coin", 1, 0, 100), ("idle", 0))
        self.assertEqual(FN("idle", "coin", 5, 0, 100), ("collecting", 5))

    def test_R3_select_vends(self):
        self.assertEqual(FN("collecting", "select", 0, 100, 100), ("dispensing", 0))
        self.assertEqual(FN("collecting", "select", 0, 130, 100), ("dispensing", 0))

    def test_R4_select_insufficient(self):
        self.assertEqual(FN("collecting", "select", 0, 75, 100), ("collecting", 75))
        self.assertEqual(FN("idle", "select", 0, 0, 100), ("idle", 0))

    def test_R5_exact_mode_coin_gate(self):
        self.assertEqual(FN("exact_change", "coin", 10, 90, 100), ("exact_change", 100))
        self.assertEqual(FN("exact_change", "coin", 25, 90, 100), ("exact_change", 90))

    def test_R6_exact_mode_select(self):
        self.assertEqual(FN("exact_change", "select", 0, 100, 100), ("dispensing", 0))
        self.assertEqual(FN("exact_change", "select", 0, 120, 100), ("exact_change", 120))

    def test_R7_refund_path(self):
        self.assertEqual(FN("collecting", "refund", 0, 60, 100), ("idle", 0))
        self.assertEqual(FN("exact_change", "refund", 0, 25, 100), ("idle", 0))
        self.assertEqual(FN("idle", "refund", 0, 0, 100), ("idle", 0))

    def test_R8_dead_ends(self):
        self.assertEqual(FN("dispensing", "coin", 25, 0, 100), ("dispensing", 0))
        self.assertEqual(FN("dispensing", "select", 0, 0, 100), ("dispensing", 0))
        self.assertEqual(FN("broken", "coin", 25, 0, 100), ("broken", 0))
        self.assertEqual(FN("collecting", "eject", 0, 50, 100), ("collecting", 50))


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        VendingSessionTests(name).run(result)
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
