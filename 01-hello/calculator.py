"""Track 1: a three-primitive agent.

A *primitive* is the core building block: a typed, documented method the
planner is allowed to call. The base class `PlanExecute` turns a written
task into a plan (a small Python program) that calls these primitives, then
runs that plan in plain Python in your process.
"""

from __future__ import annotations

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Calculator(PlanExecute):
    """A tiny calculator agent with three primitives."""

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
