"""A tiny bank-account agent with a read/write split.

`deposit` and `withdraw` change the balance, so they are declared not read-only.
`can_afford` only looks at the balance, so it is read-only. Those flags are the
author's signal (Track 5), and this track reads them back off a plan with
`analyze_plan`.
"""

from __future__ import annotations

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Account(PlanExecute):
    """A balance you can deposit to, withdraw from, and check."""

    @primitive(read_only=False)
    def deposit(self, balance: float, amount: float) -> float:
        """Add money to the balance."""
        return balance + amount

    @primitive(read_only=False)
    def withdraw(self, balance: float, amount: float) -> float:
        """Take money out of the balance."""
        return balance - amount

    @primitive(read_only=True)
    def can_afford(self, balance: float, price: float) -> bool:
        """Check whether the balance covers a price."""
        return balance >= price
