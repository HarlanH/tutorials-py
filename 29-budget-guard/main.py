"""Token-budget guard — stop a batch of tasks before the budget runs out.

BudgetedRunner wraps any agent. Before each task it checks whether enough
tokens remain to make a planning call. If not, it raises BudgetExceeded and
no further tasks run.

Usage:
    uv run main.py
"""

from __future__ import annotations

from calc import Calc
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig
from opensymbolicai.models import OrchestrationResult

TASKS = [
    "What is 7 + 3?",
    "What is 12 * 15 - 47?",
    "What is 8 factorial?",
    "What is the 10th Fibonacci number?",
    "What is 6 factorial plus the 8th Fibonacci number?",
    "What is (factorial of 5) divided by (fibonacci of 6), then add 12?",
]

BUDGET = 1000
MIN_PLANNING_TOKENS = 200


class BudgetExceeded(Exception):
    pass


class BudgetedRunner:
    """Runs tasks against an agent until the token budget is exhausted."""

    def __init__(self, agent: Calc, budget: int) -> None:
        self._agent = agent
        self._budget = budget
        self._used = 0

    @property
    def tokens_used(self) -> int:
        return self._used

    @property
    def tokens_remaining(self) -> int:
        return max(0, self._budget - self._used)

    def run(self, task: str) -> OrchestrationResult:
        if self.tokens_remaining < MIN_PLANNING_TOKENS:
            raise BudgetExceeded(
                f"{self.tokens_remaining} tokens remaining — "
                f"need at least {MIN_PLANNING_TOKENS} to plan"
            )
        result = self._agent.run(task)
        self._used += result.metrics.plan_tokens.total_tokens
        return result


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)
    runner = BudgetedRunner(Calc(llm=llm), budget=BUDGET)

    print(f"Budget: {BUDGET} tokens\n")

    for task in TASKS:
        try:
            result = runner.run(task)
            print(f"  ✓  {task}")
            print(f"     result={result.result}  cumulative tokens used={runner.tokens_used}  tokens remaining={runner.tokens_remaining}")
        except BudgetExceeded as e:
            print(f"  ✗  {task}")
            print(f"     BudgetExceeded: {e}")
            print(f"\n  Stopping — {len(TASKS) - TASKS.index(task) - 1} task(s) skipped.")
            break
        print()


if __name__ == "__main__":
    main()
