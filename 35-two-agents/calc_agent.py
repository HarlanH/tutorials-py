"""CalculatorAgent: performs basic arithmetic, nothing else."""

from __future__ import annotations

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class CalculatorAgent(PlanExecute):
    """Specialist: add, subtract, multiply, divide."""

    @primitive(read_only=True)
    def add(self, a: float, b: float) -> float:
        """Add two numbers. Example: add(3, 4) -> 7"""
        return a + b

    @primitive(read_only=True)
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a. Example: subtract(10, 3) -> 7"""
        return a - b

    @primitive(read_only=True)
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers. Example: multiply(3, 4) -> 12"""
        return a * b

    @primitive(read_only=True)
    def divide(self, a: float, b: float) -> float:
        """Divide a by b. Example: divide(10, 2) -> 5"""
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    @decomposition(
        intent="Calculate: 25 * 4",
        expanded_intent=(
            "Identify the operation from the expression and the two numbers. "
            "Call the matching primitive: add, subtract, multiply, or divide. "
            "Return the result directly."
        ),
    )
    def _example_multiply(self):
        result = self.multiply(25, 4)
        return result
