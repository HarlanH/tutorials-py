"""Run the ShoppingCart agent and read result.metrics.

Track 8 read result.plan, Track 9 read result.trace. This track reads
result.metrics: what the run cost. The numbers split cleanly in two. Planning,
the one LLM call that wrote the plan, took most of the time and all of the
tokens. Executing the plan, your primitives running in plain Python, took almost
no time and no tokens at all.

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

    print("--- metrics ---")
    m = result.metrics  # ExecutionMetrics
    print("provider:", m.provider)
    print("model:", m.model)
    print("steps executed:", m.steps_executed)
    print("plan tokens:", m.plan_tokens)  # a TokenUsage object
    print("  input:", m.plan_tokens.input_tokens)
    print("  output:", m.plan_tokens.output_tokens)
    print("  total:", m.plan_tokens.total_tokens)
    print("plan time (s):", round(m.plan_time_seconds, 4))
    print("execute time (s):", round(m.execute_time_seconds, 4))
    print("total time (s):", round(m.total_time_seconds, 4))


if __name__ == "__main__":
    main()
