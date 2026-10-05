"""Hidden-spec tests for task 16 - T1-postal-code.

Stdlib only, no pytest. Usage:
    python tests-16-postal-code.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import types
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "is_valid_postal_code"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_supported_markets",
    "test_R1_unknown_markets",
    "test_R2_norvalia_shape",
    "test_R2_norvalia_counts",
    "test_R3_territory_suffixes",
    "test_R4_kestria_shape",
    "test_R4_kestria_zero_district",
    "test_R5_zubria_format",
    "test_R6_whitespace_as_typed",
    "test_R7_case_handling",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-16-postal-code.py <solution.py>\n")
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


class PostalCodeTests(unittest.TestCase):
    def test_R1_supported_markets(self):
        self.assertIs(FN("2214 HB", "NV"), True)
        self.assertIs(FN("AB-1234", "KE"), True)
        self.assertIs(FN("123456", "ZR"), True)

    def test_R1_unknown_markets(self):
        self.assertIs(FN("12345", "US"), False)
        self.assertIs(FN("2214 HB", "XX"), False)
        self.assertIs(FN("123456", ""), False)

    def test_R2_norvalia_shape(self):
        self.assertIs(FN("2214 HB", "NV"), True)
        self.assertIs(FN("2214 H9", "NV"), False)   # digit in the letter zone
        self.assertIs(FN("22A4 HB", "NV"), False)   # letter in the digit zone

    def test_R2_norvalia_counts(self):
        self.assertIs(FN("214 HB", "NV"), False)    # three digits
        self.assertIs(FN("22144 HB", "NV"), False)  # five digits
        self.assertIs(FN("2214 HBB", "NV"), False)  # three letters

    def test_R3_territory_suffixes(self):
        self.assertIs(FN("2214 QB", "NV"), False)   # reserved opening
        self.assertIs(FN("2214 XH", "NV"), False)   # reserved opening
        self.assertIs(FN("2214 HQ", "NV"), True)    # second position is fine
        self.assertIs(FN("2214 HX", "NV"), True)    # second position is fine

    def test_R4_kestria_shape(self):
        self.assertIs(FN("AB-1234", "KE"), True)
        self.assertIs(FN("A-1234", "KE"), False)    # one letter
        self.assertIs(FN("AB1-234", "KE"), False)   # three letters

    def test_R4_kestria_zero_district(self):
        self.assertIs(FN("AB-0123", "KE"), False)   # district 0 never existed
        self.assertIs(FN("AB-9012", "KE"), True)

    def test_R5_zubria_format(self):
        self.assertIs(FN("123456", "ZR"), True)
        self.assertIs(FN("023456", "ZR"), False)    # province 0
        self.assertIs(FN("723456", "ZR"), False)    # province 7
        self.assertIs(FN("12345", "ZR"), False)     # five digits

    def test_R6_whitespace_as_typed(self):
        self.assertIs(FN(" 2214 HB", "NV"), False)
        self.assertIs(FN("2214 HB ", "NV"), False)
        self.assertIs(FN("2214-HB", "NV"), False)   # wrong separator, not a space
        self.assertIs(FN("AB-12 34", "KE"), False)  # Kestria never has a space

    def test_R7_case_handling(self):
        self.assertIs(FN("2214 hb", "NV"), False)
        self.assertIs(FN("ab-1234", "KE"), False)
        self.assertIs(FN("2214 HB", "nv"), True)    # country match is lenient
        self.assertIs(FN("2214 HB", "Nv"), True)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        PostalCodeTests(name).run(result)
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
