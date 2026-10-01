"""Hidden-spec grader for eval task 01 - T1-overtime.

Usage:
    python tests-01-overtime.py <path-to-solution.py>

Stdlib only. Loads the candidate solution via importlib, runs one
unittest.TestCase class, prints one ``RULE R# PASS|FAIL`` line per hidden
rule (a rule passes only when every test mapped to it passes), then a
final ``SCORE <passed>/<total>`` line.
"""
import importlib.util
import re
import sys
import unittest
from decimal import Decimal, ROUND_HALF_UP

sys.dont_write_bytecode = True  # never drop __pycache__ next to a candidate

_SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
_LOAD_ERROR = ""
_CENTS = Decimal("0.01")


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

# The two R6 cases sit on exact half-cent ties. These asserts pin the trap:
# half-up rounds them up, while banker's rounding and naive float round()
# both round them down. If either assert fails, the test values drifted.
assert Decimal("20.025").quantize(_CENTS, rounding=ROUND_HALF_UP) == Decimal("20.03")
assert Decimal("18.045").quantize(_CENTS, rounding=ROUND_HALF_UP) == Decimal("18.05")
assert Decimal("20.025").quantize(_CENTS) == Decimal("20.02")  # ROUND_HALF_EVEN
assert Decimal("18.045").quantize(_CENTS) == Decimal("18.04")  # ROUND_HALF_EVEN
# naive float math loses both cases too: round() sees 20.0249... and 18.0449...
assert round(13.35 * 1.5, 2) == 20.02 and round(12.03 * 1.5, 2) == 18.04


class CalcPayTests(unittest.TestCase):
    """One method per graded behaviour; the R# prefix maps it to a rule."""

    def _calc(self, hours, rate):
        if solution is None:
            self.fail("solution failed to load: %s" % (_LOAD_ERROR or "no path given",))
        func = getattr(solution, "calc_pay", None)
        if func is None:
            self.fail("solution does not expose calc_pay(hours, rate)")
        return func(hours, rate)

    def _assert_cents(self, actual, expected, msg=None):
        self.assertIsInstance(actual, float, msg)
        self.assertAlmostEqual(actual, float(expected), delta=0.001, msg=msg)

    # ---- smoke: it runs and hands back the promised dict ---------------

    def test_SMOKE_plain_forty_hour_week_returns_dict(self):
        result = self._calc(40, 12.00)
        self.assertIsInstance(result, dict)
        for key in ("regular_pay", "overtime_pay", "total"):
            self.assertIn(key, result)

    def test_SMOKE_typical_week_runs_and_totals(self):
        result = self._calc(40, 15.00)
        self.assertIsInstance(result, dict)
        self._assert_cents(result["total"], Decimal("600.00"))

    # ---- R1: overtime starts after 40 hours ----------------------------

    def test_R1_forty_hours_is_all_regular_and_past_forty_bills_ot(self):
        at_40 = self._calc(40, 12.00)
        self._assert_cents(at_40["regular_pay"], Decimal("480.00"))
        self._assert_cents(at_40["overtime_pay"], Decimal("0.00"))
        just_over = self._calc(40.5, 12.00)
        self._assert_cents(just_over["overtime_pay"], Decimal("9.00"))

    # ---- R2: 1.5x band through 50, 2.0x band above 50 ------------------

    def test_R2_premium_bands_time_and_half_then_double(self):
        band1 = self._calc(45, 12.00)
        self._assert_cents(band1["regular_pay"], Decimal("480.00"))
        expected_band1 = self._money(Decimal(5) * Decimal("12.00") * Decimal("1.5"))
        self._assert_cents(band1["overtime_pay"], expected_band1)
        self._assert_cents(band1["total"], Decimal("570.00"))

        band2 = self._calc(55, 12.00)
        self._assert_cents(band2["regular_pay"], Decimal("480.00"))
        expected_band2 = self._money(
            Decimal(10) * Decimal("12.00") * Decimal("1.5")
            + Decimal(5) * Decimal("12.00") * Decimal(2)
        )
        self._assert_cents(band2["overtime_pay"], expected_band2)
        self._assert_cents(band2["total"], Decimal("780.00"))

    # ---- R3: over 60 hours is refused ----------------------------------

    def test_R3_more_than_sixty_hours_raises_sixty_is_allowed(self):
        for hours in (60.5, 61, 100):
            with self.assertRaises(ValueError):
                self._calc(hours, 12.00)
        at_limit = self._calc(60, 12.00)
        self._assert_cents(at_limit["total"], Decimal("900.00"))

    # ---- R4: rate floor -------------------------------------------------

    def test_R4_rate_below_twelve_raises_floor_is_allowed(self):
        for rate in (11.99, 0):
            with self.assertRaises(ValueError):
                self._calc(40, rate)
        at_floor = self._calc(40, 12.00)
        self._assert_cents(at_floor["total"], Decimal("480.00"))

    # ---- R5: negative / non-numeric input ------------------------------

    def test_R5_negative_and_non_numeric_input_raises(self):
        for bad_hours in (-5, "40", None):
            with self.assertRaises(ValueError) as caught:
                self._calc(bad_hours, 12.00)
            self.assertIn("hours must be non-negative", str(caught.exception))
        for bad_rate in ("12.00", None):
            with self.assertRaises(ValueError):
                self._calc(40, bad_rate)

    # ---- R6: half-up cents, not banker's rounding ----------------------

    def test_R6_half_up_cents_case_a(self):
        result = self._calc(41, 13.35)
        self._assert_cents(result["regular_pay"], Decimal("534.00"))
        # 1.5 * 13.35 = 20.025 -> half-up 20.03 (banker's / round() say 20.02)
        self._assert_cents(
            result["overtime_pay"],
            self._money(Decimal("13.35") * Decimal("1.5")),
        )
        self._assert_cents(result["total"], Decimal("554.03"))

    def test_R6_half_up_cents_case_b(self):
        result = self._calc(41, 12.03)
        self._assert_cents(result["regular_pay"], Decimal("481.20"))
        # 1.5 * 12.03 = 18.045 -> half-up 18.05 (banker's / round() say 18.04)
        self._assert_cents(
            result["overtime_pay"],
            self._money(Decimal("12.03") * Decimal("1.5")),
        )
        self._assert_cents(result["total"], Decimal("499.25"))

    # ---- R7: shape, float values, total = regular + overtime -----------

    def test_R7_shape_floats_and_total_sums(self):
        result = self._calc(42, 20.00)
        self.assertIsInstance(result, dict)
        self.assertEqual(set(result.keys()), {"regular_pay", "overtime_pay", "total"})
        for key in ("regular_pay", "overtime_pay", "total"):
            self.assertIsInstance(result[key], float)
            self.assertEqual(result[key], round(result[key], 2))
        self._assert_cents(result["regular_pay"], Decimal("800.00"))
        self._assert_cents(result["overtime_pay"], Decimal("60.00"))
        self._assert_cents(result["total"], Decimal("860.00"))
        self.assertAlmostEqual(
            result["total"],
            result["regular_pay"] + result["overtime_pay"],
            delta=0.001,
        )

    def _money(self, value):
        return Decimal(str(value)).quantize(_CENTS, rounding=ROUND_HALF_UP)


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(CalcPayTests)
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
