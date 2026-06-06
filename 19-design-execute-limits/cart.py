"""A shopping cart agent for demonstrating DesignExecute config knobs."""

from __future__ import annotations

from opensymbolicai.blueprints import DesignExecute
from opensymbolicai.core import primitive

PRICES: dict[str, float] = {
    "apple":    0.99,
    "banana":   0.49,
    "book":    12.99,
    "notebook": 4.99,
    "pen":      1.49,
    "stapler":  8.99,
}


class Cart(DesignExecute):
    """A shopping cart agent."""

    @primitive(read_only=True)
    def item_total(self, name: str, qty: int) -> float:
        """Price for qty units of name."""
        if name not in PRICES:
            raise ValueError(f"Unknown item: {name}")
        return round(PRICES[name] * qty, 2)

    @primitive(read_only=True)
    def add(self, a: float, b: float) -> float:
        """Add two amounts."""
        return round(a + b, 2)

    @primitive(read_only=True)
    def format_total(self, total: float) -> str:
        """Format the grand total as a receipt line."""
        return f"Total: ${total:.2f}"
