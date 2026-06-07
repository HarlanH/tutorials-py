"""No-progress circuit breaker — max_iterations stops a GoalSeeking agent
that hasn't converged yet.

The guesser binary-searches a secret number (742) in 1-1000. That takes
~10 iterations. With a tight limit the circuit breaker fires first.
  Run 1: max_iterations=3  → fires before converging (MAX_ITERATIONS)
  Run 2: max_iterations=15 → enough room to converge (ACHIEVED)

Usage:
    uv run main.py
"""

from __future__ import annotations

from guesser import GOAL, Guesser, HintContext
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig
from opensymbolicai.models import ExecutionResult, GoalSeekingConfig, GoalStatus

RUNS = [
    ("max_iterations=3 ", 3),
    ("max_iterations=15", 15),
]


class VerboseGuesser(Guesser):
    """Guesser that prints each iteration's range and hint."""

    def update_context(self, context: HintContext, execution_result: ExecutionResult) -> None:
        super().update_context(context, execution_result)
        print(f"    iteration {context.iteration_count}: [{context.low}, {context.high}]  hint={context.last_hint!r}")


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    for label, max_iter in RUNS:
        config = GoalSeekingConfig(max_iterations=max_iter)
        agent = VerboseGuesser(llm=llm, config=config)

        print(f"Run: {label}")
        result = agent.seek(GOAL)

        if result.status == GoalStatus.ACHIEVED:
            print(f"  Status: ACHIEVED in {result.iteration_count} iteration(s)")
        else:
            print(f"  Status: MAX_ITERATIONS — circuit breaker fired after {result.iteration_count} iteration(s)")
        print()


if __name__ == "__main__":
    main()
