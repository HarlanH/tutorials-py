"""Run the Notebook agent and print the result.

The LLM writes a plan; your primitives run it in plain Python. Two of those
primitives carry different `read_only` flags: one reads, one writes.

Usage:
    uv run main.py
"""

from __future__ import annotations

from notebook import Notebook
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    # Ollama runs locally, no API key.
    llm = LLMConfig(provider="ollama", model=model)
    agent = Notebook(llm=llm)

    result = agent.run(
        "save notes that say buy milk, walk the dog, and call mom, "
        "then list every note"
    )
    if not result.success:
        print(result.error)
        return
    print(result.result)  # ['buy milk', 'walk the dog', 'call mom']


if __name__ == "__main__":
    main()
