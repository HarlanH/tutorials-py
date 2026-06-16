"""Token accounting — how many tokens does each task cost?

Each call to agent.run() returns result.metrics.plan_tokens with
input_tokens and output_tokens. The input is fixed (system prompt +
primitives + task). The output grows with plan complexity.

Usage:
    uv run main.py
"""

from __future__ import annotations

from calc import Calc
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

TASKS = [
    "What is 7 + 3?",
    "What is 12 * 15 - 47?",
    "What is 8 factorial?",
    "What is the 10th Fibonacci number?",
    "What is 6 factorial plus the 8th Fibonacci number?",
    "What is (factorial of 5) divided by (fibonacci of 6), then add 12?",
]


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    rows = []
    for task in TASKS:
        agent = Calc(llm=llm)
        result = agent.run(task)
        if not result.success:
            print(f"Task failed: {task}")
            print(f"Error: {result.error}")
            return
        t = result.metrics.plan_tokens
        rows.append((task, result.result, t.input_tokens, t.output_tokens, t.total_tokens))

    print(f"Provider : {llm.provider}")
    print(f"Model    : {llm.model}")
    print()

    col = 46
    print(f"{'Task':<{col}}  {'Result':>10}  {'In tokens':>10}  {'Out tokens':>10}  {'Total tokens':>12}")
    print("-" * (col + 50))
    for task, value, inp, out, total in rows:
        label = task if len(task) <= col else task[: col - 1] + "…"
        print(f"{label:<{col}}  {str(value):>10}  {inp:>10}  {out:>10}  {total:>12}")

    print()
    total_in  = sum(r[2] for r in rows)
    total_out = sum(r[3] for r in rows)
    print(f"{'Totals':<{col}}  {'':>10}  {total_in:>10}  {total_out:>10}  {total_in + total_out:>12}")


if __name__ == "__main__":
    main()
