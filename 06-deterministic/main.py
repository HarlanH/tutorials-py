"""Run the Calendar agent and print the result.

The LLM writes a plan; your primitives run it in plain Python. The two
primitives carry different `deterministic` flags: one is pure, one reads the
clock.

Usage:
    uv run main.py
"""

from __future__ import annotations

from dates import Calendar
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    # Ollama runs locally, no API key.
    llm = LLMConfig(provider="ollama", model=model)
    agent = Calendar(llm=llm)

    result = agent.run("calculate the date of the next Monday from the current date")
    if not result.success:
        print(result.error)
        return
    print(result.result)  # e.g. 2026-06-08


if __name__ == "__main__":
    main()
