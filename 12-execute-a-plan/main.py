"""Run a plan you already have, and watch execute() reject the ones it shouldn't.

A plan is just text. It does not have to come from the model. You can write one
by hand, load one from a file, or take one a teammate edited, and pass the
string straight to `agent.execute(plan)`. The model is never called here.

Before it runs anything, `execute` validates the plan. It allows only assignment
statements that call your primitives (plus a few safe builtins), and it raises
on anything else: imports, file access, loops, private attributes. That is what
makes running a plan from somewhere else safe.

Usage:
    uv run main.py
"""

from __future__ import annotations

from cart import ShoppingCart
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

# A plan we wrote by hand. No model wrote this one.
PLAN = """cart = new_cart()
cart = add_item(cart, "pens", 5, 3)
cart = add_item(cart, "notebook", 8, 1)
total = cart_total(cart)"""

# Plans execute() should refuse, each paired with why it is dangerous.
BAD_PLANS = {
    "imports a module": 'x = __import__("os")',
    "opens a file": 'x = open("/etc/passwd")',
    "runs a loop": "for i in range(3):\n    x = i",
    "reaches a dunder": "x = cart_total.__globals__",
}


def main() -> None:
    model = "qwen2.5-coder:7b"
    # Kept for parity with the other native tracks; execute() never calls the model.
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)
    agent = ShoppingCart(llm=llm)

    print("--- plan ---")
    print(PLAN)

    result = agent.execute(PLAN)  # ExecutionResult, validated then run
    print("--- result ---")
    print(result.get_value())
    print()

    print("--- rejected plans ---")
    for label, bad in BAD_PLANS.items():
        try:
            agent.execute(bad)
            print(f"{label}: ran (unexpected)")
        except ValueError as e:
            print(f"{label}: {e}")


if __name__ == "__main__":
    main()
