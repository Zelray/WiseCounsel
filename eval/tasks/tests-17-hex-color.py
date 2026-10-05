"""Hidden-spec tests for task 17 - T1-hex-color.

Stdlib only, no pytest. Usage:
    python tests-17-hex-color.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import types
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "is_valid_brand_color"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_accepted_notations",
    "test_R1_rejected_lengths",
    "test_R2_named_keywords",
    "test_R3_case_insensitive",
    "test_R4_reserved_tones",
    "test_R4_mid_gray_allowed",
    "test_R5_alpha_bounds",
    "test_R5_alpha_interior",
    "test_R6_non_string_returns_false",
    "test_R7_padding_not_trimmed",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-17-hex-color.py <solution.py>\n")
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


class HexColorTests(unittest.TestCase):
    def test_R1_accepted_notations(self):
        self.assertIs(FN("#F61"), True)        # short form
        self.assertIs(FN("#FF6F61"), True)     # long form
        self.assertIs(FN("#FF6F6180"), True)   # long form with alpha

    def test_R1_rejected_lengths(self):
        self.assertIs(FN("#F618"), False)      # the short-alpha #RGBA form
        self.assertIs(FN("FF6F61"), False)     # no leading hash
        self.assertIs(FN("#FF6F6"), False)     # five digits
        self.assertIs(FN("#FF6F611"), False)   # seven digits

    def test_R2_named_keywords(self):
        self.assertIs(FN("red"), False)
        self.assertIs(FN("aliceblue"), False)
        self.assertIs(FN("transparent"), False)

    def test_R3_case_insensitive(self):
        self.assertIs(FN("#ff6f61"), True)
        self.assertIs(FN("#fF6F61"), True)
        self.assertIs(FN("#f61"), True)

    def test_R4_reserved_tones(self):
        self.assertIs(FN("#000000"), False)
        self.assertIs(FN("#FFFFFF"), False)
        self.assertIs(FN("#000"), False)       # same tone, short spelling
        self.assertIs(FN("#00000080"), False)  # reserved even with alpha

    def test_R4_mid_gray_allowed(self):
        self.assertIs(FN("#808080"), True)
        self.assertIs(FN("#80808080"), True)

    def test_R5_alpha_bounds(self):
        self.assertIs(FN("#FF6F6100"), False)  # fully invisible
        self.assertIs(FN("#FF6F61FF"), False)  # fully opaque: use six digits

    def test_R5_alpha_interior(self):
        self.assertIs(FN("#FF6F6180"), True)
        self.assertIs(FN("#FF6F6101"), True)
        self.assertIs(FN("#FF6F61FE"), True)

    def test_R6_non_string_returns_false(self):
        for bad in (None, 0xFF6F61, ["#FF6F61"], b"#FF6F61", True):
            self.assertIs(FN(bad), False)

    def test_R7_padding_not_trimmed(self):
        self.assertIs(FN(" #FF6F61"), False)
        self.assertIs(FN("#FF6F61 "), False)
        self.assertIs(FN("\t#F61"), False)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        HexColorTests(name).run(result)
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
