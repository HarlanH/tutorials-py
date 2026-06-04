"""Teach the planner an approach, not just a pattern.

Track 14 gave the planner a worked example: an intent and a body. A decomposition
takes one more field, expanded_intent, a sentence describing the approach the
example uses. The library renders it as an "Approach:" line in the prompt, right
above the code, so the planner reads the reasoning before the steps.

The finance glossary's approach is worth spelling out, because the order matters:
expand the acronym first, then define the full form, then phrase the answer. This
runs a few obscure finance acronyms and the planner follows that two-stage
approach for each.

Usage:
    uv run main.py
"""

from __future__ import annotations

from glossary import Glossary
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

# Forward: given an acronym, expand and define it.
# Reverse: given a full term, find the acronym and define it.
QUERIES = [
    "what does KIKO mean?",
    "what does TARN mean?",
    "what does CDXIG mean?",
    "what is the acronym for Carr-Geman-Madan-Yor model?",
    "what is the acronym for vega-gamma sensitivity?",
]


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)
    agent = Glossary(llm=llm)

    for query in QUERIES:
        result = agent.run(query)
        print("--- intent ---")
        print(result.task)
        print("--- plan ---")
        print(result.plan)
        if not result.success:
            print("--- error ---")
            print(result.error)
        else:
            print("--- result ---")
            print(result.result)
        print()


if __name__ == "__main__":
    main()
