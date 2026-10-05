"""Hidden-spec tests for task 21 - T1-turnstile-gate.

Stdlib only, no pytest. Usage:
    python tests-21-turnstile-gate.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "turnstile_step"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
TEST_ORDER = [
    "test_R1_coin_unlocks",
    "test_R2_swipe_unlocks",
    "test_R3_push_relocks",
    "test_R4_push_on_locked",
    "test_R5_no_second_fare",
    "test_R6_timeout_boundary",
    "test_R6_timeout_from_locked",
    "test_R7_case_sensitive_events",
    "test_R8_unknown_events",
    "test_R8_unknown_states",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-21-turnstile-gate.py <solution.py>\n")
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


class TurnstileGateTests(unittest.TestCase):
    def test_R1_coin_unlocks(self):
        self.assertEqual(FN("locked", "coin", 0), "unlocked")
        self.assertEqual(FN("locked", "coin", 99), "unlocked")

    def test_R2_swipe_unlocks(self):
        self.assertEqual(FN("locked", "swipe", 0), "unlocked")

    def test_R3_push_relocks(self):
        self.assertEqual(FN("unlocked", "push", 0), "locked")

    def test_R4_push_on_locked(self):
        self.assertEqual(FN("locked", "push", 0), "locked")

    def test_R5_no_second_fare(self):
        self.assertEqual(FN("unlocked", "coin", 0), "unlocked")
        self.assertEqual(FN("unlocked", "swipe", 0), "unlocked")

    def test_R6_timeout_boundary(self):
        self.assertEqual(FN("unlocked", "timeout", 29), "unlocked")
        self.assertEqual(FN("unlocked", "timeout", 30), "locked")
        self.assertEqual(FN("unlocked", "timeout", 600), "locked")

    def test_R6_timeout_from_locked(self):
        self.assertEqual(FN("locked", "timeout", 120), "locked")

    def test_R7_case_sensitive_events(self):
        self.assertEqual(FN("locked", "SWIPE", 0), "locked")
        self.assertEqual(FN("locked", "Coin", 0), "locked")
        self.assertEqual(FN("unlocked", "Push", 0), "unlocked")

    def test_R8_unknown_events(self):
        self.assertEqual(FN("locked", "kick", 0), "locked")
        self.assertEqual(FN("unlocked", "kick", 0), "unlocked")

    def test_R8_unknown_states(self):
        self.assertEqual(FN("jammed", "coin", 0), "jammed")
        self.assertEqual(FN("jammed", "push", 0), "jammed")


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        TurnstileGateTests(name).run(result)
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
