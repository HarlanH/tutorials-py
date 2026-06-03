"""Run the TextKit agent and print the plan, then the result.

The LLM writes a plan from the primitive signatures, and your primitives run it
in plain Python. Printing the plan shows how the type annotations reach the
model: text arrives quoted, the count arrives as a bare integer.

Usage:
    uv run main.py
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from textkit import TextKit

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
    agent = TextKit(llm=llm)

    result = agent.run("repeat the word go 3 times, then shout the result")
    print(result.plan)  # the generated program, before it runs
    if not result.success:
        print(result.error)
        return
    print(result.result)  # GOGOGO!


if __name__ == "__main__":
    main()
