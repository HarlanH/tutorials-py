"""Run the ShoppingCart agent and walk result.trace, one step at a time.

The previous track (Track 8) read result.plan: the code the LLM wrote, before
any of it ran. This track reads result.trace, that same code after it ran. Each
line of the plan becomes a step, and each step records what it executed, the
value it produced, and the namespace before and after. Reading the trace, you
watch the cart fill up one item at a time.

Usage:
    uv run main.py
"""

from __future__ import annotations

from cart import ShoppingCart
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

QUERY = (
    "add 2 apples at 3 dollars each, 2 loaves of bread at 2 dollars each, "
    "and 3 cartons of milk at 4 dollars each, then total it up"
)


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    # Ollama runs locally, no API key.
    llm = LLMConfig(provider="ollama", model=model)
    agent = ShoppingCart(llm=llm)

    result = agent.run(QUERY)
    if not result.success:
        print(result.error)
        return

    print("--- intent ---")
    print(result.task)  # the query, echoed back on the result
    print()

    print("--- plan ---")
    print(result.plan)  # the whole program, as a string
    print()

    print("--- trace ---")
    trace = result.trace  # ExecutionTrace: the plan after it ran
    for step in trace.steps:
        print(f"step {step.step_number}: {step.statement}")
        print(f"  namespace before: {step.namespace_before}")
        print(f"  value:            {step.result_value}")
        print(f"  namespace after:  {step.namespace_after}")
        print()

    print("every step succeeded:", trace.all_succeeded)
    print("failed steps:", trace.failed_steps)


if __name__ == "__main__":
    main()
