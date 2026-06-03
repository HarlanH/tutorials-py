"""Run Track 1's Calculator on several queries and read result.plan each time.

The LLM wrote a plan: a small Python program that calls your primitives. It did
no arithmetic itself. Your primitives ran the plan in plain Python, and the
numbers they produced stayed in your process; none of them went back to the
model.

Different queries produce different plans. The same three primitives get
arranged into a single call, a chain of calls, or a mix of calls and plain
assignments, depending on what was asked.

Usage:
    uv run main.py
"""

from __future__ import annotations

from calculator import Calculator
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

QUERIES = [
    "what is 7 times 8 minus 3",
    "subtract 5 from 100",
    "multiply 6 by 4, add 2, then subtract 5",
    "I have 3 boxes of 12 apples and eat 5, how many are left",
]


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    # Ollama runs locally, no API key.
    llm = LLMConfig(provider="ollama", model=model)
    agent = Calculator(llm=llm)

    for query in QUERIES:
        result = agent.run(query)
        print("--- intent ---")
        print(result.task)  # the query, echoed back on the result
        print("--- plan ---")
        print(result.plan)  # the Python the LLM wrote, before any of it ran
        if not result.success:
            print("--- error ---")
            print(result.error)  # the plan was written but didn't run cleanly
        else:
            print("--- result ---")
            print(result.result)  # computed by your primitives
        print()


if __name__ == "__main__":
    main()
