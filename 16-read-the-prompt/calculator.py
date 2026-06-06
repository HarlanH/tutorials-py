"""A Calculator agent with one decomposition, so the prompt has all three sections."""

from __future__ import annotations

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class Calculator(PlanExecute):
    """A tiny calculator agent."""

    @primitive(read_only=True)
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    @primitive(read_only=True)
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b

    @primitive(read_only=True)
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b

    @decomposition(intent="what is 2 plus 3?")
    def _example_add(self) -> float:
        result = self.add(2, 3)
        return result
