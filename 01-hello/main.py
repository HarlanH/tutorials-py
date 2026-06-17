"""Run the three-primitive Calculator agent and print the result.

The LLM writes a plan; your primitives run it in plain Python. Provider, model,
and API key all come from .env, so switching providers is a config change, not a
code change.

Usage:
    cp .env.example .env   # then fill in KILO_API_KEY (or set LLM_PROVIDER=ollama)
    uv run main.py
"""

from __future__ import annotations

import os
from pathlib import Path

from calculator import Calculator
from dotenv import load_dotenv
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

load_dotenv(Path(__file__).with_name(".env"))

PROVIDERS = {
    "kilo": "KILO_API_KEY",
    "ollama": None,
}

RUN_HINT = "Set it in .env, then run: uv run main.py"


def main() -> None:
    provider = os.environ.get("LLM_PROVIDER")
    model = os.environ.get("LLM_MODEL")
    if not provider or not model:
        print(f"LLM_PROVIDER and LLM_MODEL must be set. {RUN_HINT}")
        return
    if provider not in PROVIDERS:
        print(f"Unknown LLM_PROVIDER '{provider}'. Choose one of: {', '.join(PROVIDERS)}")
        return

    kwargs: dict = {"provider": "ollama" if provider == "ollama" else "openai", "model": model}

    if provider == "kilo":
        api_key = os.environ.get("KILO_API_KEY")
        if not api_key:
            print(f"KILO_API_KEY isn't set. {RUN_HINT}")
            return
        kwargs["api_key"] = api_key
        kwargs["base_url"] = os.environ.get("KILO_BASE_URL", "https://api.kilo.ai/api/gateway")
    else:
        if not check_ollama(model):
            return

    llm = LLMConfig(**kwargs)
    agent = Calculator(llm=llm)

    result = agent.run("what is 7 times 8 minus 3")
    if not result.success:
        print(result.error)
        return
    print(result.result)  # 53


if __name__ == "__main__":
    main()
