"""Hidden-spec tests for task 18 - T1-seat-map.

Stdlib only, no pytest. Usage:
    python tests-18-seat-map.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import types
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "parse_seat"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_joined_notation",
    "test_R1_rejects_variants",
    "test_R2_row_range",
    "test_R2_skipped_letters",
    "test_R3_front_capacity",
    "test_R3_rear_capacity",
    "test_R4_no_seat_thirteen",
    "test_R5_wheelchair_ends",
    "test_R6_unparseable_never_raises",
    "test_R7_numbering_style",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-18-seat-map.py <solution.py>\n")
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


class SeatMapTests(unittest.TestCase):
    def test_R1_joined_notation(self):
        self.assertEqual(FN("J14"), ("J", 14))
        self.assertEqual(FN("B7"), ("B", 7))

    def test_R1_rejects_variants(self):
        self.assertIsNone(FN("J 14"))
        self.assertIsNone(FN("J-14"))
        self.assertIsNone(FN("j14"))
        self.assertIsNone(FN("JJ14"))

    def test_R2_row_range(self):
        self.assertEqual(FN("A1"), ("A", 1))
        self.assertEqual(FN("S21"), ("S", 21))
        self.assertIsNone(FN("U5"))    # past T
        self.assertIsNone(FN("Z9"))    # past T

    def test_R2_skipped_letters(self):
        self.assertIsNone(FN("I5"))    # struck from the lettering
        self.assertIsNone(FN("O5"))    # struck from the lettering
        self.assertEqual(FN("H21"), ("H", 21))
        self.assertEqual(FN("J5"), ("J", 5))

    def test_R3_front_capacity(self):
        self.assertEqual(FN("D12"), ("D", 12))
        self.assertIsNone(FN("A15"))   # beyond the front rows' 14
        self.assertIsNone(FN("A20"))   # far beyond the front rows

    def test_R3_rear_capacity(self):
        self.assertEqual(FN("E21"), ("E", 21))
        self.assertEqual(FN("M21"), ("M", 21))
        self.assertIsNone(FN("E23"))   # beyond 22
        self.assertIsNone(FN("E30"))

    def test_R4_no_seat_thirteen(self):
        self.assertIsNone(FN("M13"))
        self.assertIsNone(FN("D13"))
        self.assertEqual(FN("M12"), ("M", 12))
        self.assertEqual(FN("M14"), ("M", 14))

    def test_R5_wheelchair_ends(self):
        self.assertIsNone(FN("A14"))   # last seat of a front row
        self.assertIsNone(FN("C14"))
        self.assertIsNone(FN("T22"))   # last seat of a rear row
        self.assertEqual(FN("A12"), ("A", 12))

    def test_R6_unparseable_never_raises(self):
        for junk in ("", "12A", "J", "9", "row J seat 4", None, 42, ["J14"]):
            self.assertIsNone(FN(junk))

    def test_R7_numbering_style(self):
        self.assertIsNone(FN("J0"))    # no seat 0
        self.assertIsNone(FN("J07"))   # no zero padding
        self.assertEqual(FN("J7"), ("J", 7))


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        SeatMapTests(name).run(result)
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
