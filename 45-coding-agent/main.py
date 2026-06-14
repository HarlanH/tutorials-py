"""Track 45: coding agent.

CodingAgent reads a recursive Python program, rewrites it as iterative,
saves it in place, then runs it to confirm the output is unchanged.
The diff between original and rewritten is printed for each program.
"""

from __future__ import annotations

import difflib
import sys
import time
from pathlib import Path

from opensymbolicai.llm import InMemoryCache, LLMConfig, create_llm

from coding_agent import CodingAgent
from ollama import check_ollama

MODEL = "qwen2.5-coder:7b"

TASKS = [
    {
        "path": "programs/fib.py",
        "instruction": (
            "Convert the recursive fibonacci function to iterative. "
            "Keep the same function signature and the same printed output."
        ),
    },
    {
        "path": "programs/factorial.py",
        "instruction": (
            "Convert the recursive factorial function to iterative. "
            "Keep the same function signature and the same printed output."
        ),
    },
    {
        "path": "programs/binary_search.py",
        "instruction": (
            "Convert the recursive binary_search function to iterative. "
            "Keep the same function signature and the same printed output."
        ),
    },
]


def show_diff(original: str, updated: str, path: str) -> None:
    lines_a = original.splitlines(keepends=True)
    lines_b = updated.splitlines(keepends=True)
    diff = list(difflib.unified_diff(lines_a, lines_b, fromfile=f"a/{path}", tofile=f"b/{path}"))
    if diff:
        print("".join(diff), end="")
    else:
        print("  (no change)")


def main() -> None:
    if not check_ollama(MODEL):
        sys.exit(1)

    llm = create_llm(LLMConfig(provider="ollama", model=MODEL), cache=InMemoryCache())
    agent = CodingAgent(llm=llm)

    print(f"Model: {MODEL}")
    print("=" * 60)

    for task in TASKS:
        path = task["path"]
        instruction = task["instruction"]

        original = Path(path).read_text(encoding="utf-8")

        print(f"\n{path}")
        print("-" * 40)

        t0 = time.time()
        result = agent.run(f"Convert {path} from recursive to iterative. {instruction}")
        elapsed = time.time() - t0

        updated = Path(path).read_text(encoding="utf-8")

        print("Diff:")
        show_diff(original, updated, path)
        print(f"\nOutput ({elapsed:.1f}s):")
        print(f"  {result.result}")


if __name__ == "__main__":
    main()
