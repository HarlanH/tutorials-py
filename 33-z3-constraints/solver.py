"""A constraint-satisfaction agent backed by Z3.

Every primitive returns a value so the plan assigns every call — PlanExecute
requires every statement to be an assignment. The Z3 state lives in the agent
instance; the plan references variables by name.
"""

from __future__ import annotations

import z3

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class ConstraintSolver(PlanExecute):
    """Solves integer constraint problems using Z3."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._solver = z3.Solver()
        self._vars: dict[str, z3.ArithRef] = {}

    @primitive(read_only=True)
    def add_var(self, name: str) -> str:
        """Declare an integer variable and return its name.

        Example: c = add_var("chickens")
        """
        self._vars[name] = z3.Int(name)
        return name

    @primitive(read_only=True)
    def add_constraint(self, expr: str) -> str:
        """Add a constraint using declared variable names and return the expression.

        Example: c1 = add_constraint("chickens + rabbits == 20")
        Example: c2 = add_constraint("2*chickens + 4*rabbits == 56")
        """
        self._solver.add(eval(expr, {}, self._vars))
        return expr

    @primitive(read_only=True)
    def solve(self) -> dict[str, int]:
        """Find integer values satisfying all constraints and return them.

        Returns a dict mapping each variable name to its value.
        Raises ValueError if no solution exists.
        """
        if self._solver.check() != z3.sat:
            raise ValueError("No solution exists for the given constraints.")
        model = self._solver.model()
        return {name: model[var].as_long() for name, var in self._vars.items()}

    # ------------------------------------------------------------------
    # Decomposition: shows the exact plan pattern the LLM should follow.
    # ------------------------------------------------------------------

    @decomposition(
        intent="A farmer has 20 heads and 56 legs (chickens and rabbits). How many of each?",
        expanded_intent=(
            "Declare one integer variable per unknown using add_var. "
            "Translate each sentence into a constraint: heads gives a sum, legs gives a weighted sum. "
            "Every add_var and add_constraint call must be assigned to a variable. "
            "Call solve() last and return its result directly — no if statements."
        ),
    )
    def _example_farmer(self):
        c = self.add_var("chickens")
        r = self.add_var("rabbits")
        c1 = self.add_constraint("chickens + rabbits == 20")
        c2 = self.add_constraint("2*chickens + 4*rabbits == 56")
        result = self.solve()
        return result

    @decomposition(
        intent="30 coins: dimes (10c) and quarters (25c), total 480 cents. How many of each?",
        expanded_intent=(
            "Declare one variable per denomination using its full name (e.g. 'dimes', 'quarters'). "
            "Use the same full name in constraint expressions — never abbreviate. "
            "One constraint for total count, one for total value in the same unit (cents)."
        ),
    )
    def _example_coins(self):
        d = self.add_var("dimes")
        q = self.add_var("quarters")
        c1 = self.add_constraint("dimes + quarters == 30")
        c2 = self.add_constraint("10*dimes + 25*quarters == 480")
        result = self.solve()
        return result

    @decomposition(
        intent="Alice, Bob, and Carol share 90 tasks. Alice does twice as many as Carol. Bob does Carol plus 6. How many each?",
        expanded_intent=(
            "Declare one variable per person using their full lowercase name: 'alice', 'bob', 'carol'. "
            "Write a total constraint summing all three, then each ratio or offset as its own constraint. "
            "Use the exact same name in every constraint expression as was passed to add_var. "
            "Never shorten 'alice' to 'a', 'bob' to 'b', or 'carol' to 'c'."
        ),
    )
    def _example_three_vars(self):
        a = self.add_var("alice")
        b = self.add_var("bob")
        c = self.add_var("carol")
        c1 = self.add_constraint("alice + bob + carol == 90")
        c2 = self.add_constraint("alice == 2*carol")
        c3 = self.add_constraint("bob == carol + 6")
        result = self.solve()
        return result
