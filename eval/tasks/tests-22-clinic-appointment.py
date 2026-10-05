"""Hidden-spec tests for task 22 - T1-clinic-appointment.

Stdlib only, no pytest. Usage:
    python tests-22-clinic-appointment.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "update_appointment"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
TEST_ORDER = [
    "test_R1_checkin_window_opens",
    "test_R2_ontime_checkin",
    "test_R2_late_arrival_boundary",
    "test_R3_forward_progression",
    "test_R3_progression_needs_predecessor",
    "test_R4_noshow_cutoff",
    "test_R5_cancel_cutoff",
    "test_R6_terminal_states",
    "test_R7_unmapped_pairs",
    "test_R8_unknown_names",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-22-clinic-appointment.py <solution.py>\n")
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


class ClinicAppointmentTests(unittest.TestCase):
    def test_R1_checkin_window_opens(self):
        self.assertEqual(FN("booked", "check_in", 45), "booked")
        self.assertEqual(FN("booked", "check_in", 31), "booked")
        self.assertEqual(FN("booked", "check_in", 30), "checked_in")

    def test_R2_ontime_checkin(self):
        self.assertEqual(FN("booked", "check_in", 10), "checked_in")
        self.assertEqual(FN("booked", "check_in", 0), "checked_in")

    def test_R2_late_arrival_boundary(self):
        self.assertEqual(FN("booked", "check_in", -15), "checked_in")
        self.assertEqual(FN("booked", "check_in", -16), "no_show")
        self.assertEqual(FN("booked", "check_in", -60), "no_show")

    def test_R3_forward_progression(self):
        self.assertEqual(FN("checked_in", "start_visit", 0), "in_room")
        self.assertEqual(FN("in_room", "complete", 0), "completed")

    def test_R3_progression_needs_predecessor(self):
        self.assertEqual(FN("booked", "complete", 0), "booked")
        self.assertEqual(FN("checked_in", "complete", 0), "checked_in")

    def test_R4_noshow_cutoff(self):
        self.assertEqual(FN("booked", "mark_no_show", 1), "booked")
        self.assertEqual(FN("booked", "mark_no_show", 0), "no_show")
        self.assertEqual(FN("booked", "mark_no_show", -30), "no_show")

    def test_R5_cancel_cutoff(self):
        self.assertEqual(FN("booked", "cancel", 1), "cancelled")
        self.assertEqual(FN("booked", "cancel", 0), "booked")
        self.assertEqual(FN("booked", "cancel", -5), "booked")

    def test_R6_terminal_states(self):
        self.assertEqual(FN("completed", "check_in", 0), "completed")
        self.assertEqual(FN("cancelled", "cancel", 10), "cancelled")
        self.assertEqual(FN("no_show", "mark_no_show", 0), "no_show")
        self.assertEqual(FN("completed", "start_visit", 0), "completed")

    def test_R7_unmapped_pairs(self):
        self.assertEqual(FN("checked_in", "cancel", 10), "checked_in")
        self.assertEqual(FN("booked", "start_visit", 0), "booked")
        self.assertEqual(FN("checked_in", "check_in", 0), "checked_in")
        self.assertEqual(FN("in_room", "cancel", 0), "in_room")

    def test_R8_unknown_names(self):
        self.assertEqual(FN("booked", "CHECK_IN", 0), "booked")
        self.assertEqual(FN("rescheduled", "cancel", 10), "rescheduled")
        self.assertEqual(FN("booked", "reschedule", 10), "booked")


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        ClinicAppointmentTests(name).run(result)
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
