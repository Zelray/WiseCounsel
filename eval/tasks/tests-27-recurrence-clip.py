"""Hidden-spec tests for task 27 - T1-recurrence-clip.

Stdlib only, no pytest. Usage:
    python tests-27-recurrence-clip.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "recurrence_clip"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
TEST_ORDER = [
    "test_R1_anchor_is_first_occurrence",
    "test_R2_weekly_cadence",
    "test_R3_count_caps_series",
    "test_R3_count_zero_or_negative",
    "test_R4_window_start_edge_inclusive",
    "test_R4_window_end_edge_exclusive",
    "test_R5_ascending_order",
    "test_R6_window_miss_yields_empty_list",
    "test_R7_reversed_window_yields_empty_list",
    "test_R8_malformed_dates_raise",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-27-recurrence-clip.py <solution.py>\n")
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("solution", SOLUTION_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    _MODULE = _load_solution()
except Exception:
    _MODULE = None
FN = getattr(_MODULE, FUNCTION_NAME, None)
if FN is None:
    sys.stderr.write(
        "NOTE: no function named %r found in the solution; scoring as zero.\n" % FUNCTION_NAME
    )


class RecurrenceClipTests(unittest.TestCase):
    def test_R1_anchor_is_first_occurrence(self):
        self.assertEqual(
            FN("2024-01-03", 4, "2024-01-01", "2024-01-31"),
            ["2024-01-03", "2024-01-10", "2024-01-17", "2024-01-24"],
        )

    def test_R2_weekly_cadence(self):
        # Anchor on Jan 1 sits outside the window; only the +7d repeats show up.
        self.assertEqual(FN("2024-01-01", 6, "2024-01-02", "2024-01-21"),
                         ["2024-01-08", "2024-01-15"])

    def test_R3_count_caps_series(self):
        # The window would admit many more occurrences; the series ends after 3.
        self.assertEqual(FN("2024-01-01", 3, "2024-01-01", "2024-03-31"),
                         ["2024-01-01", "2024-01-08", "2024-01-15"])

    def test_R3_count_zero_or_negative(self):
        self.assertEqual(FN("2024-01-01", 0, "2024-01-01", "2024-12-31"), [])
        self.assertEqual(FN("2024-01-01", -3, "2024-01-01", "2024-12-31"), [])

    def test_R4_window_start_edge_inclusive(self):
        # An occurrence on the window's first day counts; one on the boundary day
        # at the far end does not (it belongs to the next window).
        self.assertEqual(
            FN("2024-01-01", 10, "2024-01-15", "2024-02-12"),
            ["2024-01-15", "2024-01-22", "2024-01-29", "2024-02-05"],
        )

    def test_R4_window_end_edge_exclusive(self):
        # The two windows below share the seam day 2024-01-15: exactly one of them
        # claims it, so adjacent windows never double-count a meeting.
        self.assertEqual(FN("2024-01-01", 10, "2024-01-08", "2024-01-15"), ["2024-01-08"])
        self.assertEqual(FN("2024-01-01", 10, "2024-01-15", "2024-01-22"), ["2024-01-15"])

    def test_R5_ascending_order(self):
        result = FN("2024-01-01", 4, "2023-12-01", "2024-03-01")
        self.assertEqual(
            result, ["2024-01-01", "2024-01-08", "2024-01-15", "2024-01-22"]
        )
        self.assertEqual(result, sorted(result))

    def test_R6_window_miss_yields_empty_list(self):
        # The window slots entirely between two occurrences.
        self.assertEqual(FN("2024-01-01", 5, "2024-01-02", "2024-01-07"), [])

    def test_R7_reversed_window_yields_empty_list(self):
        self.assertEqual(FN("2024-01-01", 5, "2024-02-01", "2024-01-01"), [])
        self.assertEqual(FN("2024-01-01", 2, "2024-06-01", "2024-06-30"), [])

    def test_R8_malformed_dates_raise(self):
        for bad in ("garbage", "2024/01/01", "2024-13-01", None, 20240101):
            with self.assertRaises(ValueError):
                FN(bad, 3, "2024-01-01", "2024-02-01")


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        RecurrenceClipTests(name).run(result)
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
