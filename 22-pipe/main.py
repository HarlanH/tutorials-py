"""Show that a large intermediate list never appears in the LLM prompt.

Each task runs on two dataset sizes. The plan pipes monthly_returns() into
an aggregator via a Python variable. The list is never serialized into any
prompt — the same plan works whether the list has 100 entries or 100,000.

Usage:
    uv run main.py
"""

from __future__ import annotations

import time

from analyst import ReturnAnalyst
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

TASKS = [
    "What is the mean monthly return?",
    "What fraction of months had a positive return?",
    "What is the range between the best and worst monthly return?",
]

SIZES = [100, 100_000]


def run(n: int, llm: LLMConfig, task: str) -> None:
    agent = ReturnAnalyst(n=n, llm=llm)

    result = agent.run(task)

    print(f"  n={n:>7,}  Result ->  {result.result}")
    print(f"  plan:")
    for line in result.plan.splitlines():
        print(f"    {line}")
    print()


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    for task in TASKS:
        print(f"\n{'='*60}")
        print(f"Task: {task}\n")
        for n in SIZES:
            run(n, llm, task)


if __name__ == "__main__":
    main()
