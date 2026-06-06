"""Show why DesignExecute is needed when a plan must loop.

PlanExecute forbids for/while. Its validate_plan raises ValueError the moment
the LLM writes one. DesignExecute permits loops.

The task asks for the sum of the squares of all integers from 1 to 100. No
model will write 100 inline square() calls. The plan must loop, so PlanExecute
cannot run it. This script runs the task on DesignExecute and then proves the
generated plan is rejected by PlanExecute.

Usage:
    uv run main.py
"""

from __future__ import annotations

from accumulator import Accumulator
from ollama import check_ollama

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive
from opensymbolicai.llm import LLMConfig

TASK = "What is the sum of the squares of all integers from 1 to 100?"


class _AccumulatorPE(PlanExecute):
    """Same primitives on PlanExecute, used only to prove validation fails."""

    @primitive(read_only=True)
    def square(self, n: int) -> int:
        return n * n

    @primitive(read_only=True)
    def add(self, a: int, b: int) -> int:
        return a + b

    @primitive(read_only=True)
    def format_result(self, label: str, value: int) -> str:
        return f"{label}: {value}"


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    # Run on DesignExecute.
    agent = Accumulator(llm=llm)
    result = agent.run(TASK)

    print("--- plan ---")
    print(result.plan)
    print()

    if result.success:
        print("--- result ---")
        print(result.result)
        steps = result.trace.steps
        print(f"({len(steps)} primitive calls)")
    else:
        print("--- error ---")
        print(result.error)
    print()

    # Prove the plan is rejected by PlanExecute.
    pe = _AccumulatorPE(llm=llm)
    try:
        pe.validate_plan(result.plan)
        print("PlanExecute: plan passed (no loop written)")
    except ValueError as e:
        print(f"PlanExecute rejects the plan: {e}")


if __name__ == "__main__":
    main()
