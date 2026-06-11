"""Structured memory: facts stored as key-value pairs across sessions.

Four sessions on the same memory file:
  Session 1 -- user shares their name and language preference
  Session 2 -- user adds an editor preference
  Session 3 -- user asks what the agent remembers
  Session 4 -- user asks a specific question about stored facts

Usage:
    uv run main.py
"""

from __future__ import annotations

import json
import os

from memory_agent import MEMORY_FILE, MemoryAgent
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

MODEL = "qwen2.5-coder:7b"
DIVIDER = "=" * 60
THIN = "-" * 60

SESSIONS = [
    "My name is Sam and I work mainly in Go.",
    "I also prefer light mode and use VS Code.",
    "What do you know about me?",
    "What editor do I use?",
    "What coffee brand do I drink?",
]


def peek_memory() -> None:
    if not os.path.exists(MEMORY_FILE):
        print("  (memory.json does not exist yet)")
        return
    with open(MEMORY_FILE) as f:
        data = json.load(f)
    if not data:
        print("  (memory.json is empty)")
    else:
        for k, v in data.items():
            print(f"  {k}: {v}")


def main() -> None:
    if not check_ollama(MODEL):
        return

    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)

    llm = LLMConfig(provider="ollama", model=MODEL)

    for i, task in enumerate(SESSIONS, 1):
        print(DIVIDER)
        print(f"Session {i}")
        print(THIN)
        print(f"User: {task}")

        agent = MemoryAgent(llm=llm)
        result = agent.run(task)

        print(f"\nPlan:\n  {result.plan.strip()}")
        print(f"\nAgent: {result.result}")

        print("\nmemory.json after this session:")
        peek_memory()
        print()


if __name__ == "__main__":
    main()
