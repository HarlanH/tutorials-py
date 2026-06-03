"""A two-primitive agent whose primitives differ in the `deterministic` flag.

`deterministic` signals whether a primitive is a pure function: same inputs,
same output. `next_monday` is pure, so it keeps the default `deterministic=True`.
`today` reads the system clock, so its result depends on when it runs; it is
marked `deterministic=False`. The flag is metadata that downstream validation
tooling reads; on its own it does not change how a plan executes.
"""

from __future__ import annotations

from datetime import date, timedelta

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Calendar(PlanExecute):
    """A tiny calendar agent with one pure and one clock-reading primitive."""

    @primitive(read_only=True, deterministic=False)  # depends on the clock
    def today(self) -> date:
        """Return today's date."""
        return date.today()

    @primitive(read_only=True)  # deterministic defaults to True: a pure function
    def next_monday(self, d: date) -> date:
        """Return the date of the first Monday after `d`."""
        days_ahead = (0 - d.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return d + timedelta(days=days_ahead)
