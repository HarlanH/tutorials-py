"""A two-primitive agent whose type annotations form the LLM's contract.

The planner never sees these method bodies. It sees their signatures, built
straight from your annotations: `repeat(text: str, times: int) -> str` and
`shout(text: str) -> str`. Those types tell the planner what each argument is,
so it knows to pass text as a quoted string and a count as a bare integer.
"""

from __future__ import annotations

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class TextKit(PlanExecute):
    """A tiny text agent with two typed primitives."""

    @primitive(read_only=True)
    def repeat(self, text: str, times: int) -> str:
        """Repeat text the given number of times."""
        return text * times

    @primitive(read_only=True)
    def shout(self, text: str) -> str:
        """Return text uppercased with an exclamation mark."""
        return text.upper() + "!"
