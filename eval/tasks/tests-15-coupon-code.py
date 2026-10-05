"""Hidden-spec tests for task 15 - T1-coupon-code.

Stdlib only, no pytest. Usage:
    python tests-15-coupon-code.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.

Calibration note (2026-10-05): the ValueError-only posture and its message
keywords ('invalid' for non-string input, 'empty' for blank input) are stated in
the public brief; the hidden conventions (tag set, exact length, charset,
banned substrings, version digit) are each measured so a wrong guess costs at
most one test.
"""
import importlib.util
import sys
import types
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "validate_coupon_code"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_campaign_tags",
    "test_R2_exact_shape",
    "test_R2_hyphen_position",
    "test_R3_body_charset",
    "test_R3_tag_case",
    "test_R4_forbidden_substrings",
    "test_R5_version_digit",
    "test_R6_non_string_invalid",
    "test_R6_never_other_exception",
    "test_R7_blank_raises",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-15-coupon-code.py <solution.py>\n")
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("solution", SOLUTION_PATH)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as error:  # a broken candidate degrades to a clean zero
        sys.stderr.write(
            "NOTE: solution failed to load (%s); scoring as zero.\n" % error
        )
        return types.ModuleType("solution")
    return module


_MODULE = _load_solution()
FN = getattr(_MODULE, FUNCTION_NAME, None)
if FN is None:
    sys.stderr.write(
        "NOTE: no function named %r found in the solution; scoring as zero.\n" % FUNCTION_NAME
    )


class CouponCodeTests(unittest.TestCase):
    def _expect_value_error(self, raw, keyword=None):
        with self.assertRaises(ValueError) as caught:
            FN(raw)
        if keyword is not None:
            self.assertIn(keyword, str(caught.exception).lower())

    def test_R1_campaign_tags(self):
        for tag in ("SPR", "SUM", "FAL", "WIN"):
            self.assertIs(FN("%s-7X4Q2" % tag), True)
        self._expect_value_error("AUT-7X4Q2")    # near miss on the fall tag
        self._expect_value_error("NEW-7X4Q2")    # not one of ours
        self._expect_value_error("SUMR-7X4Q2")   # near miss on the summer tag

    def test_R2_exact_shape(self):
        self.assertIs(FN("SPR-7X4Q2"), True)    # three + hyphen + five = nine
        self._expect_value_error("SPR-7X4Q")    # eight characters
        self._expect_value_error("SPR-7X4Q22")  # ten characters

    def test_R2_hyphen_position(self):
        self._expect_value_error("SPR7X4Q2")    # no hyphen at all
        self._expect_value_error("SPR7-X4Q2")   # hyphen one slot late
        self.assertIs(FN("SPR-7X4Q2"), True)

    def test_R3_body_charset(self):
        self.assertIs(FN("SPR-24779"), True)     # all digits is fine
        self._expect_value_error("SPR-24a77")    # lowercase body
        self._expect_value_error("SPR-2A7-9")    # a second symbol

    def test_R3_tag_case(self):
        self._expect_value_error("spr-7X4Q2")    # lowercase tag
        self._expect_value_error("Spr-7X4Q2")    # mixed-case tag
        self.assertIs(FN("SPR-7X4Q2"), True)

    def test_R4_forbidden_substrings(self):
        self._expect_value_error("SPR-VOID8")
        self._expect_value_error("SPR-FREE4")
        self.assertIs(FN("SPR-VOI58"), True)     # near miss is fine
        self.assertIs(FN("SPR-FRE53"), True)     # near miss is fine

    def test_R5_version_digit(self):
        self.assertIs(FN("SUM-8XY41"), True)
        self._expect_value_error("SUM-8XY4A")    # body ends in a letter
        self._expect_value_error("FAL-9QW2Z")

    def test_R6_non_string_invalid(self):
        self._expect_value_error(None, "invalid")
        self._expect_value_error(123456789, "invalid")
        self._expect_value_error(["SPR-7X4Q2"], "invalid")
        self._expect_value_error(b"SPR-7X4Q2", "invalid")

    def test_R6_never_other_exception(self):
        for bad in ({}, 3.14, True, object()):
            try:
                FN(bad)
            except ValueError as caught:
                self.assertIn("invalid", str(caught).lower())
            except Exception as error:  # the contract names ValueError, nothing else
                self.fail("expected ValueError for %r, got %s" % (bad, type(error).__name__))
            else:
                self.fail("expected ValueError for %r, got a return" % (bad,))

    def test_R7_blank_raises(self):
        self._expect_value_error("", "empty")
        self._expect_value_error("   ", "empty")
        self._expect_value_error("\t\n", "empty")


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        CouponCodeTests(name).run(result)
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
