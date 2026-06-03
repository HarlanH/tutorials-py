"""Run the three-primitive Calculator agent and print the result.

The LLM writes a plan; your primitives run it in plain Python. Provider, model,
and API key all come from .env, so switching providers is a config change, not a
code change.

Usage:
    uv run main.py
"""

from __future__ import annotations

import os
from pathlib import Path

from calculator import Calculator
from dotenv import load_dotenv

from opensymbolicai.llm import LLMConfig

# Load .env sitting next to this file into the environment.
load_dotenv(Path(__file__).with_name(".env"))

PROVIDER_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
}

RUN_HINT = "Set it in .env, then run: uv run main.py"


def check_api_key(provider: str) -> bool:
    """Return True if the provider's API key is set, else print how to set it."""
    env_var = PROVIDER_ENV[provider]
    if not os.environ.get(env_var):
        print(f"{env_var} isn't set. {RUN_HINT}")
        return False
    return True


def main() -> None:
    provider = os.environ.get("LLM_PROVIDER")
    model = os.environ.get("LLM_MODEL")
    if not provider or not model:
        print(f"LLM_PROVIDER and LLM_MODEL aren't set. {RUN_HINT}")
        return
    if provider not in PROVIDER_ENV:
        print(f"Unknown LLM_PROVIDER '{provider}'. Choose one of: {', '.join(PROVIDER_ENV)}")
        return
    if not check_api_key(provider):
        return

    # Provider, model, and API key all come from the environment, not the code.
    llm = LLMConfig(provider=provider, model=model)
    agent = Calculator(llm=llm)

    result = agent.run("what is 7 times 8 minus 3")
    if not result.success:
        print(result.error)
        return
    print(result.result)  # 53


if __name__ == "__main__":
    main()
