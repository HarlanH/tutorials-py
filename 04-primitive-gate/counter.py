"""A one-primitive agent that counts letters.

`@primitive` is the gate: it registers a method so the planner is allowed to
call it. A plain method, with no decorator, is invisible to the planner. The
type annotations are the planner's contract, and the docstring is its guidance.
"""

from __future__ import annotations

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class LetterCounter(PlanExecute):
    """A tiny agent with a single registered primitive."""

    @primitive(read_only=True)
    def count_letter(self, word: str, letter: str) -> int:
        """Count how many times `letter` appears in `word`."""
        return word.count(letter)
