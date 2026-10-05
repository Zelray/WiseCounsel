"""Hidden-spec tests for task 26 - T1-invoice-aging.

Stdlib only, no pytest. Usage:
    python tests-26-invoice-aging.py <path-to-solution.py>

Loads the solution with importlib.util.spec_from_file_location("solution", argv[1]),
runs one unittest.TestCase class whose method names encode rule ids, then prints
one `RULE R# PASS|FAIL` line per rule and a final `SCORE <passed>/<total>` line.
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True

SOLUTION_PATH = sys.argv[1] if len(sys.argv) > 1 else ""
FUNCTION_NAME = "invoice_aging"
RULE_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
TEST_ORDER = [
    "test_R1_ages_from_due_date",
    "test_R1_ignores_invoice_date",
    "test_R2_not_yet_overdue_is_current",
    "test_R3_bucket_edges_inclusive",
    "test_R3_day_after_edge_moves_bucket",
    "test_R4_credit_notes_net_in_place",
    "test_R5_totals_rounded_to_cents",
    "test_R6_all_buckets_always_present",
    "test_R7_malformed_dates_raise",
    "test_R8_malformed_amounts_raise",
]


def _load_solution():
    if not SOLUTION_PATH:
        sys.stderr.write("usage: python tests-26-invoice-aging.py <solution.py>\n")
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


def _inv(due, amount, invoice_date="2024-01-10", invoice_id="INV-1"):
    return {
        "invoice_id": invoice_id,
        "invoice_date": invoice_date,
        "due_date": due,
        "amount": amount,
    }


class InvoiceAgingTests(unittest.TestCase):
    def test_R1_ages_from_due_date(self):
        # 2024-03-01 is 14 days past due on 2024-03-15 (the early invoice_date is a decoy).
        aging = FN([_inv("2024-03-01", 100.0, invoice_date="2024-01-05")], "2024-03-15")
        self.assertEqual(aging["1-30"], 100.0)
        aging = FN([_inv("2023-12-01", 75.0, invoice_date="2023-12-01")], "2024-03-15")
        self.assertEqual(aging["91+"], 75.0)

    def test_R1_ignores_invoice_date(self):
        # Same due date, wildly different invoice dates: identical bucketing.
        aging = FN(
            [
                _inv("2024-04-01", 100.0, invoice_date="2024-01-01"),
                _inv("2024-04-01", 150.0, invoice_date="2024-03-14"),
            ],
            "2024-03-15",
        )
        self.assertEqual(aging["current"], 250.0)

    def test_R2_not_yet_overdue_is_current(self):
        # Due on the report date itself, and due further out - neither is overdue yet.
        aging = FN(
            [
                _inv("2024-03-15", 40.0),
                _inv("2024-06-01", 60.0),
            ],
            "2024-03-15",
        )
        self.assertEqual(aging["current"], 100.0)

    def test_R3_bucket_edges_inclusive(self):
        aging = FN(
            [
                _inv("2024-02-14", 1.0),   # exactly 30 days late
                _inv("2024-01-15", 2.0),   # exactly 60 days late
                _inv("2023-12-16", 3.0),   # exactly 90 days late
            ],
            "2024-03-15",
        )
        self.assertEqual(aging["1-30"], 1.0)
        self.assertEqual(aging["31-60"], 2.0)
        self.assertEqual(aging["61-90"], 3.0)
        self.assertEqual(aging["91+"], 0.0)

    def test_R3_day_after_edge_moves_bucket(self):
        aging = FN(
            [
                _inv("2024-02-13", 1.0),   # 31 days late
                _inv("2024-01-14", 2.0),   # 61 days late
                _inv("2023-12-15", 3.0),   # 91 days late
            ],
            "2024-03-15",
        )
        self.assertEqual(aging["1-30"], 0.0)
        self.assertEqual(aging["31-60"], 1.0)
        self.assertEqual(aging["61-90"], 2.0)
        self.assertEqual(aging["91+"], 3.0)

    def test_R4_credit_notes_net_in_place(self):
        aging = FN(
            [
                _inv("2024-02-14", 80.0),
                _inv("2024-02-14", -50.0),
                _inv("2024-01-14", -25.0),
            ],
            "2024-03-15",
        )
        self.assertEqual(aging["1-30"], 30.0)
        self.assertEqual(aging["61-90"], -25.0)

    def test_R5_totals_rounded_to_cents(self):
        aging = FN(
            [
                _inv("2024-02-14", 0.1),
                _inv("2024-02-14", 0.1),
                _inv("2024-02-14", 0.1),
            ],
            "2024-03-15",
        )
        self.assertEqual(aging["1-30"], 0.3)

    def test_R6_all_buckets_always_present(self):
        aging = FN([], "2024-03-15")
        self.assertEqual(
            aging,
            {"current": 0.0, "1-30": 0.0, "31-60": 0.0, "61-90": 0.0, "91+": 0.0},
        )
        aging = FN([_inv("2024-03-01", 5.0)], "2024-03-15")
        self.assertEqual(
            sorted(aging.keys()), ["1-30", "31-60", "61-90", "91+", "current"]
        )

    def test_R7_malformed_dates_raise(self):
        with self.assertRaises(ValueError):
            FN([_inv("02/14/2024", 10.0)], "2024-03-15")
        with self.assertRaises(ValueError):
            FN([_inv(None, 10.0)], "2024-03-15")

    def test_R8_malformed_amounts_raise(self):
        missing = {
            "invoice_id": "INV-9",
            "invoice_date": "2024-01-10",
            "due_date": "2024-03-01",
        }
        with self.assertRaises(ValueError):
            FN([missing], "2024-03-15")
        for bad in (None, "abc", {"cents": 5}):
            with self.assertRaises(ValueError):
                FN([_inv("2024-03-01", bad)], "2024-03-15")


def main():
    outcomes = []
    for name in TEST_ORDER:
        result = unittest.TestResult()
        InvoiceAgingTests(name).run(result)
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
