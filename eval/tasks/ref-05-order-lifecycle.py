"""Reference solution for eval task 05 - T1-order-lifecycle.

Plain e-commerce order state machine:

    created --pay--> paid --ship--> shipped --deliver--> delivered
        |                |
        cancel           cancel
        v                v
    'cancelled'      'refunded'

Terminal states: 'delivered', 'refunded', 'cancelled'.
Illegal moves raise ValueError("illegal transition: <from> -> <to>").
Paying an already-paid order is an idempotent no-op.
"""


class Order:
    TERMINAL_STATES = ("delivered", "refunded", "cancelled")
    TARGET_BY_METHOD = {
        "pay": "paid",
        "ship": "shipped",
        "deliver": "delivered",
        "cancel": "cancelled",
    }

    def __init__(self):
        self.status = "created"

    def _reject(self, target):
        raise ValueError("illegal transition: %s -> %s" % (self.status, target))

    def pay(self):
        if self.status == "created":
            self.status = "paid"
        elif self.status == "paid":
            return  # duplicate capture: idempotent no-op
        else:
            self._reject(self.TARGET_BY_METHOD["pay"])

    def ship(self):
        if self.status == "paid":
            self.status = "shipped"
        else:
            self._reject(self.TARGET_BY_METHOD["ship"])

    def deliver(self):
        if self.status == "shipped":
            self.status = "delivered"
        else:
            self._reject(self.TARGET_BY_METHOD["deliver"])

    def cancel(self, reason=""):
        if self.status == "created":
            self.status = "cancelled"
        elif self.status == "paid":
            self.status = "refunded"  # money already moved: refund, don't plain-cancel
        else:
            self._reject(self.TARGET_BY_METHOD["cancel"])
