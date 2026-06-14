"""NoteAgent: reads and summarizes a user's private research notes.

Each agent instance is bound to one user. The read_note primitive strips
any path components from the filename before opening it, so the plan the
LLM generates can never escape the user's directory regardless of what
the input prompt says.
"""

from __future__ import annotations

import os

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class NoteAgent(PlanExecute):

    def __init__(self, user_id: str, llm) -> None:
        super().__init__(llm=llm)
        self._user_id = user_id
        self._base = os.path.join("data", user_id)

    @primitive(read_only=True)
    def list_notes(self) -> list:
        """Return the filenames of all notes belonging to this user."""
        return sorted(f for f in os.listdir(self._base) if f.endswith(".txt"))

    @primitive(read_only=True)
    def read_note(self, filename: str) -> str:
        """Read one of this user's notes.

        Any directory component in filename is stripped before the path is
        constructed, so ../other_user/file.txt becomes file.txt inside this
        user's own directory.
        """
        safe_name = os.path.basename(filename)
        path = os.path.join(self._base, safe_name)
        if not os.path.exists(path):
            available = sorted(f for f in os.listdir(self._base) if f.endswith(".txt"))
            raise FileNotFoundError(
                f"'{safe_name}' not found in {self._user_id}'s notes. "
                f"Available: {available}"
            )
        with open(path, encoding="utf-8") as f:
            return f.read()

    @primitive(read_only=True)
    def summarize(self, text: str, topic: str) -> str:
        """Summarize text in two or three sentences, focused on topic."""
        prompt = (
            f"Summarize the following text in two or three sentences, "
            f"focusing on {topic}.\n\n{text}"
        )
        return self._llm.generate(prompt).text.strip()

    @primitive(read_only=True)
    def respond(self, message: str) -> str:
        """Return message as the final response."""
        return message

    @decomposition(
        intent="List my notes.",
        expanded_intent=(
            "Call list_notes to get the filenames. "
            "Return respond with the list as a string."
        ),
    )
    def _example_list(self):
        notes = self.list_notes()
        return self.respond(str(notes))

    @decomposition(
        intent="Read newton.txt and summarize the key ideas.",
        expanded_intent=(
            "Call read_note with the filename. "
            "Call summarize with the text and a short topic description. "
            "Return respond with the summary."
        ),
    )
    def _example_read(self):
        text = self.read_note("newton.txt")
        summary = self.summarize(text, "key scientific ideas")
        return self.respond(summary)
