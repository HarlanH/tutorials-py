"""Run the three-primitive Calculator agent and print the result.

The LLM writes a plan; your primitives run it in plain Python.

Usage:
    uv run main.py
"""

from __future__ import annotations

from calculator import Calculator
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    # Ollama runs locally, no API key.
    llm = LLMConfig(provider="ollama", model=model)
    agent = Calculator(llm=llm)

    result = agent.run("what is 7 times 8 minus 3")
    print(result.result)  # 53


if __name__ == "__main__":
    main()
