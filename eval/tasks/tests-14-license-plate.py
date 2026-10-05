"""Hidden-spec tests for task 14 - T1-license-plate.

Stdlib only, no pytest. Usage:
    python tests-14-license-plate.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.

Calibration note (2026-10-05): the error posture (never raise, non-str -> False)
and the no-trim rule are stated in the public brief; the hidden conventions
(serial shapes, I/O/Q ban, DP/CX prefixes, vintage series, uppercase embossing)
are each measured so a wrong guess costs at most one test.
"""
import importlib.util
import sys
import types
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "is_valid_plate"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_modern_shape",
    "test_R1_no_separators",
    "test_R2_confusable_letters_rejected",
    "test_R2_clean_letters_accepted",
    "test_R3_reserved_prefixes_rejected",
    "test_R3_lookalike_prefixes_accepted",
    "test_R4_vintage_series",
    "test_R5_lowercase_rejected",
    "test_R6_padding_not_trimmed",
    "test_R7_non_string_returns_false",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-14-license-plate.py <solution.py>\n")
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


class LicensePlateTests(unittest.TestCase):
    def test_R1_modern_shape(self):
        self.assertIs(FN("HBK2214"), True)     # three letters, four digits
        self.assertIs(FN("HBK221"), False)     # one digit short
        self.assertIs(FN("HBK22144"), False)   # one digit over

    def test_R1_no_separators(self):
        self.assertIs(FN("HBK-2214"), False)
        self.assertIs(FN("HBK 2214"), False)

    def test_R2_confusable_letters_rejected(self):
        self.assertIs(FN("HBQ2214"), False)    # Q reads as 0
        self.assertIs(FN("HBO2214"), False)    # O reads as 0
        self.assertIs(FN("IBK2214"), False)    # I reads as 1

    def test_R2_clean_letters_accepted(self):
        self.assertIs(FN("HBZ2214"), True)
        self.assertIs(FN("PKW4409"), True)     # no confusables anywhere

    def test_R3_reserved_prefixes_rejected(self):
        self.assertIs(FN("DPK2214"), False)    # disabled-veteran opening
        self.assertIs(FN("CXK2214"), False)    # commercial-fleet opening

    def test_R3_lookalike_prefixes_accepted(self):
        self.assertIs(FN("DBK2214"), True)     # D followed by other letters is fine
        self.assertIs(FN("CYK2214"), True)     # near miss on the second letter

    def test_R4_vintage_series(self):
        self.assertIs(FN("KM2214"), True)      # two letters + four digits, pre-1987
        self.assertIs(FN("K22144"), False)     # one letter + five digits never existed
        self.assertIs(FN("KM221"), False)      # two letters + three digits, too short

    def test_R5_lowercase_rejected(self):
        self.assertIs(FN("hbk2214"), False)
        self.assertIs(FN("Hbk2214"), False)
        self.assertIs(FN("HBk2214"), False)

    def test_R6_padding_not_trimmed(self):
        self.assertIs(FN(" HBK2214"), False)
        self.assertIs(FN("HBK2214 "), False)
        self.assertIs(FN("\tHBK2214"), False)

    def test_R7_non_string_returns_false(self):
        for bad in (None, 22142214, ["HBK2214"], b"HBK2214", True):
            self.assertIs(FN(bad), False)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        LicensePlateTests(name).run(result)
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
