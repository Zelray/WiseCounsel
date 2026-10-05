"""Hidden-spec tests for task 37 - T1-dryclean-order.

Stdlib only, no pytest. Usage:
    python tests-37-dryclean-order.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.

Calibration: the full rate card, the 50% express rate, the input shapes, and the
-1.0 cannot-price convention are published in the brief; the linen bundle, the
volume break, the express exclusion, the minimum charge, the rounding tie
direction, and the exact invalid edges stay hidden. The three R1 probes are
clean - plain tickets whose totals carry no half cent and cross no hidden
threshold - so a brief-only implementer scores them; every other probe isolates
one hidden rule at quantities and garment mixes where no second rule can bind.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "price_order"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_rate_card_prices",
    "test_R1_mixed_ticket_total",
    "test_R1_plain_express_ticket",
    "test_R2_linens_bundle_flat_price",
    "test_R2_bundle_leftovers_price_alone",
    "test_R3_volume_break_at_twelve",
    "test_R4_specialty_never_takes_express",
    "test_R5_minimum_charge_floor",
    "test_R6_rounding_ties_go_up",
    "test_R7_bad_ticket_returns_sentinel",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-37-dryclean-order.py <solution.py>\n")
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("solution", SOLUTION_PATH)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        # A submission that cannot even import still scores: it just loses every
        # probe below. The harness itself must never crash on a bad candidate.
        sys.stderr.write("NOTE: solution failed to import; scoring as zero.\n")
    return module


_MODULE = _load_solution()
FN = getattr(_MODULE, FUNCTION_NAME, None)
if FN is None:
    sys.stderr.write(
        "NOTE: no function named %r found in the solution; scoring as zero.\n" % FUNCTION_NAME
    )


class DrycleanOrderTests(unittest.TestCase):
    def assertTotal(self, expected, items, express):
        self.assertAlmostEqual(FN(items, express), expected, delta=0.005)

    def test_R1_rate_card_prices(self):
        # Clean cases: quantity x card price and nothing else - every value is
        # printed on the rate card and no hidden threshold is anywhere in reach.
        self.assertTotal(14.00, [("shirt", 4)], False)
        self.assertTotal(16.00, [("pants", 2), ("dress", 1)], False)

    def test_R1_mixed_ticket_total(self):
        # Clean case: three lines off the public card, four pieces, exact cents.
        self.assertTotal(20.00, [("coat", 1), ("blouse", 2), ("tie", 1)], False)

    def test_R1_plain_express_ticket(self):
        # Clean case: express is public math - 50% on a ticket with nothing
        # excluded, no linens, four pieces, so no hidden rule can touch 27.75.
        self.assertTotal(27.75, [("sweater", 2), ("shirt", 2)], True)

    def test_R2_linens_bundle_flat_price(self):
        # Only the bundle can move this number: five mixed linen pieces price as
        # one flat line, not the 18.75 the per-piece card adds up to.
        self.assertTotal(18.00, [("bedsheet", 2), ("pillowcase", 3)], False)

    def test_R2_bundle_leftovers_price_alone(self):
        # Seven tablecloths: one flat bundle plus two pieces back on the card.
        self.assertTotal(28.50, [("tablecloth", 7)], False)

    def test_R3_volume_break_at_twelve(self):
        # Twelve pieces is the break, ten pieces miss it; no linens and no
        # express, so only the volume rule can move 43.20.
        self.assertTotal(43.20, [("shirt", 6), ("pants", 6)], False)
        self.assertTotal(40.00, [("shirt", 5), ("pants", 5)], False)

    def test_R4_specialty_never_takes_express(self):
        # The 50% lands on the two shirts only: 53.00, not the 74.25 an
        # everything-surcharge gives - and a gown-only ticket adds no rush
        # money at all, still 27.50.
        self.assertTotal(53.00, [("leather jacket", 1), ("wedding gown", 1), ("shirt", 2)], True)
        self.assertTotal(27.50, [("wedding gown", 1)], True)

    def test_R5_minimum_charge_floor(self):
        # Small tickets under the floor ring at 10.00; a ticket above it is
        # priced untouched. No linens, no express, tiny piece counts.
        self.assertTotal(10.00, [("tie", 1), ("shirt", 1)], False)
        self.assertTotal(10.00, [("tie", 3)], False)
        self.assertTotal(10.50, [("shirt", 3)], False)

    def test_R6_rounding_ties_go_up(self):
        # 13.75 plus 50% is 20.625 - a true half cent that posts as 20.63, not
        # the 20.62 banker's rounding gives. The second ticket needs no
        # rounding at all.
        self.assertTotal(20.63, [("blouse", 1), ("tie", 1), ("shirt", 2)], True)
        self.assertTotal(18.00, [("shirt", 2), ("tie", 2)], True)

    def test_R7_bad_ticket_returns_sentinel(self):
        # Published convention: a ticket we cannot price comes back -1.0 and
        # the function never raises.
        self.assertTotal(-1.0, [("tuxedo", 1)], False)    # garment not on the card
        self.assertTotal(-1.0, [("shirt", 0)], False)     # zero pieces
        self.assertTotal(-1.0, [("shirt", 2.5)], False)   # fractional pieces
        self.assertTotal(-1.0, [(None, 1)], False)        # garment type isn't text
        self.assertTotal(-1.0, [("shirt", True)], False)  # booleans aren't counts


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        DrycleanOrderTests(name).run(result)
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
