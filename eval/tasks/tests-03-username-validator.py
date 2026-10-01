"""Hidden-spec tests for task 03 - T1-username-validator.

Stdlib only, no pytest. Usage:
    python tests-03-username-validator.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "validate_username"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_min_length",
    "test_R1_max_length",
    "test_R2_allowed_charset",
    "test_R2_rejects_other_characters",
    "test_R3_must_start_with_letter",
    "test_R4_reserved_names_case_insensitive",
    "test_R4_reserved_substring_allowed",
    "test_R5_padding_is_not_trimmed",
    "test_R6_repeated_runs",
    "test_R7_non_string_returns_false",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-03-username-validator.py <solution.py>\n")
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


class UsernameValidatorTests(unittest.TestCase):
    def test_R1_min_length(self):
        self.assertIs(FN("ab"), False)   # too short
        self.assertIs(FN("abc"), True)   # exactly at the floor

    def test_R1_max_length(self):
        self.assertIs(FN("ab" * 10), True)        # exactly at the ceiling
        self.assertIs(FN("ab" * 10 + "a"), False)  # one over the ceiling

    def test_R2_allowed_charset(self):
        self.assertIs(FN("a_b_9"), True)
        self.assertIs(FN("Zephyr_88"), True)

    def test_R2_rejects_other_characters(self):
        self.assertIs(FN("a-b"), False)
        self.assertIs(FN("a.b"), False)
        self.assertIs(FN("café"), False)   # non-ASCII letter
        self.assertIs(FN("a b"), False)

    def test_R3_must_start_with_letter(self):
        self.assertIs(FN("9abc"), False)
        self.assertIs(FN("_abc"), False)
        self.assertIs(FN("a9c"), True)

    def test_R4_reserved_names_case_insensitive(self):
        self.assertIs(FN("admin"), False)
        self.assertIs(FN("ROOT"), False)
        self.assertIs(FN("System"), False)

    def test_R4_reserved_substring_allowed(self):
        self.assertIs(FN("adminuser"), True)
        self.assertIs(FN("roots"), True)

    def test_R5_padding_is_not_trimmed(self):
        self.assertIs(FN("  bob"), False)
        self.assertIs(FN("bob  "), False)
        self.assertIs(FN(" bob "), False)

    def test_R6_repeated_runs(self):
        self.assertIs(FN("aabb"), True)
        self.assertIs(FN("aaab"), False)
        self.assertIs(FN("abbb"), False)

    def test_R7_non_string_returns_false(self):
        for bad in (None, 123, 12.5, ["bob"], b"bob", True):
            self.assertIs(FN(bad), False)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        UsernameValidatorTests(name).run(result)
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
