"""A shopping cart agent with a tiered discount and a decomposition example.

The discount rule has two tiers: 15% off when subtotal exceeds $100, 10% off
when it exceeds $50, and no discount otherwise. A decomposition teaches the
planner the correct approach before it tries to generalize.
"""

from __future__ import annotations

from opensymbolicai.blueprints import DesignExecute
from opensymbolicai.core import decomposition, primitive

PRICES: dict[str, float] = {
    "apple":    0.99,
    "banana":   0.49,
    "book":    12.99,
    "keyboard": 79.00,
    "monitor": 299.00,
    "notebook": 4.99,
    "pen":      1.49,
    "stapler":  8.99,
}


class Cart(DesignExecute):
    """A shopping cart with tiered discounts: 15% over $100, 10% over $50."""

    @primitive(read_only=True)
    def item_total(self, name: str, qty: int) -> float:
        """Price for qty units of name."""
        if name not in PRICES:
            raise ValueError(f"Unknown item: {name}")
        return round(PRICES[name] * qty, 2)

    @primitive(read_only=True)
    def add(self, a: float, b: float) -> float:
        """Add two amounts. Chain calls to sum three or more: add(add(a, b), c)."""
        return round(a + b, 2)

    @primitive(read_only=True)
    def apply_discount(self, total: float, pct: float) -> float:
        """Reduce total by pct percent (e.g. pct=15 means 15% off)."""
        return round(total * (1.0 - pct / 100.0), 2)

    @primitive(read_only=True)
    def format_bill(self, subtotal: float, discount_pct: float, final: float) -> str:
        """Format a receipt showing subtotal, discount tier, and final amount."""
        if discount_pct > 0:
            return (
                f"Subtotal: ${subtotal:.2f}. "
                f"Discount: {discount_pct:.0f}%. "
                f"Total: ${final:.2f}"
            )
        return f"Total: ${final:.2f} (no discount)"

    @decomposition(
        intent="how much for 3 notebooks, 1 stapler, and 2 pens?",
        expanded_intent=(
            "Compute each item's total, chain add() to build the subtotal "
            "(add takes exactly two arguments, so nest calls for three or more: "
            "add(add(a, b), c)), then pick the discount tier: 15% if subtotal "
            "exceeds 100, 10% if it exceeds 50, else 0. Apply the discount and "
            "format the bill."
        ),
    )
    def _example_three_items(self) -> str:
        notebooks = self.item_total("notebook", 3)
        stapler = self.item_total("stapler", 1)
        pens = self.item_total("pen", 2)
        subtotal = self.add(self.add(notebooks, stapler), pens)
        if subtotal > 100:
            discount_pct = 15
        elif subtotal > 50:
            discount_pct = 10
        else:
            discount_pct = 0
        final = self.apply_discount(subtotal, discount_pct)
        bill = self.format_bill(subtotal, discount_pct, final)
        return bill
