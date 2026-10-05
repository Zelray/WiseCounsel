"""Hidden-spec tests for task 19 - T1-subscription-lifecycle.

Stdlib only, no pytest. Usage:
    python tests-19-subscription-lifecycle.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "advance_subscription"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
TEST_ORDER = [
    "test_R1_trial_convert",
    "test_R2_cancel_from_trial_or_active",
    "test_R3_failed_charge_starts_dunning",
    "test_R4_recovery_grace_boundary",
    "test_R5_retry_grace_boundary",
    "test_R6_reactivation_window",
    "test_R6_reactivation_too_late",
    "test_R7_expired_terminal",
    "test_R8_unmapped_pairs_unchanged",
    "test_R8_unknown_names_unchanged",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-19-subscription-lifecycle.py <solution.py>\n")
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


class SubscriptionLifecycleTests(unittest.TestCase):
    def test_R1_trial_convert(self):
        self.assertEqual(FN("trial", "convert", 0), "active")
        self.assertEqual(FN("trial", "convert", 40), "active")

    def test_R2_cancel_from_trial_or_active(self):
        self.assertEqual(FN("trial", "cancel", 0), "canceled")
        self.assertEqual(FN("active", "cancel", 0), "canceled")

    def test_R3_failed_charge_starts_dunning(self):
        self.assertEqual(FN("active", "payment_failed", 0), "past_due")
        self.assertEqual(FN("active", "payment_failed", 60), "past_due")

    def test_R4_recovery_grace_boundary(self):
        self.assertEqual(FN("past_due", "payment_succeeded", 0), "active")
        self.assertEqual(FN("past_due", "payment_succeeded", 30), "active")
        self.assertEqual(FN("past_due", "payment_succeeded", 31), "expired")
        self.assertEqual(FN("past_due", "payment_succeeded", 100), "expired")

    def test_R5_retry_grace_boundary(self):
        self.assertEqual(FN("past_due", "payment_failed", 0), "past_due")
        self.assertEqual(FN("past_due", "payment_failed", 30), "past_due")
        self.assertEqual(FN("past_due", "payment_failed", 31), "expired")
        self.assertEqual(FN("past_due", "payment_failed", 90), "expired")

    def test_R6_reactivation_window(self):
        self.assertEqual(FN("canceled", "reactivate", 0), "active")
        self.assertEqual(FN("canceled", "reactivate", 14), "active")

    def test_R6_reactivation_too_late(self):
        self.assertEqual(FN("canceled", "reactivate", 15), "expired")
        self.assertEqual(FN("canceled", "reactivate", 90), "expired")

    def test_R7_expired_terminal(self):
        self.assertEqual(FN("expired", "reactivate", 0), "expired")
        self.assertEqual(FN("expired", "payment_succeeded", 0), "expired")
        self.assertEqual(FN("expired", "cancel", 0), "expired")
        self.assertEqual(FN("expired", "convert", 0), "expired")

    def test_R8_unmapped_pairs_unchanged(self):
        self.assertEqual(FN("trial", "payment_failed", 0), "trial")
        self.assertEqual(FN("active", "reactivate", 0), "active")
        self.assertEqual(FN("past_due", "cancel", 0), "past_due")

    def test_R8_unknown_names_unchanged(self):
        self.assertEqual(FN("paused", "convert", 0), "paused")
        self.assertEqual(FN("trial", "upgrade", 0), "trial")


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        SubscriptionLifecycleTests(name).run(result)
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
