"""Run the LetterCounter agent and print the result.

The LLM writes a plan; your registered primitive runs it in plain Python.

Usage:
    uv run main.py
"""

from __future__ import annotations

from counter import LetterCounter
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    # Ollama runs locally, no API key.
    llm = LLMConfig(provider="ollama", model=model)
    agent = LetterCounter(llm=llm)

    result = agent.run("how many times does the letter r appear in strawberry")
    if not result.success:
        print(result.error)
        return
    print(result.result)  # 3


if __name__ == "__main__":
    main()
