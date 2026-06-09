"""Run the CalculusAgent on four physics-themed problems.

Each shows a different facet of calculus: differentiation of polynomial,
constant, trigonometric, and symbolic expressions. The answers are exact
symbolic results, not floating-point approximations.

Usage:
    uv run main.py
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy

from calculus import CalculusAgent
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig


@dataclass
class Problem:
    name: str
    context: str   # one sentence a anyone can appreciate
    task: str
    expected: str  # expected SymPy expression


PROBLEMS = [
    Problem(
        name="Projectile velocity",
        context="Throw a ball upward and its height follows a parabola. Differentiate to find speed.",
        task=(
            "A ball is thrown upward. Its height in meters is h = -5*t**2 + 20*t + 2 "
            "where t is time in seconds. What is the velocity v(t) = dh/dt?"
        ),
        expected="-10*t + 20",
    ),
    Problem(
        name="Projectile acceleration",
        context="Differentiate velocity to recover the acceleration due to gravity.",
        task=(
            "A ball's velocity as a function of time t is the expression -10*t + 20 m/s. "
            "Differentiate this expression with respect to t to find the acceleration. "
            "The answer should equal the gravitational acceleration near Earth's surface."
        ),
        expected="-10",
    ),
    Problem(
        name="Pendulum velocity",
        context="A pendulum swings back and forth. Its position is a cosine wave; its velocity is a sine wave.",
        task=(
            "A pendulum's horizontal position is x = 3*cos(2*t) meters. "
            "What is its velocity v(t) = dx/dt?"
        ),
        expected="-6*sin(2*t)",
    ),
    Problem(
        name="Gravity: force to potential",
        context=(
            "Newton's inverse square gravity law integrated gives the 1/r potential — "
            "the same shape that governs orbits."
        ),
        task=(
            "Use the integrate primitive on the expression G*M/r**2 with variable r. "
            "This computes the antiderivative of Newton's gravitational force with respect "
            "to distance r, which gives the gravitational potential energy shape."
        ),
        expected="-G*M/r",
    ),
]


def check(result_str: str, expected_str: str) -> bool:
    """Return True if result and expected are mathematically equal."""
    try:
        diff = sympy.simplify(sympy.sympify(result_str) - sympy.sympify(expected_str))
        return diff == 0
    except Exception:
        return result_str.strip() == expected_str.strip()


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)
    agent = CalculusAgent(llm=llm)

    for problem in PROBLEMS:
        print(f"[{problem.name}]")
        print(f"  {problem.context}")
        result = agent.run(problem.task)
        if not result.success:
            print(f"  error:    {result.error}")
            print(f"  plan:\n{result.plan}")
        else:
            ok = "PASS" if check(str(result.result), problem.expected) else "FAIL"
            print(f"  result:   {result.result}")
            print(f"  expected: {problem.expected}  [{ok}]")
        print()


if __name__ == "__main__":
    main()
