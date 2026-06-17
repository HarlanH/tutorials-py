"""Preflight check that Ollama is running and the requested model is pulled."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

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
