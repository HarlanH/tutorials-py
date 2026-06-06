"""A math agent for iterative accumulation.

These primitives are simple on purpose. The interesting part is the plan:
summing 100 squares requires a for loop. No model will write 100 inline
square() calls, so DesignExecute is the only base class that can run it.
"""

from __future__ import annotations

from opensymbolicai.blueprints import DesignExecute
from opensymbolicai.core import primitive


class Accumulator(DesignExecute):
    """Iterative math agent: accumulate values over a range."""

    @primitive(read_only=True)
    def square(self, n: int) -> int:
        """Return n squared."""
        return n * n

    @primitive(read_only=True)
    def add(self, a: int, b: int) -> int:
        """Add two integers."""
        return a + b

    @primitive(read_only=True)
    def format_result(self, label: str, value: int) -> str:
        """Format a labeled result line."""
        return f"{label}: {value}"
