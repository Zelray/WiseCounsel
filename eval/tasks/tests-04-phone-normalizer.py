"""Hidden-spec tests for task 04 - T1-phone-normalizer.

Stdlib only, no pytest. Usage:
    python tests-04-phone-normalizer.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "normalize_phone"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_blank_none_no_digits",
    "test_R2_letters_rejected",
    "test_R3_extension_appended",
    "test_R3_extension_bounds",
    "test_R4_ten_digit_exact",
    "test_R4_separator_shapes",
    "test_R5_leading_one",
    "test_R5_one_with_extension",
    "test_R6_too_short",
    "test_R7_too_long",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-04-phone-normalizer.py <solution.py>\n")
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


class PhoneNormalizerTests(unittest.TestCase):
    def _expect_value_error(self, raw, keyword):
        with self.assertRaises(ValueError) as caught:
            FN(raw)
        self.assertIn(keyword, str(caught.exception).lower())

    def test_R1_blank_none_no_digits(self):
        self._expect_value_error(None, "empty")
        self._expect_value_error("", "empty")
        self._expect_value_error("   ", "empty")
        self._expect_value_error("---", "empty")

    def test_R2_letters_rejected(self):
        self._expect_value_error("call 555-867-5309", "letters")
        self._expect_value_error("555x8675309", "letters")

    def test_R3_extension_appended(self):
        self.assertEqual(FN("5558675309 x123"), "(555) 867-5309, ext. 123")
        self.assertEqual(FN("555-867-5309 ext. 42"), "(555) 867-5309, ext. 42")

    def test_R3_extension_bounds(self):
        self._expect_value_error("5558675309 x", "extension")
        self._expect_value_error("5558675309 x123456", "extension")

    def test_R4_ten_digit_exact(self):
        self.assertEqual(FN("5558675309"), "(555) 867-5309")

    def test_R4_separator_shapes(self):
        for raw in ("555.867.5309", "(555) 867-5309", "555 867 5309", "555----867..5309"):
            self.assertEqual(FN(raw), "(555) 867-5309")

    def test_R5_leading_one(self):
        self.assertEqual(FN("15558675309"), "(555) 867-5309")
        self.assertEqual(FN("+1 (555) 867-5309"), "(555) 867-5309")

    def test_R5_one_with_extension(self):
        self.assertEqual(FN("1-555-867-5309 x456"), "(555) 867-5309, ext. 456")

    def test_R6_too_short(self):
        self._expect_value_error("555867530", "short")
        self._expect_value_error("12345", "short")

    def test_R7_too_long(self):
        self._expect_value_error("555867530912", "long")
        self._expect_value_error("25558675309", "long")


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        PhoneNormalizerTests(name).run(result)
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
