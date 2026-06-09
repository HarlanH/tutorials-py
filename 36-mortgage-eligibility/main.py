"""Run MortgageChecker on four applicant scenarios.

Usage:
    uv run main.py
"""

from __future__ import annotations

from dataclasses import dataclass

from checker import MortgageChecker
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig


@dataclass
class Problem:
    name: str
    task: str
    expected_approved: bool
    expected_contains: list[str]  # strings that must appear in the result


PROBLEMS = [
    Problem(
        name="Alex — qualified applicant",
        task=(
            "Age 35, credit score 720, annual income $85,000, monthly debt $1,500, "
            "loan amount $280,000. Is Alex eligible for a mortgage?"
        ),
        expected_approved=True,
        expected_contains=["Approved"],
    ),
    Problem(
        name="Jordan — low credit score",
        task=(
            "Age 28, credit score 580, annual income $60,000, monthly debt $800, "
            "loan amount $200,000. Is Jordan eligible for a mortgage?"
        ),
        expected_approved=False,
        expected_contains=["Denied", "credit score"],
    ),
    Problem(
        name="Casey — high debt and large loan",
        task=(
            "Age 42, credit score 680, annual income $55,000, monthly debt $2,200, "
            "loan amount $320,000. Is Casey eligible for a mortgage?"
        ),
        expected_approved=False,
        expected_contains=["Denied", "debt-to-income", "loan-to-income"],
    ),
    Problem(
        name="Casey — minimum income to qualify",
        task=(
            "Casey has monthly debt of $2,200 and wants a $320,000 loan. "
            "What is the minimum annual income Casey needs to qualify?"
        ),
        expected_approved=True,  # expects a valid income figure, not a denial
        expected_contains=["71,111"],
    ),
]


def check_result(result_str: str, problem: Problem) -> str:
    has_verdict = "Approved" in result_str or "Denied" in result_str
    if has_verdict:
        approved = "Approved" in result_str and "Denied" not in result_str
        status_ok = approved if problem.expected_approved else not approved
    else:
        status_ok = True  # numeric result (e.g. minimum_income) — no verdict expected
    contains_ok = all(term in result_str for term in problem.expected_contains)
    if status_ok and contains_ok:
        return "PASS"
    parts = []
    if not status_ok:
        parts.append("approval status wrong")
    if not contains_ok:
        missing = [t for t in problem.expected_contains if t not in result_str]
        parts.append(f"missing: {missing}")
    return f"FAIL ({', '.join(parts)})"


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    for problem in PROBLEMS:
        agent = MortgageChecker(llm=llm)
        result = agent.run(problem.task)

        print(f"[{problem.name}]")
        if not result.success:
            print(f"  error: {result.error}")
            print(f"  plan:\n{result.plan}")
        else:
            verdict = check_result(str(result.result), problem)
            print(f"  result: {result.result}")
            if verdict != "PASS":
                print(f"  plan:\n{result.plan}")
            print(f"  [{verdict}]")
        print()


if __name__ == "__main__":
    main()
