"""Print the prompt the LLM receives before it writes a plan.

build_plan_prompt(task) builds the full prompt string without calling the LLM.
The prompt has three sections: DEFINITIONS, CONTEXT, and INSTRUCTIONS. This
script prints each one in turn so you can see exactly what the model reads.

Usage:
    uv run main.py
"""

from __future__ import annotations

from calculator import Calculator

from opensymbolicai.llm import LLMConfig
from opensymbolicai.models import (
    PROMPT_CONTEXT_BEGIN,
    PROMPT_CONTEXT_END,
    PROMPT_DEFINITIONS_BEGIN,
    PROMPT_DEFINITIONS_END,
    PROMPT_INSTRUCTIONS_BEGIN,
    PROMPT_INSTRUCTIONS_END,
)

TASK = "what is 7 times 8 minus 3?"

SECTION_LABELS = {
    PROMPT_DEFINITIONS_BEGIN: "DEFINITIONS START",
    PROMPT_DEFINITIONS_END: "DEFINITIONS END",
    PROMPT_CONTEXT_BEGIN: "CONTEXT START",
    PROMPT_CONTEXT_END: "CONTEXT END",
    PROMPT_INSTRUCTIONS_BEGIN: "INSTRUCTIONS START",
    PROMPT_INSTRUCTIONS_END: "INSTRUCTIONS END",
}


def annotate(prompt: str) -> str:
    """Replace section markers with labeled dividers."""
    for marker, label in SECTION_LABELS.items():
        prompt = prompt.replace(marker, f"# --- {label} ---")
    return prompt


def main() -> None:
    # A real LLMConfig is needed to construct the agent, but build_plan_prompt
    # never calls the LLM, so Ollama does not need to be running.
    llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")
    agent = Calculator(llm=llm)

    prompt = agent.build_plan_prompt(TASK)
    print(annotate(prompt))


if __name__ == "__main__":
    main()
