"""Run the ConstraintSolver agent on three word problems.

Each problem gets a fresh agent instance; Z3 solver state is per instance.

Usage:
    uv run main.py
"""

from __future__ import annotations

from dataclasses import dataclass

from ollama import check_ollama
from solver import ConstraintSolver

from opensymbolicai.llm import LLMConfig


@dataclass
class Problem:
    name: str
    task: str
    expected: list[int]  # sorted expected values; key names are chosen by the LLM


PROBLEMS = [
    Problem(
        name="Coin counting",
        task=(
            "I have 20 coins. Some are nickels (worth 5 cents each) and the rest "
            "are quarters (worth 25 cents each). The total value is 200 cents. "
            "How many nickels and how many quarters do I have?"
        ),
        expected=[5, 15],  # quarters=5, nickels=15
    ),
    Problem(
        name="Age puzzle",
        task=(
            "The sum of Alice's and Bob's ages is 40. "
            "In 4 years, Alice will be exactly twice as old as Bob. "
            "How old are Alice and Bob now?"
        ),
        expected=[12, 28],  # bob=12, alice=28
    ),
    Problem(
        name="Work hours",
        task=(
            "Alice, Bob, and Carol together work 110 hours a week. "
            "Alice works twice as many hours as Carol. "
            "Bob works 10 more hours than Carol. "
            "How many hours does each person work?"
        ),
        expected=[25, 35, 50],  # carol=25, bob=35, alice=50
    ),
]


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    for problem in PROBLEMS:
        agent = ConstraintSolver(llm=llm)
        result = agent.run(problem.task)
        print(f"[{problem.name}]")
        print(f"  task:     {problem.task}")
        if not result.success:
            print(f"  error:    {result.error}")
            print(f"  plan:\n{result.plan}")
            print(f"  (tip: check that variable names in constraints match add_var() names exactly)")
        else:
            got = sorted(result.result.values())
            ok = "PASS" if got == problem.expected else "FAIL"
            print(f"  result:   {result.result}")
            print(f"  expected: {problem.expected}  [{ok}]")
        print()


if __name__ == "__main__":
    main()
