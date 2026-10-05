"""Hidden-spec tests for task 29 - T1-cart-promotions.

Stdlib only, no pytest. Usage:
    python tests-29-cart-promotions.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.

Round-4 calibration: the promo catalog with numeric face values (WELCOME15 = 15%,
TAKE20 = 20%, FIVE5 = 5%, SAVE15 = 15.00 flat behind a published 25.00 gate),
code-entry forgiveness, unknown-code handling, one-percentage-in-force, and
empty-cart behavior are published in the brief; each test below isolates one
hidden rule so a wrong guess on one convention costs only its own test - and
three tests (R1 positive, R2 no-stack, R3 flat gate) are clean single-code cases
computable from the brief alone, so a near-miss implementation still banks them.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "apply_promotions"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
TEST_ORDER = [
    "test_R1_percentage_covers_apparel_and_home",
    "test_R1_other_categories_pay_full_price",
    "test_R2_only_one_percentage_is_in_force",
    "test_R2_winner_independent_of_entry_order",
    "test_R3_flat_gate_honors_its_published_minimum",
    "test_R3_flat_gate_measured_after_percentages",
    "test_R4_flat_code_is_order_wide",
    "test_R5_combined_discount_is_capped",
    "test_R6_totals_round_half_up_to_the_cent",
    "test_R7_duplicate_codes_count_once",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-29-cart-promotions.py <solution.py>\n")
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


def _item(price, category):
    return {"price": price, "category": category}


class CartPromotionsTests(unittest.TestCase):
    def test_R1_percentage_covers_apparel_and_home(self):
        # Clean cases: one percentage code alone on a single-category cart, face
        # value published, well under the cap, no half cent in sight. The only
        # convention in play is which departments a percentage code covers.
        self.assertEqual(FN([_item(100, "apparel")], ["WELCOME15"]), 85.0)
        self.assertEqual(FN([_item(80, "home")], ["TAKE20"]), 64.0)

    def test_R1_other_categories_pay_full_price(self):
        cart = [_item(40, "apparel"), _item(60, "home"), _item(50, "clearance")]
        self.assertEqual(FN(cart, ["WELCOME15"]), 135.0)
        # Unknown category, plus published convention: unknown codes do nothing.
        self.assertEqual(FN([_item(80, "grocery")], ["TAKE20", "BOGUS", "also_fake"]), 80.0)

    def test_R2_only_one_percentage_is_in_force(self):
        # Published convention: percentage offers never combine - the result must
        # equal one of the single-code totals, never a sum of them. (Which single
        # code wins is house policy; the entry-order probe below pins that.)
        cart = [_item(100, "apparel")]
        self.assertIn(FN(cart, ["WELCOME15", "TAKE20"]), (85.0, 80.0, 95.0))
        self.assertIn(FN(cart, ["WELCOME15", "TAKE20", "FIVE5"]), (85.0, 80.0, 95.0))

    def test_R2_winner_independent_of_entry_order(self):
        cart = [_item(100, "apparel")]
        self.assertEqual(FN(cart, ["TAKE20", "WELCOME15"]), 80.0)
        self.assertEqual(FN(cart, ["FIVE5", "WELCOME15"]), 85.0)

    def test_R3_flat_gate_honors_its_published_minimum(self):
        # Clean cases: the 25.00 gate is printed on the code, so both sides of it
        # are computable from the brief - and with no percentage code in play,
        # the gate-measurement convention cannot move these totals either.
        self.assertEqual(FN([_item(35, "apparel")], ["SAVE15"]), 20.0)
        self.assertEqual(FN([_item(24.99, "apparel")], ["SAVE15"]), 24.99)  # one cent short
        # Published convention: an empty cart is a 0.0 charge.
        self.assertEqual(FN([], ["SAVE15"]), 0.0)

    def test_R3_flat_gate_measured_after_percentages(self):
        # 20% comes off first (6.00), leaving 24.00 - under the flat code's bar.
        cart = [_item(30, "apparel")]
        self.assertEqual(FN(cart, ["TAKE20", "SAVE15"]), 24.0)

    def test_R4_flat_code_is_order_wide(self):
        # No percentage-eligible line in the cart, yet the flat code still comes off.
        self.assertEqual(FN([_item(120, "electronics")], ["SAVE15"]), 105.0)
        self.assertEqual(FN([_item(20, "food"), _item(110, "electronics")], ["SAVE15"]), 115.0)

    def test_R5_combined_discount_is_capped(self):
        # Raw combo would be 9.00 + 15.00 = 24.00 off a 45.00 subtotal; the cap holds it to 22.50.
        cart = [_item(45, "apparel")]
        self.assertEqual(FN(cart, ["TAKE20", "SAVE15"]), 22.5)
        # Same codes on a bigger cart stay under the cap.
        big = [_item(100, "apparel")]
        self.assertEqual(FN(big, ["TAKE20", "SAVE15"]), 65.0)

    def test_R6_totals_round_half_up_to_the_cent(self):
        # 50.10 at 5% off is exactly 47.595 - the half cent rounds up to 47.60.
        self.assertEqual(FN([_item(50.10, "apparel")], ["FIVE5"]), 47.6)
        self.assertEqual(FN([_item(14.10, "apparel")], ["FIVE5"]), 13.4)   # 13.395 -> 13.40
        self.assertEqual(FN([_item(33.33, "apparel")], ["WELCOME15"]), 28.33)

    def test_R7_duplicate_codes_count_once(self):
        # The flat code is where a repeat would actually multiply the discount.
        cart = [_item(100, "apparel")]
        self.assertEqual(FN(cart, ["SAVE15", "SAVE15"]), 85.0)
        self.assertEqual(FN(cart, [" save15 ", "SAVE15"]), 85.0)
        self.assertEqual(FN(cart, ["WELCOME15", "WELCOME15"]), 85.0)


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        CartPromotionsTests(name).run(result)
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
