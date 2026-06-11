"""MemoryAgent: stores and recalls typed facts across sessions.

Facts are written to memory.json as key-value pairs. Each new session
loads the same file, so what the user says in session 1 is available
in session 2.
"""

from __future__ import annotations

import json
import os

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")


class MemoryAgent(PlanExecute):
    """Remembers facts about the user across sessions using a JSON file."""

    @primitive(read_only=True)
    def load_memory(self) -> str:
        """Read all stored facts from memory.json.

        Returns a formatted list of key-value pairs, or a message if nothing is stored.
        """
        if not os.path.exists(MEMORY_FILE):
            return "No facts stored yet."
        with open(MEMORY_FILE) as f:
            data = json.load(f)
        if not data:
            return "No facts stored yet."
        return "\n".join(f"{k}: {v}" for k, v in data.items())

    @primitive(read_only=False)
    def save_fact(self, key: str, value: str) -> str:
        """Save a single fact to memory.json, overwriting if the key exists.

        Example: save_fact("name", "Alex") -> "Saved: name = Alex"
        """
        data: dict = {}
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE) as f:
                data = json.load(f)
        data[key] = value
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return f"Saved: {key} = {value}"

    @primitive(read_only=True)
    def load_keys(self) -> str:
        """Return all stored keys as a comma-separated string.

        Example: load_keys() -> "name, city, timezone"
        Returns an empty string if nothing is stored.
        """
        if not os.path.exists(MEMORY_FILE):
            return ""
        with open(MEMORY_FILE) as f:
            data = json.load(f)
        return ", ".join(data.keys())

    @primitive(read_only=True)
    def get_fact(self, key: str) -> str:
        """Read a single fact by key from memory.json.

        Example: get_fact("name") -> "Alex"
        Returns an empty string if the key does not exist.
        """
        if not os.path.exists(MEMORY_FILE):
            return ""
        with open(MEMORY_FILE) as f:
            data = json.load(f)
        return data.get(key, "")

    @primitive(read_only=True)
    def select_relevant_keys(self, question: str, available_keys: str) -> str:
        """Use an LLM to pick which stored keys are relevant to answer a question.

        Returns comma-separated key names, or empty string if none match.
        Example: select_relevant_keys("What editor do I use?", "name, editor, language") -> "editor"
        """
        if not available_keys:
            return ""
        prompt = (
            f"Memory keys: {available_keys}\n"
            f"Question: {question}\n"
            f"List only the key names that are needed to answer the question, "
            f"comma-separated. If none apply, reply with 'none'."
        )
        response = self._llm.generate(prompt)
        result = response.text.strip().lower()
        return "" if result == "none" else response.text.strip()

    @primitive(read_only=True)
    def get_facts_for_keys(self, keys: str) -> str:
        """Fetch values for a comma-separated list of keys from memory.json.

        Returns formatted key: value lines, or 'No results found.' if none match.
        Example: get_facts_for_keys("name, editor") -> "name: Sam\\neditor: VS Code"
        """
        if not keys:
            return "No results found."
        if not os.path.exists(MEMORY_FILE):
            return "No results found."
        with open(MEMORY_FILE) as f:
            data = json.load(f)
        key_list = [k.strip() for k in keys.split(",")]
        found = [(k, data[k]) for k in key_list if k in data]
        if not found:
            return "No results found."
        return "\n".join(f"{k}: {v}" for k, v in found)

    @primitive(read_only=True)
    def respond(self, message: str) -> str:
        """Return the message as the final response.

        Example: respond("Your name is Alex.") -> "Your name is Alex."
        """
        return message

    @decomposition(
        intent="Call me Alex. I work in Berlin and my timezone is CET.",
        expanded_intent="Assign each save_fact call to a variable, then return the respond call.",
    )
    def _example_remember(self):
        r1 = self.save_fact("name", "Alex")
        r2 = self.save_fact("city", "Berlin")
        r3 = self.save_fact("timezone", "CET")
        return self.respond("Got it! I've saved your name, city, and timezone.")

    @decomposition(
        intent="I use a standing desk and prefer morning meetings.",
        expanded_intent="Assign each save_fact call to a variable, then return the respond call.",
    )
    def _example_remember_2(self):
        r1 = self.save_fact("desk_type", "standing")
        r2 = self.save_fact("meeting_preference", "morning")
        return self.respond("Noted! I've saved your desk type and meeting preference.")

    @decomposition(
        intent="What do you know about me?",
        expanded_intent="Assign load_memory to a variable, then return the respond call with that variable.",
    )
    def _example_recall(self):
        memory = self.load_memory()
        return self.respond(memory)

    @decomposition(
        intent="What language do I use?",
        expanded_intent=(
            "Call load_keys to get the available keys. "
            "Call select_relevant_keys with the question and the keys to let the LLM decide which are relevant. "
            "Call get_facts_for_keys with the result to fetch the values. "
            "Return the respond call with the values."
        ),
    )
    def _example_get_fact(self):
        keys = self.load_keys()
        relevant = self.select_relevant_keys("What language do I use?", keys)
        values = self.get_facts_for_keys(relevant)
        return self.respond(values)
