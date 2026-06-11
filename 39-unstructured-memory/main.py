"""Unstructured memory: session notes appended to a plain text file.

Three sessions on the same diary file:
  Session 1 -- user describes a bug they are debugging
  Session 2 -- user reports progress on the same bug
  Session 3 -- user asks where they left off

Usage:
    uv run main.py
"""

from __future__ import annotations

import os

from diary_agent import DIARY_FILE, DiaryAgent
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

MODEL = "qwen2.5-coder:7b"
DIVIDER = "=" * 60
THIN = "-" * 60

SESSIONS = [
    "I'm debugging a memory leak in my Flask app. Narrowed it to the connection pool.",
    "Fixed the pool issue by setting pool_recycle=1800. Now testing the API endpoints.",
    "Where did I leave off on my Flask project?",
]


def peek_diary() -> None:
    if not os.path.exists(DIARY_FILE):
        print("  (diary.txt does not exist yet)")
        return
    lines = open(DIARY_FILE).read().strip().splitlines()
    if not lines:
        print("  (diary.txt is empty)")
    else:
        for line in lines:
            print(f"  {line}")


def main() -> None:
    if not check_ollama(MODEL):
        return

    if os.path.exists(DIARY_FILE):
        os.remove(DIARY_FILE)

    llm = LLMConfig(provider="ollama", model=MODEL)

    for i, task in enumerate(SESSIONS, 1):
        print(DIVIDER)
        print(f"Session {i}")
        print(THIN)
        print(f"User: {task}")

        agent = DiaryAgent(llm=llm)
        result = agent.run(task)

        print(f"\nPlan:\n  {result.plan.strip()}")
        print(f"\nAgent: {result.result}")

        print("\ndiary.txt after this session:")
        peek_diary()
        print()


if __name__ == "__main__":
    main()
