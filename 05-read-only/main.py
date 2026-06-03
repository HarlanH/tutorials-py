"""Run the Notebook agent and print the result.

The LLM writes a plan; your primitives run it in plain Python. Two of those
primitives carry different `read_only` flags: one reads, one writes.

Usage:
    uv run main.py
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from notebook import Notebook

from opensymbolicai.llm import LLMConfig

OLLAMA_URL = "http://localhost:11434"


def check_ollama(model: str) -> bool:
    """Return True if Ollama is running and `model` is pulled, else print why."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as resp:
            tags = json.load(resp)
    except urllib.error.URLError:
        print("Ollama isn't running. Start the Ollama app (or run `ollama serve`).")
        return False

    installed = {m["name"] for m in tags.get("models", [])}
    if model not in installed:
        print(f"Model '{model}' isn't pulled. Run: ollama pull {model}")
        return False

    return True


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
