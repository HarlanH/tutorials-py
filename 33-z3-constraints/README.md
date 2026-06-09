# Track 33: Constraint satisfaction with Z3

Some problems can't be expressed as a single equation. They are constraint
satisfaction problems: find values that satisfy a set of conditions
simultaneously. Z3 is an SMT solver built for this.

The task is the classic farmer puzzle:

> A farmer has chickens and rabbits. There are 20 heads and 56 legs.
> How many of each?

The LLM translates the problem into integer constraints. Z3 finds the assignment.

## 1. Install

```bash
uv add opensymbolicai-core z3-solver
```

## 2. The agent

Three primitives: declare a variable, add a constraint, solve.

```python
# solver.py
import z3
from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class ConstraintSolver(PlanExecute):

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
        """Find integer values satisfying all constraints.

        Returns a dict mapping each variable name to its value.
        Raises ValueError if no solution exists.
        """
        if self._solver.check() != z3.sat:
            raise ValueError("No solution exists for the given constraints.")
        model = self._solver.model()
        return {name: model[var].as_long() for name, var in self._vars.items()}
```

Every primitive returns a value so every plan statement is an assignment,
which PlanExecute requires.

## 3. Run it

```bash
uv run main.py
```

`main.py` runs three problems, each with a fresh agent instance.

### Coin counting

```
Task: 20 coins totalling 200 cents — nickels and quarters?
Result: {'nickels': 15, 'quarters': 5}
```

### Age puzzle

```
Task: ages sum to 40; in 4 years Alice is twice Bob's age. Ages now?
Result: {'alice_age': 28, 'bob_age': 12}
```

### Work hours

```
Task: 110 hours total; Alice works 2× Carol; Bob works Carol + 10. Hours each?
Result: {'alice': 50, 'bob': 35, 'carol': 25}
```

The plan for the farmer puzzle looks roughly like this:

```python
c = add_var("chickens")
r = add_var("rabbits")
c1 = add_constraint("chickens + rabbits == 20")
c2 = add_constraint("2*chickens + 4*rabbits == 56")
result = solve()
```

## What just happened

The LLM did not solve any of these puzzles. It read each sentence and wrote
down the constraints. Z3 searched for integer values that satisfy all of them.

## Takeaway

Z3 finds values that satisfy a set of conditions simultaneously. Give it
constraints and it either produces a satisfying assignment or tells you none
exists.
