"""Multi-turn shopping cart.

Four turns: add a first batch of items, add more, remove a few, get the total.
The cart is created when the agent is instantiated and persists across all turns.

Usage:
    uv run main.py
"""

from __future__ import annotations

from cart import ShoppingCart
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig
from opensymbolicai.models import PlanExecuteConfig

TASKS = [
    (
        "Add to the cart: milk at $2.50, eggs at $3.99, bread at $4.50, "
        "butter at $5.99, yogurt at $1.99, and cheese at $6.50."
    ),
    (
        "Add to the cart: chicken at $8.99, pasta at $2.25, tomatoes at $3.50, "
        "garlic at $1.50, olive oil at $7.99, and onions at $1.25."
    ),
    "Remove eggs and butter from the cart.",
    "What is the total?",
]


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)
    config = PlanExecuteConfig(multi_turn=True)
    agent = ShoppingCart(llm=llm, config=config)

    for task in TASKS:
        result = agent.run(task)
        print("---", task)
        print("plan:")
        for line in result.plan.splitlines():
            print(" ", line)
        if result.success:
            print("result:", result.result)
        else:
            print("error:", result.error)
        print()


if __name__ == "__main__":
    main()
