"""Hidden-spec grader for eval task 02 - T1-parking.

Usage:
    python tests-02-parking.py <path-to-solution.py>

Stdlib only. Loads the candidate solution via importlib, runs one
unittest.TestCase class, prints one ``RULE R# PASS|FAIL`` line per hidden
rule (a rule passes only when every test mapped to it passes), then a
final ``SCORE <passed>/<total>`` line.
"""
import importlib.util
import re
import sys
import unittest
from decimal import Decimal

sys.dont_write_bytecode = True  # never drop __pycache__ next to a candidate

_SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
_LOAD_ERROR = ""

# The hidden posted-rate card. Nothing in the public brief names these
# numbers; a candidate has to reason from real garage conventions.
_GRACE_MINUTES = 15
_UNIT_MINUTES = 30
_UNIT_RATE = Decimal("2.75")
_DAILY_CAP = Decimal("25.00")
_LOST_TICKET_FEE = Decimal("40.00")


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

# Sanity pins: the cap must bite somewhere inside a single day, and the
# started-unit boundary must be a true ceiling on whole-minute input.
assert _UNIT_RATE * 9 < _DAILY_CAP < _UNIT_RATE * 10
assert -(-270 // _UNIT_MINUTES) == 9 and -(-271 // _UNIT_MINUTES) == 10


class ParkingFeeTests(unittest.TestCase):
    """One method per graded behaviour; the R# prefix maps it to a rule."""

    def _fee(self, entry, leave):
        if solution is None:
            self.fail("solution failed to load: %s" % (_LOAD_ERROR or "no path given",))
        func = getattr(solution, "parking_fee", None)
        if func is None:
            self.fail("solution does not expose parking_fee(entry_minute, exit_minute)")
        return func(entry, leave)

    def _assert_fee(self, actual, expected, msg=None):
        self.assertIsInstance(actual, float, msg)
        self.assertAlmostEqual(actual, float(expected), delta=0.001, msg=msg)

    # ---- R1: grace window ----------------------------------------------

    def test_R1_fifteen_minutes_or_less_is_free(self):
        self._assert_fee(self._fee(480, 480), Decimal("0.00"))
        self._assert_fee(self._fee(480, 495), Decimal("0.00"))

    def test_R1_grace_expires_at_sixteen_minutes(self):
        self._assert_fee(self._fee(480, 496), _UNIT_RATE)

    # ---- R2: one flat block per started half-hour, from entry ----------

    def test_R2_started_half_hour_boundary_is_not_prorated(self):
        self._assert_fee(self._fee(480, 510), _UNIT_RATE)  # 30 min -> one block
        self._assert_fee(self._fee(480, 511), _UNIT_RATE * 2)  # 31 min -> two

    def test_R2_nine_blocks_still_sits_under_the_cap(self):
        # 270 minutes -> exactly nine started half-hours
        self._assert_fee(self._fee(480, 750), _UNIT_RATE * 9)

    # ---- R3: daily maximum ---------------------------------------------

    def test_R3_daily_cap_overrides_the_block_total(self):
        # 300 min -> ten blocks = 27.50, billed at the cap
        self._assert_fee(self._fee(480, 780), _DAILY_CAP)
        # 420 min -> fourteen blocks, still just the cap
        self._assert_fee(self._fee(480, 900), _DAILY_CAP)

    # ---- R4: lost ticket ------------------------------------------------

    def test_R4_lost_ticket_is_a_flat_fee(self):
        self._assert_fee(self._fee(480, None), _LOST_TICKET_FEE)
        self._assert_fee(self._fee(500, None), _LOST_TICKET_FEE)

    # ---- R5: reversed timestamps ---------------------------------------

    def test_R5_exit_before_entry_raises_and_equal_is_free(self):
        with self.assertRaises(ValueError):
            self._fee(600, 540)
        self._assert_fee(self._fee(600, 600), Decimal("0.00"))

    # ---- R6: minutes must be whole numbers within the day --------------

    def test_R6_minutes_outside_the_day_raise(self):
        for entry, leave in ((1440, 1500), (-1, 30), (480, 1440)):
            with self.assertRaises(ValueError):
                self._fee(entry, leave)

    def test_R6_fractional_and_non_numeric_minutes_raise(self):
        for entry, leave in (("480", 540), (480, 540.5), (None, 540)):
            with self.assertRaises(ValueError):
                self._fee(entry, leave)

    # ---- R7: plain float at two decimals -------------------------------

    def test_R7_returns_plain_float_at_two_decimals(self):
        fee = self._fee(480, 750)
        self.assertIsInstance(fee, float)
        self.assertEqual(fee, round(fee, 2))
        self._assert_fee(fee, _UNIT_RATE * 9)


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(ParkingFeeTests)
    tests = list(suite)  # snapshot first: suite.run() empties itself
    result = unittest.TestResult()
    suite.run(result)

    failed_ids = set()
    for outcome in (result.failures, result.errors):
        for test, _traceback in outcome:
            failed_ids.add(test.id())
            # terse diagnostic on stderr; stdout stays machine-readable
            sys.stderr.write("FAILED %s\n" % (test.id(),))

    passed_by_rule = {}
    total_by_rule = {}
    for test in tests:
        name = getattr(test, "_testMethodName", "")
        match = re.match(r"^test_(R\d+|SMOKE)_", name)
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
