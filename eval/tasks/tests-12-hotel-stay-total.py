"""Hidden-spec tests for task 12 - T1-hotel-stay-total.

Stdlib only, no pytest. Usage:
    python tests-12-hotel-stay-total.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "stay_total"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_peak_months_rate",
    "test_R1_shoulder_and_offseason_rate",
    "test_R1_start_month_pins_whole_stay",
    "test_R2_extra_guest_fee",
    "test_R3_cleaning_fee_flat",
    "test_R4_long_stay_threshold",
    "test_R4_discount_excludes_cleaning",
    "test_R5_tax_base_room_only",
    "test_R6_tax_rounded_half_up",
    "test_R7_invalid_inputs_return_sentinel",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-12-hotel-stay-total.py <solution.py>\n")
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


def total(nights, guests, month):
    return FN(nights, guests, month)


class HotelStayTotalTests(unittest.TestCase):
    def assertTotal(self, expected, nights, guests, month):
        self.assertAlmostEqual(total(nights, guests, month), expected, delta=0.005)

    def test_R1_peak_months_rate(self):
        # Clean case: one-night, two-guest peak stays - the peak months and the
        # 180.00 rate are printed on the rate card, and the levy is exact to the cent.
        self.assertTotal(256.20, 1, 2, 7)   # 180.00 room, 60.00 housekeeping, 16.20 levy
        self.assertTotal(256.20, 1, 1, 6)   # June is peak too; one guest prices the same

    def test_R1_shoulder_and_offseason_rate(self):
        # Clean case: same shape in the other two seasons - months and rates are
        # published, no extra guests, no long stay, no half-cent anywhere.
        self.assertTotal(218.05, 1, 2, 4)    # 145.00 room, 60.00 fee, 13.05 levy
        self.assertTotal(218.05, 1, 2, 10)   # October is shoulder
        self.assertTotal(179.90, 1, 2, 1)    # 110.00 room, 60.00 fee, 9.90 levy
        self.assertTotal(299.80, 2, 2, 3)    # March is quiet: 220.00, 60.00, 19.80

    def test_R1_start_month_pins_whole_stay(self):
        # Clean case: an end-of-August start prices BOTH nights at the peak rate
        # even though the stay rolls into September - the start month prices the
        # whole stay, exactly as the brief says.
        self.assertTotal(452.40, 2, 2, 8)   # 2 x 180.00 room, 60.00 fee, 32.40 levy

    def test_R2_extra_guest_fee(self):
        self.assertTotal(648.60, 3, 2, 7)    # two guests included
        self.assertTotal(689.48, 3, 3, 7)    # third guest: 12.50 per night
        self.assertTotal(730.35, 3, 4, 7)    # fourth guest too

    def test_R3_cleaning_fee_flat(self):
        # Clean case: the 60.00 fee is printed on the folio; short one- and
        # two-night stays for two guests show it charged once, not per night.
        self.assertTotal(179.90, 1, 2, 1)   # one night still carries the full 60.00
        self.assertTotal(299.80, 2, 2, 2)   # February is quiet: 220.00, 60.00, 19.80

    def test_R4_long_stay_threshold(self):
        self.assertTotal(1115.12, 10, 2, 1)  # 10 nights get the discount
        self.assertTotal(779.40, 6, 2, 1)    # 6 nights do not

    def test_R4_discount_excludes_cleaning(self):
        self.assertTotal(2170.24, 20, 2, 1)  # discount off room charge only

    def test_R5_tax_base_room_only(self):
        self.assertTotal(419.70, 3, 2, 1)    # tax on 330.00, not on 390.00
        self.assertTotal(1041.00, 5, 2, 7)   # tax on 900.00

    def test_R6_tax_rounded_half_up(self):
        self.assertTotal(689.48, 3, 3, 7)    # tax 51.975 rounds to 51.98
        self.assertTotal(918.38, 5, 3, 4)    # tax 70.875 rounds to 70.88

    def test_R7_invalid_inputs_return_sentinel(self):
        for nights in (0, 3.5, "3", None, True):
            self.assertAlmostEqual(total(nights, 2, 7), -1.0, delta=0.005)
        for guests in (0, 2.0, True):
            self.assertAlmostEqual(total(3, guests, 7), -1.0, delta=0.005)
        for month in (13, 0, True):
            self.assertAlmostEqual(total(3, 2, month), -1.0, delta=0.005)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        HotelStayTotalTests(name).run(result)
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
