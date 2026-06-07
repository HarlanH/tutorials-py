"""Return analyst: monthly returns piped as a variable into an aggregator.

The LLM generates a plan like:

    monthly = self.monthly_returns()
    return self.stdev_of(values=monthly)

The list lives in the plan's Python namespace — never serialized into a prompt.
"""

from __future__ import annotations

import random
import statistics

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


def generate_monthly_returns(n: int, seed: int = 42) -> list[float]:
    """Synthetic monthly returns: ~normal(0.008, 0.04)."""
    rng = random.Random(seed)
    return [round(rng.gauss(0.008, 0.04), 6) for _ in range(n)]


class ReturnAnalyst(PlanExecute):
    """Answers questions about a monthly-return series."""

    def __init__(self, n: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self._monthly = generate_monthly_returns(n)

    @primitive(read_only=True)
    def monthly_returns(self) -> list[float]:
        """Monthly return series for the full dataset."""
        return self._monthly

    @primitive(read_only=True)
    def stdev_of(self, values: list[float]) -> float:
        """Sample standard deviation of a list of floats."""
        return round(statistics.stdev(values), 6)

    @primitive(read_only=True)
    def mean_of(self, values: list[float]) -> float:
        """Arithmetic mean of a list of floats."""
        return round(sum(values) / len(values), 6)

    @primitive(read_only=True)
    def max_of(self, values: list[float]) -> float:
        """Largest value in the list."""
        return round(max(values), 6)

    @primitive(read_only=True)
    def min_of(self, values: list[float]) -> float:
        """Smallest value in the list."""
        return round(min(values), 6)

    @primitive(read_only=True)
    def count_positive(self, values: list[float]) -> int:
        """Number of positive values in the list."""
        return sum(1 for v in values if v > 0)

    @primitive(read_only=True)
    def len_of(self, values: list[float]) -> int:
        """Number of entries in the list."""
        return len(values)

    @primitive(read_only=True)
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return round(a - b, 6)

    @primitive(read_only=True)
    def divide(self, a: float, b: float) -> float:
        """Divide a by b."""
        return round(a / b, 6)
