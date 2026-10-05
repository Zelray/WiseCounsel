"""Hidden-spec tests for task 31 - T1-badge-eligibility.

Stdlib only, no pytest. Usage:
    python tests-31-badge-eligibility.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "badge_access"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_fails_closed_on_unknown_input",
    "test_R1_day_names_case_insensitive",
    "test_R2_employee_business_hours",
    "test_R3_contractor_hour_cap",
    "test_R3_contractor_zone_cap",
    "test_R4_lab_tier",
    "test_R4_server_admin_only",
    "test_R5_admin_master_key",
    "test_R6_weekend_lockout",
    "test_R7_senior_anytime_any_day",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-31-badge-eligibility.py <solution.py>\n")
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


class BadgeEligibilityTests(unittest.TestCase):
    def test_R1_fails_closed_on_unknown_input(self):
        self.assertIs(FN("visitor", "general", "monday", 10), False)
        self.assertIs(FN("employee", "roof", "monday", 10), False)
        self.assertIs(FN("employee", "general", "funday", 10), False)
        self.assertIs(FN("employee", "general", "monday", 24), False)
        self.assertIs(FN("employee", "general", "monday", -1), False)

    def test_R1_day_names_case_insensitive(self):
        self.assertIs(FN("employee", "general", "MONDAY", 10), True)
        self.assertIs(FN("employee", "general", "FriDay", 10), True)

    def test_R2_employee_business_hours(self):
        self.assertIs(FN("employee", "general", "monday", 6), True)
        self.assertIs(FN("employee", "general", "monday", 19), True)
        self.assertIs(FN("employee", "general", "monday", 5), False)
        self.assertIs(FN("employee", "general", "monday", 20), False)

    def test_R3_contractor_hour_cap(self):
        self.assertIs(FN("contractor", "general", "tuesday", 8), True)
        self.assertIs(FN("contractor", "general", "tuesday", 17), True)
        self.assertIs(FN("contractor", "general", "tuesday", 7), False)
        self.assertIs(FN("contractor", "general", "tuesday", 18), False)

    def test_R3_contractor_zone_cap(self):
        self.assertIs(FN("contractor", "general", "monday", 10), True)
        self.assertIs(FN("contractor", "lab", "monday", 10), False)
        self.assertIs(FN("contractor", "server", "monday", 10), False)

    def test_R4_lab_tier(self):
        self.assertIs(FN("senior", "lab", "sunday", 3), True)
        self.assertIs(FN("employee", "lab", "monday", 10), False)
        self.assertIs(FN("contractor", "lab", "monday", 10), False)

    def test_R4_server_admin_only(self):
        self.assertIs(FN("admin", "server", "sunday", 3), True)
        self.assertIs(FN("senior", "server", "monday", 10), False)
        self.assertIs(FN("employee", "server", "monday", 10), False)

    def test_R5_admin_master_key(self):
        self.assertIs(FN("admin", "general", "sunday", 3), True)
        self.assertIs(FN("admin", "lab", "monday", 23), True)
        self.assertIs(FN("admin", "server", "monday", 0), True)

    def test_R6_weekend_lockout(self):
        self.assertIs(FN("employee", "general", "saturday", 10), False)
        self.assertIs(FN("contractor", "general", "sunday", 12), False)

    def test_R7_senior_anytime_any_day(self):
        self.assertIs(FN("senior", "general", "sunday", 3), True)
        self.assertIs(FN("senior", "lab", "saturday", 22), True)
        self.assertIs(FN("senior", "general", "monday", 5), True)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        BadgeEligibilityTests(name).run(result)
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
