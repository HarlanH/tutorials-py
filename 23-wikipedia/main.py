"""Wikipedia analyst: answer questions by fetching and analysing articles.

Each task fetches one or more Wikipedia articles. The text lives in Python
variables and is never serialized back into any LLM prompt.

Usage:
    uv run main.py
"""

from __future__ import annotations

import time

from analyst import WikipediaAnalyst
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

TASKS = [
    "Which has a longer Wikipedia article: Python or JavaScript?",
    "Does 'algorithm' appear more in the Artificial Intelligence article or the Computer Science article?",
    "What are the 5 most common words across the Python and JavaScript articles combined?",
    "What is the sentiment of the Alan Turing Wikipedia article?",
]


def run(llm: LLMConfig, task: str) -> None:
    agent = WikipediaAnalyst(llm=llm)
    result = agent.run(task)

    fetched = {topic: len(text) for topic, text in agent._cache.items()}
    pipe_summary = ", ".join(f'"{t}" ({n:,} chars)' for t, n in fetched.items())

    print(f"Task:   {task}")
    print(f"Pipe:   fetched {pipe_summary}")
    print(f"        {sum(fetched.values()):,} chars total in Python namespace, 0 in the planning prompt")
    print(f"Result: {result.result}")
    print(f"Plan:")
    for line in result.plan.splitlines():
        print(f"  {line}")
    print()


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    for task in TASKS:
        print(f"{'='*60}")
        run(llm, task)
        time.sleep(2)


if __name__ == "__main__":
    main()
