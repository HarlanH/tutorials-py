"""A goal-seeking agent that guesses a secret number from temperature hints.

Usage:
    uv run main.py
"""

from __future__ import annotations

from guesser import GOAL, SECRET, Guesser
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig
from opensymbolicai.models import Iteration

# Toggle to print the plan and trace for each iteration.
SHOW_PLANS = True


def guess_step(iteration: Iteration):
    return next(
        (s for s in iteration.execution_result.trace.steps if s.primitive_called == "guess"),
        None,
    )


def print_plan(iteration: Iteration) -> None:
    for line in iteration.plan_result.plan.splitlines():
        print(f"    {line}")
    print()


def print_trace(iteration: Iteration) -> None:
    for s in iteration.execution_result.trace.steps:
        status = "ok  " if s.success else "FAIL"
        val = repr(s.result_value) if s.result_value is not None else s.error or ""
        print(f"    [{status}] {s.statement:<40}  -> {val}")
    print()


def print_iteration(iteration: Iteration) -> None:
    step = guess_step(iteration)
    n_arg = step.args.get("n") or step.args.get("arg0") if step else None
    n = int(n_arg.resolved_value) if n_arg else "—"
    hint = str(step.result_value) if step and step.result_value else "—"
    achieved = iteration.evaluation.goal_achieved

    print(f"iteration {iteration.iteration_number:2d}: guess={n!s:>4}  hint={hint:<25} {'✓' if achieved else ''}")

    if SHOW_PLANS:
        print_plan(iteration)
        print_trace(iteration)


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    print(f"Secret number: {SECRET}")
    print()

    llm = LLMConfig(provider="ollama", model=model)
    agent = Guesser(llm=llm)
    result = agent.seek(GOAL)

    for iteration in result.iterations:
        print_iteration(iteration)

    print(f"status:     {result.status.value}")
    print(f"iterations: {result.iteration_count}")


if __name__ == "__main__":
    main()
