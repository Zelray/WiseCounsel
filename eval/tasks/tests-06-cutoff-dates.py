"""Hidden-spec grader for eval task 06 - T1-cutoff-dates.

Usage:
    python tests-06-cutoff-dates.py <path-to-solution.py>

Stdlib only. Loads the candidate solution via importlib, runs one
unittest.TestCase class, prints one ``RULE R# PASS|FAIL`` line per hidden
rule, then a final ``SCORE <passed>/<total>`` line.

Calendar notes (hand-checked, year 2027):
    2027-03-10 Wed, 03-11 Thu, 03-12 Fri, 03-13 Sat, 03-14 Sun, 03-15 Mon, 03-16 Tue
    2026-12-31 Thu, 2027-01-01 Fri (holiday), 01-04 Mon, 01-05 Tue
"""
import importlib.util
import re
import sys
import unittest
from datetime import date, datetime

_SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
_LOAD_ERROR = ""


def _load(path):
    spec = importlib.util.spec_from_file_location("solution", path)
    if spec is None or spec.loader is None:
        raise ImportError("could not create a module spec for %r" % (path,))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    solution = _load(_SOLUTION_PATH)
except Exception as exc:  # grader must never crash on a broken candidate
    solution = None
    _LOAD_ERROR = "%s: %s" % (type(exc).__name__, exc)


class CutoffDateTests(unittest.TestCase):
    """One method per graded behaviour; the R# prefix maps it to a rule."""

    def _ship_date(self, when, holidays=()):
        if solution is None:
            self.fail("solution failed to load: %s" % (_LOAD_ERROR or "no path given",))
        func = getattr(solution, "ship_date", None)
        if func is None:
            self.fail("solution does not expose a ship_date function")
        return func(when, list(holidays))

    # ---- R1: pre-cutoff orders ship the next business day --------------

    def test_R1_morning_order_ships_next_business_day(self):
        # Wed 2027-03-10 09:15, no holidays -> ships Thursday 2027-03-11.
        self.assertEqual(self._ship_date(datetime(2027, 3, 10, 9, 15)), date(2027, 3, 11))

    def test_R1_friday_order_ships_monday(self):
        # Fri 2027-03-12 08:00 -> the weekend is dark, so Monday 2027-03-15.
        self.assertEqual(self._ship_date(datetime(2027, 3, 12, 8, 0)), date(2027, 3, 15))

    # ---- R2: at/after the cutoff costs one extra business day ----------

    def test_R2_afternoon_order_ships_a_business_day_later(self):
        # Wed 2027-03-10 14:30 -> Friday 2027-03-12 (not Thursday).
        self.assertEqual(self._ship_date(datetime(2027, 3, 10, 14, 30)), date(2027, 3, 12))

    def test_R2_cutoff_boundary_is_inclusive(self):
        # Exactly 14:00:00 is already too late -> Friday 2027-03-12.
        self.assertEqual(self._ship_date(datetime(2027, 3, 10, 14, 0, 0)), date(2027, 3, 12))
        # One minute earlier still makes the truck -> Thursday 2027-03-11.
        self.assertEqual(self._ship_date(datetime(2027, 3, 10, 13, 59)), date(2027, 3, 11))

    # ---- R3: listed holidays are not business days ---------------------

    def test_R3_listed_holiday_is_skipped(self):
        # Wed 2027-03-10 10:00 with Thursday 03-11 dark -> Friday 2027-03-12.
        holidays = [date(2027, 3, 11)]
        self.assertEqual(self._ship_date(datetime(2027, 3, 10, 10, 0), holidays), date(2027, 3, 12))

    # ---- R4: answers always land on an open day (roll forward) ---------

    def test_R4_dark_cluster_rolls_forward(self):
        # Thu 2027-03-11 09:00 with Fri 03-12 and Mon 03-15 dark -> Tue 2027-03-16.
        holidays = [date(2027, 3, 12), date(2027, 3, 15)]
        self.assertEqual(self._ship_date(datetime(2027, 3, 11, 9, 0), holidays), date(2027, 3, 16))

    # ---- R5: a bare date counts as noon that day -----------------------

    def test_R5_bare_date_is_normalised_to_noon(self):
        # date(2027,3,10) -> inside the window -> Thursday 2027-03-11.
        self.assertEqual(self._ship_date(date(2027, 3, 10)), date(2027, 3, 11))
        # date(2027,3,12) is a Friday -> Monday 2027-03-15.
        self.assertEqual(self._ship_date(date(2027, 3, 12)), date(2027, 3, 15))

    # ---- R6: an empty holiday list is legal ----------------------------

    def test_R6_empty_holidays_skip_weekends_only(self):
        # Saturday 2027-03-13 09:00 with no holidays -> Monday 2027-03-15.
        self.assertEqual(self._ship_date(datetime(2027, 3, 13, 9, 0), []), date(2027, 3, 15))
        self.assertEqual(self._ship_date(datetime(2027, 3, 13, 9, 0), set()), date(2027, 3, 15))

    # ---- R7: weekend holidays add nothing extra ------------------------

    def test_R7_weekend_holiday_adds_no_delay(self):
        # Fri 2027-03-12 09:00; Sat 03-13 + Sun 03-14 listed as holidays ->
        # still Monday 2027-03-15 (the weekend already ate those days).
        holidays = [date(2027, 3, 13), date(2027, 3, 14)]
        self.assertEqual(self._ship_date(datetime(2027, 3, 12, 9, 0), holidays), date(2027, 3, 15))

    # ---- R8: rolling ignores the year boundary -------------------------

    def test_R8_year_boundary_holiday_chain(self):
        new_year = [date(2027, 1, 1)]
        # Thu 2026-12-31 13:59, Jan 1 dark: Fri->Sat->Sun roll lands Mon 2027-01-04.
        self.assertEqual(self._ship_date(datetime(2026, 12, 31, 13, 59), new_year), date(2027, 1, 4))
        # Same day at 14:00 misses the cutoff: Mon 01-04 + one -> Tue 2027-01-05.
        self.assertEqual(self._ship_date(datetime(2026, 12, 31, 14, 0), new_year), date(2027, 1, 5))


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(CutoffDateTests)
    all_tests = list(suite)  # snapshot BEFORE run(): suite.run() drops its entries
    result = unittest.TestResult()
    suite.run(result)

    failed_ids = set()
    for outcome in (result.failures, result.errors):
        for test, _traceback in outcome:
            failed_ids.add(test.id())

    passed_by_rule = {}
    total_by_rule = {}
    for test in all_tests:
        name = getattr(test, "_testMethodName", "")
        match = re.match(r"^test_(R\d+)_", name)
        rule = match.group(1) if match else "R0"
        total_by_rule[rule] = total_by_rule.get(rule, 0) + 1
        if test.id() not in failed_ids:
            passed_by_rule[rule] = passed_by_rule.get(rule, 0) + 1

    def rule_sort_key(rule):
        return int(rule[1:]) if rule[1:].isdigit() else 999

    for rule in sorted(total_by_rule, key=rule_sort_key):
        verdict = "PASS" if passed_by_rule.get(rule, 0) == total_by_rule[rule] else "FAIL"
        print("RULE %s %s" % (rule, verdict))

    total = result.testsRun
    passed = total - len(failed_ids)
    print("SCORE %d/%d" % (passed, total))


if __name__ == "__main__":
    main()
