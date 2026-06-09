"""A symbolic calculus agent backed by SymPy.

The LLM picks which operation to apply (differentiate, integrate, simplify) and
SymPy returns an exact symbolic answer. The LLM handles the language; SymPy
handles the math.

Rule for the plan: always pass the full expression string and the exact
variable name to differentiate/integrate. Never pass a variable name like 'v'
or 'a' — always use the symbol that appears in the expression (e.g. 't', 'x', 'r').
"""

from __future__ import annotations

import sympy

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class CalculusAgent(PlanExecute):
    """Performs symbolic calculus using SymPy."""

    @primitive(read_only=True)
    def differentiate(self, expr: str, variable: str) -> str:
        """Differentiate expr with respect to variable and return the result as a string.

        Example: differentiate("x**3 + 2*x**2 - 5", "x") -> "3*x**2 + 4*x"
        """
        x = sympy.Symbol(variable)
        result = sympy.diff(sympy.sympify(expr), x)
        return str(result)

    @primitive(read_only=True)
    def integrate(self, expr: str, variable: str) -> str:
        """Integrate expr with respect to variable and return the result as a string.

        Example: integrate("3*x**2 + 4*x", "x") -> "x**3 + 2*x**2"
        """
        x = sympy.Symbol(variable)
        result = sympy.integrate(sympy.sympify(expr), x)
        return str(result)

    @primitive(read_only=True)
    def simplify(self, expr: str) -> str:
        """Simplify expr and return the result as a string.

        Example: simplify("sin(x)**2 + cos(x)**2") -> "1"
        """
        result = sympy.simplify(sympy.sympify(expr))
        return str(result)

    # ------------------------------------------------------------------
    # Decompositions: show the exact plan patterns the LLM should follow.
    # ------------------------------------------------------------------

    @decomposition(
        intent="A car's position is s = 3*t**2 + 10*t meters. What is its velocity (ds/dt)?",
        expanded_intent=(
            "Velocity is the derivative of position with respect to time t. "
            "Pass the position expression and variable 't' to differentiate. "
            "Always use the symbol that appears in the expression, not the output variable name."
        ),
    )
    def _example_polynomial(self):
        result = self.differentiate("3*t**2 + 10*t", "t")
        return result

    @decomposition(
        intent="A wave's displacement is y = 5*sin(3*x). What is dy/dx?",
        expanded_intent=(
            "Differentiate the trigonometric expression with respect to the symbol x. "
            "The chain rule applies: d/dx sin(3*x) = 3*cos(3*x), so the result is 15*cos(3*x). "
            "Pass the full expression string and the variable name 'x' to differentiate."
        ),
    )
    def _example_trig(self):
        result = self.differentiate("5*sin(3*x)", "x")
        return result

    @decomposition(
        intent="A force F = 2*r newtons acts over distance r. Find the work done (integrate F dr).",
        expanded_intent=(
            "Work is the integral of force over distance. "
            "Pass the force expression and variable 'r' to integrate. "
            "Use integrate, not differentiate, when the task asks for accumulation or antiderivative."
        ),
    )
    def _example_integrate(self):
        result = self.integrate("2*r", "r")
        return result
