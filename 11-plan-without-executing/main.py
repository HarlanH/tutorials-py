"""Plan a task without running it, look at the plan, then run it on purpose.

`agent.run(task)` plans and executes in one call. This track splits that in two.
`agent.plan(task)` asks the model for a plan and hands it back as a PlanResult,
and nothing has run yet: no primitive was called, no cart was built. You get the
program as text, with the tokens and time the planning cost. Only when you call
`agent.execute(plan)` does the plan actually run.

That gap is the point. Between planning and executing you can read the plan, log
it, or refuse it. The model's output is just text until you choose to run it.

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

    print("--- intent ---")
    print(QUERY)  # PlanResult has no task field, so print the query itself
    print()

    # Step 1: plan the task. This calls the model but runs nothing.
    plan_result = agent.plan(QUERY)  # PlanResult

    print("--- plan ---")
    print(plan_result.plan)  # the program, as text, before it runs
    print("--- planning cost ---")
    print("usage:", plan_result.usage)  # a TokenUsage object
    print("time (s):", round(plan_result.time_seconds, 4))
    print()

    # Review the plan here: read it, log it, gate it. Nothing has run yet.

    # Step 2: the plan looks right, so run it.
    exec_result = agent.execute(plan_result.plan)  # ExecutionResult

    print("--- result ---")
    print(exec_result.get_value())


if __name__ == "__main__":
    main()
