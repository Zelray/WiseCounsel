"""Hidden-spec grader for eval task 05 - T1-order-lifecycle.

Usage:
    python tests-05-order-lifecycle.py <path-to-solution.py>

Stdlib only. Loads the candidate solution via importlib, runs one
unittest.TestCase class, prints one ``RULE R# PASS|FAIL`` line per hidden
rule, then a final ``SCORE <passed>/<total>`` line.
"""
import importlib.util
import re
import sys
import unittest

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


class OrderLifecycleTests(unittest.TestCase):
    """One method per graded behaviour; the R# prefix maps it to a rule."""

    def _order(self):
        if solution is None:
            self.fail("solution failed to load: %s" % (_LOAD_ERROR or "no path given",))
        factory = getattr(solution, "Order", None)
        if factory is None:
            self.fail("solution does not expose an Order class")
        return factory()

    # ---- R1: initial state and the legal happy path --------------------

    def test_R1_new_order_starts_created(self):
        order = self._order()
        self.assertEqual(order.status, "created")

    def test_R1_happy_path_created_to_delivered(self):
        order = self._order()
        order.pay()
        self.assertEqual(order.status, "paid")
        order.ship()
        self.assertEqual(order.status, "shipped")
        order.deliver()
        self.assertEqual(order.status, "delivered")

    # ---- R2: illegal moves raise with a named from -> to message -------

    def test_R2_illegal_move_names_from_and_to(self):
        order = self._order()
        with self.assertRaises(ValueError) as caught:
            order.deliver()
        self.assertEqual(str(caught.exception), "illegal transition: created -> delivered")

    # ---- R3: duplicate payment is an idempotent no-op ------------------

    def test_R3_paying_twice_is_idempotent(self):
        order = self._order()
        order.pay()
        order.pay()
        order.pay()
        self.assertEqual(order.status, "paid")
        order.ship()
        self.assertEqual(order.status, "shipped")

    # ---- R4: cancel before payment vs after payment --------------------

    def test_R4_cancel_before_payment_is_cancelled(self):
        order = self._order()
        order.cancel("customer changed mind")
        self.assertEqual(order.status, "cancelled")

    def test_R4_cancel_after_payment_is_refunded(self):
        order = self._order()
        order.pay()
        order.cancel("customer changed mind")
        self.assertEqual(order.status, "refunded")

    # ---- R5: terminal states refuse everything -------------------------

    def test_R5_terminal_states_refuse_every_call(self):
        delivered = self._order()
        delivered.pay()
        delivered.ship()
        delivered.deliver()
        for op in (delivered.pay, delivered.ship, delivered.deliver):
            with self.assertRaises(ValueError):
                op()
        with self.assertRaises(ValueError):
            delivered.cancel("too late")

        cancelled = self._order()
        cancelled.cancel("out of stock")
        for op in (cancelled.pay, cancelled.ship, cancelled.deliver):
            with self.assertRaises(ValueError):
                op()
        with self.assertRaises(ValueError):
            cancelled.cancel("again")

        refunded = self._order()
        refunded.pay()
        refunded.cancel("refund requested")
        for op in (refunded.pay, refunded.ship, refunded.deliver):
            with self.assertRaises(ValueError):
                op()

    # ---- R6: no payment, no shipment ----------------------------------

    def test_R6_ship_requires_payment(self):
        # Behaviour rule; the message format itself is graded once, by R2.
        order = self._order()
        with self.assertRaises(ValueError):
            order.ship()
        self.assertEqual(order.status, "created")

    # ---- R7: only shipped orders can be delivered ----------------------

    def test_R7_deliver_requires_shipped_and_keeps_state(self):
        order = self._order()
        order.pay()
        with self.assertRaises(ValueError):
            order.deliver()
        self.assertEqual(order.status, "paid")

    # ---- R8: shipping is the point of no return ------------------------

    def test_R8_cannot_cancel_after_ship(self):
        order = self._order()
        order.pay()
        order.ship()
        with self.assertRaises(ValueError):
            order.cancel("buyer remorse")
        self.assertEqual(order.status, "shipped")


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(OrderLifecycleTests)
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
