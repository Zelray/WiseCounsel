"""Hidden-spec tests for task 10 - T1-electricity-tier-bill.

Stdlib only, no pytest. Usage:
    python tests-10-electricity-tier-bill.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "electricity_bill"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_first_block_rate",
    "test_R1_all_blocks_marginal",
    "test_R2_boundary_at_500",
    "test_R2_boundary_at_1000",
    "test_R3_fixed_charge_even_at_zero_usage",
    "test_R4_prorated_fixed_charge",
    "test_R4_divisor_always_30",
    "test_R5_tax_base_includes_fixed_charge",
    "test_R6_tax_rounded_before_adding",
    "test_R7_invalid_inputs_raise",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-10-electricity-tier-bill.py <solution.py>\n")
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


def bill(kwh, days):
    return FN(kwh, days)


class ElectricityBillTests(unittest.TestCase):
    def assertBill(self, expected, kwh, days):
        self.assertAlmostEqual(bill(kwh, days), expected, delta=0.005)

    def test_R1_first_block_rate(self):
        self.assertBill(48.50, 300, 30)   # 36.00 energy
        self.assertBill(73.94, 500, 30)   # 60.00 energy, all in block one

    def test_R1_all_blocks_marginal(self):
        self.assertBill(195.84, 1200, 30)  # 60.00 + 75.00 + 40.00 energy
        self.assertBill(113.69, 750, 30)   # 60.00 + 37.50 energy

    def test_R2_boundary_at_500(self):
        self.assertBill(73.94, 500, 30)   # the 500th kWh still at the cheap rate
        self.assertBill(74.09, 501, 30)   # the 501st kWh is the first expensive one

    def test_R2_boundary_at_1000(self):
        self.assertBill(153.44, 1000, 30)
        self.assertBill(153.65, 1001, 30)  # the 1001st kWh at the top rate

    def test_R3_fixed_charge_even_at_zero_usage(self):
        self.assertBill(10.34, 0, 30)     # 9.75 fixed charge plus tax on it alone

    def test_R4_prorated_fixed_charge(self):
        self.assertBill(5.17, 0, 15)      # half a period: 4.875 rounds to 4.88
        self.assertBill(56.05, 400, 15)

    def test_R4_divisor_always_30(self):
        self.assertBill(23.40, 100, 31)   # 31-day cycle still divides by 30

    def test_R5_tax_base_includes_fixed_charge(self):
        self.assertBill(48.50, 300, 30)   # tax on 45.75, not on 36.00 alone
        self.assertBill(113.69, 750, 30)  # tax on 147.75, not on 112.50 alone

    def test_R6_tax_rounded_before_adding(self):
        self.assertBill(73.94, 500, 30)   # tax 4.185 rounds to 4.19, then adds
        self.assertBill(48.50, 300, 30)   # tax 2.745 rounds to 2.75, then adds

    def test_R7_invalid_inputs_raise(self):
        for kwh in (-5, "100", None, True):
            with self.assertRaises(ValueError):
                bill(kwh, 30)
        for days in (30.5, 0, -2, "30"):
            with self.assertRaises(ValueError):
                bill(100, days)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        ElectricityBillTests(name).run(result)
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
