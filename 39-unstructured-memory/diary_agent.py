"""DiaryAgent: logs free-text session notes that persist across sessions.

Each session appends one line to diary.txt. The next session reads the
full diary as context before responding.
"""

from __future__ import annotations

import os

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive

DIARY_FILE = os.path.join(os.path.dirname(__file__), "diary.txt")


class DiaryAgent(PlanExecute):
    """Logs and recalls session notes using a plain text file."""

    @primitive(read_only=True)
    def read_diary(self) -> str:
        """Read all past session notes from diary.txt.

        Returns the full diary, or a message if there are no entries yet.
        Example: read_diary() -> "Optimised slow query by adding an index."
        """
        if not os.path.exists(DIARY_FILE):
            return "No entries yet."
        content = open(DIARY_FILE).read().strip()
        return content if content else "No entries yet."

    @primitive(read_only=False)
    def append_diary(self, entry: str) -> str:
        """Append one line to diary.txt.

        Keep the entry short: one sentence describing what the user said.
        Example: append_diary("Optimised slow query by adding an index on user_id.") -> "Logged."
        """
        with open(DIARY_FILE, "a") as f:
            f.write(entry.strip() + "\n")
        return "Logged."

    @primitive(read_only=True)
    def summarize(self, text: str) -> str:
        """Use an LLM to summarize diary entries into a short answer.

        Example: summarize("Debugging memory leak...\\nFixed pool...") -> "You were debugging a memory leak..."
        """
        prompt = (
            f"Diary entries:\n{text}\n\n"
            f"Summarize what the user has been working on in 2-3 sentences."
        )
        response = self._llm.generate(prompt)
        return response.text.strip()

    @primitive(read_only=True)
    def respond(self, message: str) -> str:
        """Return the message as the final response.

        Example: respond("Logged your progress.") -> "Logged your progress."
        """
        return message

    @decomposition(
        intent="I spent the day optimising a slow PostgreSQL query. Added an index on user_id.",
        expanded_intent=(
            "Assign append_diary to a variable with a one-sentence summary of what the user said. "
            "Then return the respond call to acknowledge. "
            "Do not call read_diary or summarize."
        ),
    )
    def _example_log(self):
        r = self.append_diary("Optimised slow PostgreSQL query by adding an index on user_id.")
        return self.respond("Logged. Good progress on the query optimisation.")

    @decomposition(
        intent="Rolled back the index change after it caused a regression in the nightly job.",
        expanded_intent=(
            "Assign append_diary to a variable with a one-sentence summary of what the user said. "
            "Then return the respond call to acknowledge. "
            "Do not call read_diary or summarize."
        ),
    )
    def _example_log_2(self):
        r = self.append_diary("Rolled back index change after it caused a regression in the nightly job.")
        return self.respond("Logged. I've noted the rollback.")

    @decomposition(
        intent="What have I been working on lately?",
        expanded_intent=(
            "Call read_diary to fetch the entries. "
            "Call summarize to process them with an LLM. "
            "Then return the respond call with the summary."
        ),
    )
    def _example_recall(self):
        diary = self.read_diary()
        summary = self.summarize(diary)
        return self.respond(summary)
