"""Hidden-spec tests for task 11 - T1-taxi-fare.

Stdlib only, no pytest. Usage:
    python tests-11-taxi-fare.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "taxi_fare"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_flag_drop_on_every_ride",
    "test_R2_day_rate_and_hours",
    "test_R2_night_rate_and_hours",
    "test_R3_distance_rounds_up_to_tenth",
    "test_R3_exact_tenths_bill_exactly",
    "test_R4_airport_flat_override",
    "test_R5_below_minimum_bumps_up",
    "test_R5_at_minimum_unchanged",
    "test_R6_fare_rounds_to_half_dollar",
    "test_R7_invalid_inputs_return_sentinel",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-11-taxi-fare.py <solution.py>\n")
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


def fare(distance_miles, start_hour, airport=False):
    return FN(distance_miles, start_hour, airport)


class TaxiFareTests(unittest.TestCase):
    def assertFare(self, expected, distance_miles, start_hour, airport=False):
        self.assertAlmostEqual(fare(distance_miles, start_hour, airport), expected, delta=0.005)

    def test_R1_flag_drop_on_every_ride(self):
        self.assertFare(8.00, 0, 12)       # flag drop alone, bumped to the minimum
        self.assertFare(15.50, 5.0, 12)    # 3.00 drop inside a 12.50 ride

    def test_R2_day_rate_and_hours(self):
        self.assertFare(15.50, 5.0, 14)    # 2.50 per mile by day
        self.assertFare(8.00, 2.0, 5)      # hour 5 is already day
        self.assertFare(8.00, 2.0, 21)     # hour 21 is still day

    def test_R2_night_rate_and_hours(self):
        self.assertFare(18.50, 5.0, 23)    # 3.10 per mile by night
        self.assertFare(9.00, 2.0, 22)     # hour 22 is night
        self.assertFare(9.00, 2.0, 4)      # hour 4 is still night
        self.assertFare(9.00, 2.0, 0)      # midnight is night

    def test_R3_distance_rounds_up_to_tenth(self):
        self.assertFare(11.50, 3.24, 12)   # bills as 3.3 miles
        self.assertFare(11.50, 3.21, 12)   # still 3.3 miles

    def test_R3_exact_tenths_bill_exactly(self):
        self.assertFare(8.50, 2.1, 12)     # exactly 2.1 miles
        self.assertFare(15.50, 5.0, 14)    # exactly 5.0 miles

    def test_R4_airport_flat_override(self):
        self.assertFare(42.00, 2.5, 3, True)   # flat beats the night rate
        self.assertFare(42.00, 0.3, 22, True)  # flat at any distance, no minimum math

    def test_R5_below_minimum_bumps_up(self):
        self.assertFare(8.00, 1.8, 12)     # metered 7.50 rides at 8.00
        self.assertFare(8.00, 0, 12)       # flag drop alone rides at 8.00

    def test_R5_at_minimum_unchanged(self):
        self.assertFare(8.00, 2.0, 12)     # metered exactly 8.00
        self.assertFare(8.50, 2.1, 12)     # metered 8.25, tie rounds up

    def test_R6_fare_rounds_to_half_dollar(self):
        self.assertFare(10.00, 2.2, 23)    # metered 9.82 rounds to 10.00
        self.assertFare(8.50, 2.1, 12)     # metered 8.25 ties upward

    def test_R7_invalid_inputs_return_sentinel(self):
        for distance in (-1, "5", None, True):
            self.assertAlmostEqual(fare(distance, 12), -1.0, delta=0.005)
        for hour in (24, -1, True, 12.0, "12"):
            self.assertAlmostEqual(fare(5.0, hour), -1.0, delta=0.005)
        self.assertAlmostEqual(fare(5.0, 12, "yes"), -1.0, delta=0.005)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        TaxiFareTests(name).run(result)
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
