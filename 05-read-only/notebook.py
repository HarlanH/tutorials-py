"""A two-primitive agent whose primitives differ in one flag.

`read_only` signals whether a primitive modifies the agent's state. `list_notes`
only reads, so it is marked `read_only=True`. `save_note` appends to the notes,
so it keeps the default, `read_only=False`. The flag is a declaration of intent
that downstream tooling can act on; on its own it does not stop or gate anything.
"""

from __future__ import annotations

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive

from opensymbolicai.llm import LLM, LLMConfig


class Notebook(PlanExecute):
    """A tiny notebook agent with one read-only and one mutating primitive."""

    def __init__(self, llm: LLM | LLMConfig) -> None:
        super().__init__(llm=llm)
        self.notes: list[str] = []

    @primitive(read_only=True)
    def list_notes(self) -> list[str]:
        """Return every note saved so far."""
        return list(self.notes)

    @primitive()  # read_only defaults to False: saving a note changes state.
    def save_note(self, text: str) -> str:
        """Save a note and return a confirmation."""
        self.notes.append(text)
        return f"saved: {text}"
