"""Calculator agent with arithmetic, factorial, and Fibonacci primitives."""

from __future__ import annotations

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Calc(PlanExecute):

    @primitive(read_only=True)
    def add(self, a: float, b: float) -> float:
        """Return a + b."""
        return a + b

    @primitive(read_only=True)
    def subtract(self, a: float, b: float) -> float:
        """Return a - b."""
        return a - b

    @primitive(read_only=True)
    def multiply(self, a: float, b: float) -> float:
        """Return a * b."""
        return a * b

    @primitive(read_only=True)
    def divide(self, a: float, b: float) -> float:
        """Return a / b."""
        return a / b

    @primitive(read_only=True)
    def factorial(self, n: int) -> int:
        """Return n! (n factorial). n must be a non-negative integer."""
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    @primitive(read_only=True)
    def fibonacci(self, n: int) -> int:
        """Return the nth Fibonacci number (0-indexed: fib(0)=0, fib(1)=1, fib(2)=1)."""
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
