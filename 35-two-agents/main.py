"""Run the MasterAgent on three problems that each need abbreviations and arithmetic.

Usage:
    uv run main.py
"""

from __future__ import annotations

from dataclasses import dataclass

from master import MasterAgent
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig


@dataclass
class Problem:
    name: str
    task: str
    expected_terms: list[str]   # words that must appear in the result
    expected_answer: float      # numeric answer, checked as "X.XX"


PROBLEMS = [
    Problem(
        name="Road trip",
        task="I drove 300km at 60kph. What do km and kph mean, and how long did the trip take?",
        expected_terms=["kilometers", "kilometers per hour"],
        expected_answer=5.0,
    ),
    Problem(
        name="Grocery shopping",
        task="I bought 2.5kg of apples at $3.20/kg. What does kg mean and what is the total cost?",
        expected_terms=["kilograms"],
        expected_answer=8.0,
    ),
    Problem(
        name="Water bottle",
        task="My bottle has 1200mL of water. I drank 500mL. What does mL mean and how much is left?",
        expected_terms=["milliliters"],
        expected_answer=700.0,
    ),
]


def check_result(result_str: str, problem: Problem) -> str:
    terms_ok = all(term in result_str for term in problem.expected_terms)
    answer_ok = f"{problem.expected_answer:.2f}" in result_str
    if terms_ok and answer_ok:
        return "PASS"
    parts = []
    if not terms_ok:
        missing = [t for t in problem.expected_terms if t not in result_str]
        parts.append(f"missing terms: {missing}")
    if not answer_ok:
        parts.append(f"answer {problem.expected_answer:.2f} not found")
    return f"FAIL ({', '.join(parts)})"


SHOW_PLANS = False  # set to True to print the master's plan for every problem


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    for problem in PROBLEMS:
        agent = MasterAgent(llm=llm, verbose=SHOW_PLANS)
        result = agent.run(problem.task)

        print(f"[{problem.name}]")
        print(f"  task:   {problem.task}")
        if not result.success:
            print(f"  error:  {result.error}")
            print(f"  plan:\n{result.plan}")
        else:
            verdict = check_result(str(result.result), problem)
            print(f"  result: {result.result}")
            if SHOW_PLANS or verdict != "PASS":
                print(f"  plan:\n{result.plan}")
            print(f"  [{verdict}]")
        print()


if __name__ == "__main__":
    main()
