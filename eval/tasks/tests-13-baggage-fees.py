"""Hidden-spec tests for task 13 - T1-baggage-fees.

Stdlib only, no pytest. Usage:
    python tests-13-baggage-fees.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "baggage_fees"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_carry_on_fees",
    "test_R2_checked_escalator",
    "test_R2_bags_beyond_second",
    "test_R3_overweight_fee",
    "test_R3_weight_limit_boundary",
    "test_R4_refusal_over_32kg",
    "test_R5_loyalty_waivers",
    "test_R5_waiver_keeps_escalator_position",
    "test_R6_prepay_discount",
    "test_R7_invalid_inputs_return_sentinel",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-13-baggage-fees.py <solution.py>\n")
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


def fees(carry_ons, checked, heaviest_kg, tier, prepaid=False):
    return FN(carry_ons, checked, heaviest_kg, tier, prepaid)


class BaggageFeesTests(unittest.TestCase):
    def assertFees(self, expected, carry_ons, checked, heaviest_kg, tier, prepaid=False):
        self.assertAlmostEqual(
            fees(carry_ons, checked, heaviest_kg, tier, prepaid), expected, delta=0.005
        )

    def test_R1_carry_on_fees(self):
        self.assertFees(0.00, 1, 0, 10.0, "none")    # first carry-on free
        self.assertFees(35.00, 2, 0, 10.0, "none")   # second carry-on costs
        self.assertFees(35.00, 2, 0, 10.0, "gold")   # status never waives carry-ons

    def test_R2_checked_escalator(self):
        self.assertFees(40.00, 0, 1, 20.0, "none")   # first bag 40.00
        self.assertFees(95.00, 0, 2, 20.0, "none")   # second bag 55.00

    def test_R2_bags_beyond_second(self):
        self.assertFees(185.00, 0, 3, 20.0, "none")  # third bag 90.00
        self.assertFees(275.00, 0, 4, 20.0, "none")  # fourth bag another 90.00

    def test_R3_overweight_fee(self):
        self.assertFees(115.00, 0, 1, 25.0, "none")  # 40.00 plus 75.00
        self.assertFees(115.00, 0, 1, 23.1, "none")  # just over the limit counts

    def test_R3_weight_limit_boundary(self):
        self.assertFees(40.00, 0, 1, 23.0, "none")   # exactly 23 kg is not overweight
        self.assertFees(40.00, 0, 1, 20.0, "none")

    def test_R4_refusal_over_32kg(self):
        self.assertFees(115.00, 0, 1, 32.0, "none")  # exactly 32 kg still flies
        self.assertFees(-1.0, 0, 1, 32.5, "none")    # heavier is refused outright

    def test_R5_loyalty_waivers(self):
        self.assertFees(55.00, 0, 2, 20.0, "silver")  # first bag free, second pays
        self.assertFees(145.00, 0, 3, 20.0, "silver")
        self.assertFees(0.00, 0, 2, 20.0, "gold")     # first two bags free
        self.assertFees(90.00, 0, 3, 20.0, "gold")    # third bag still pays
        self.assertFees(0.00, 0, 2, 20.0, "GOLD")     # tier name is case-insensitive

    def test_R5_waiver_keeps_escalator_position(self):
        # The waived bag is the 40.00 bag; the paying bag is priced as a second bag.
        self.assertFees(55.00, 0, 2, 20.0, "silver")

    def test_R6_prepay_discount(self):
        self.assertFees(76.00, 0, 2, 20.0, "none", True)    # 20% off 95.00
        self.assertFees(148.00, 0, 3, 20.0, "none", True)   # 20% off 185.00
        self.assertFees(44.00, 0, 2, 20.0, "silver", True)  # 20% off the 55.00 left
        self.assertFees(142.00, 2, 1, 25.0, "none", True)   # overweight fee not discounted

    def test_R7_invalid_inputs_return_sentinel(self):
        for carry_ons in (-1, 3, "1", True):
            self.assertAlmostEqual(fees(carry_ons, 0, 10.0, "none"), -1.0, delta=0.005)
        for checked in (-2, 1.5, False):
            self.assertAlmostEqual(fees(0, checked, 10.0, "none"), -1.0, delta=0.005)
        for kg in (0, -5, "10"):
            self.assertAlmostEqual(fees(0, 0, kg, "none"), -1.0, delta=0.005)
        self.assertAlmostEqual(fees(0, 0, 10.0, "platinum"), -1.0, delta=0.005)
        self.assertAlmostEqual(fees(0, 0, 10.0, "none", "yes"), -1.0, delta=0.005)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        BaggageFeesTests(name).run(result)
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
