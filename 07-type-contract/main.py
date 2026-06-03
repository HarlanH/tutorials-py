"""Run the TextKit agent and print the plan, then the result.

The LLM writes a plan from the primitive signatures, and your primitives run it
in plain Python. Printing the plan shows how the type annotations reach the
model: text arrives quoted, the count arrives as a bare integer.

Usage:
    uv run main.py
"""

from __future__ import annotations

from textkit import TextKit
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    # Ollama runs locally, no API key.
    llm = LLMConfig(provider="ollama", model=model)
    agent = TextKit(llm=llm)

    result = agent.run("repeat the word go 3 times, then shout the result")

    print("--- plan ---")
    print(result.plan)  # the generated program, before it runs
    if not result.success:
        print("--- error ---")
        print(result.error)
        return
    print("--- result ---")
    print(result.result)  # GOGOGO!


if __name__ == "__main__":
    main()
