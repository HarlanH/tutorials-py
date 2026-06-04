"""Teach the planner with worked examples, then watch it follow the pattern.

A decomposition is an example you write for the planner: a method body that
composes your primitives, tagged with the natural-language intent it answers.
The library drops it into the planner's prompt under "Example Decompositions",
so the model sees how the pieces fit together before it writes its own plan.

cart.py carries two decompositions. This runs a few different orders, each
phrased its own way, none of them matching an example word for word, and the
planner reuses the pattern for each.

Usage:
    uv run main.py
"""

from __future__ import annotations

from cart import ShoppingCart
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

# Different orders, each phrased its own way, none copied from the examples.
QUERIES = [
    "ring up 5 oranges at 1 dollar each and 2 yogurts at 3 dollars each",
    "what's the damage on 3 notebooks at 4 dollars each and 2 pens at 1 dollar each?",
    "I'll take 10 eggs at 1 dollar each and 1 cake at 12 dollars",
]


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)
    agent = ShoppingCart(llm=llm)

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
