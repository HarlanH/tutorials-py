"""Combine flat item totals with a tiered discount, then read the trace.

This track introduces no new API. The agent uses DesignExecute (Track 17),
a plan with an if/elif/else conditional (Track 17), and reads the trace
(Track 9) to see which discount tier fired and what each step returned.

Three tasks exercise each tier so you can compare the traces side by side.

Usage:
    uv run main.py
"""

from __future__ import annotations

from cart import Cart
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

TASKS = [
    # Subtotal ~$26.94: no discount tier.
    (
        "no discount",
        "How much for 2 pens, 3 notebooks, and 1 stapler?",
    ),
    # Subtotal ~$91.89: 10% tier.
    (
        "10% tier",
        "How much for 2 pens, 3 notebooks, 1 stapler, and 5 books?",
    ),
    # Subtotal ~$249.89: 15% tier.
    (
        "15% tier",
        "How much for 2 pens, 3 notebooks, 1 stapler, 5 books, and 2 keyboards?",
    ),
]


def run_and_print(agent: Cart, label: str, task: str) -> None:
    result = agent.run(task)

    print(f"=== {label} ===")
    print("task:", task)
    print()
    print("plan:")
    print(result.plan)
    print()

    if not result.success:
        print("error:", result.error)
        print()
        return

    print("trace:")
    for step in result.trace.steps:
        status = "ok" if step.success else "FAIL"
        value = repr(step.result_value) if step.result_value is not None else ""
        print(f"  step {step.step_number:2d} [{status}] {step.statement}")
        if value:
            print(f"           -> {value}")
    print()
    print("result:", result.result)
    print()


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)
    agent = Cart(llm=llm)

    for label, task in TASKS:
        run_and_print(agent, label, task)


if __name__ == "__main__":
    main()
