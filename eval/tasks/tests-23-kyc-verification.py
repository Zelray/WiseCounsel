"""Hidden-spec tests for task 23 - T1-kyc-verification.

Stdlib only, no pytest. Usage:
    python tests-23-kyc-verification.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "advance_kyc"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
TEST_ORDER = [
    "test_R1_screen_moves_to_review",
    "test_R2_approval",
    "test_R3_rejection",
    "test_R4_request_docs",
    "test_R5_resubmit_within_cap",
    "test_R5_resubmit_cap_exhausted",
    "test_R6_terminal_decisions",
    "test_R7_unmapped_pairs",
    "test_R7_more_unmapped_pairs",
    "test_R8_unknown_names",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-23-kyc-verification.py <solution.py>\n")
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


class KycVerificationTests(unittest.TestCase):
    def test_R1_screen_moves_to_review(self):
        self.assertEqual(FN("pending", "screen", 0), "review")

    def test_R2_approval(self):
        self.assertEqual(FN("review", "approve", 0), "approved")

    def test_R3_rejection(self):
        self.assertEqual(FN("review", "reject", 0), "rejected")

    def test_R4_request_docs(self):
        self.assertEqual(FN("review", "request_docs", 0), "resubmit")

    def test_R5_resubmit_within_cap(self):
        self.assertEqual(FN("resubmit", "resubmit", 0), "pending")
        self.assertEqual(FN("resubmit", "resubmit", 1), "pending")

    def test_R5_resubmit_cap_exhausted(self):
        self.assertEqual(FN("resubmit", "resubmit", 2), "rejected")
        self.assertEqual(FN("resubmit", "resubmit", 3), "rejected")

    def test_R6_terminal_decisions(self):
        self.assertEqual(FN("approved", "screen", 0), "approved")
        self.assertEqual(FN("approved", "resubmit", 0), "approved")
        self.assertEqual(FN("rejected", "approve", 0), "rejected")
        self.assertEqual(FN("rejected", "resubmit", 5), "rejected")

    def test_R7_unmapped_pairs(self):
        self.assertEqual(FN("pending", "approve", 0), "pending")
        self.assertEqual(FN("pending", "reject", 0), "pending")
        self.assertEqual(FN("pending", "request_docs", 0), "pending")
        self.assertEqual(FN("review", "screen", 0), "review")

    def test_R7_more_unmapped_pairs(self):
        self.assertEqual(FN("resubmit", "approve", 0), "resubmit")
        self.assertEqual(FN("resubmit", "screen", 0), "resubmit")
        self.assertEqual(FN("resubmit", "request_docs", 0), "resubmit")

    def test_R8_unknown_names(self):
        self.assertEqual(FN("pending", "SCREEN", 0), "pending")
        self.assertEqual(FN("on_hold", "screen", 0), "on_hold")
        self.assertEqual(FN("pending", "escalate", 0), "pending")


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        KycVerificationTests(name).run(result)
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
