"""Show how max_loop_iterations caps runaway loops.

DesignExecute injects a counter into every loop's AST before execution. If
the counter exceeds max_loop_iterations, the loop stops and the step is
recorded as failed.

The sum-of-squares plan loops exactly 100 times. Running it with a limit of
50 trips on iteration 51. Running it with a limit of 100 succeeds.

Usage:
    uv run main.py
"""

from __future__ import annotations

from accumulator import Accumulator

from opensymbolicai.llm import LLMConfig
from opensymbolicai.models import DesignExecuteConfig

# Loops exactly 100 times: one square() + one add() per iteration.
PLAN = """\
total = 0
for i in range(1, 101):
    sq = square(i)
    total = add(total, sq)
return format_result("Sum of squares 1 to 100", total)
"""


def run(label: str, max_loop_iterations: int) -> None:
    llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")
    config = DesignExecuteConfig(max_loop_iterations=max_loop_iterations)
    agent = Accumulator(llm=llm, config=config)

    result = agent.execute(PLAN)
    last_step = result.trace.steps[-1]

    print(f"--- {label} (max_loop_iterations={max_loop_iterations}) ---")
    if result.trace.all_succeeded:
        print("result:", result.get_value())
        print(f"primitive calls: {len(result.trace.steps)}")
    else:
        print("error:", last_step.error)
    print()


def main() -> None:
    # limit=50: loop body runs 100 times, trips on iteration 51.
    run("limit too small", max_loop_iterations=50)

    # limit=100: all 100 iterations fit.
    run("limit sufficient", max_loop_iterations=100)


if __name__ == "__main__":
    main()
