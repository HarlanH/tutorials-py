# Track 13: Analyze a plan's structure

Track 12 ran a plan you already had. Before you run one, you might want to know
what it would do. `agent.analyze_plan(plan)` tells you. It parses the plan and
reports every primitive call in it: the method name, whether that method is
read-only, and the arguments. Nothing runs, and the model is not called. It is
pure inspection of the plan text.

The question it answers: which mutating primitives does this plan touch?

## Install

```bash
uv add opensymbolicai-core
```

## A bank account, with reads and writes

A bank account is a good example for this, because it has a real read/write
split. `deposit` and `withdraw` change the balance, so they are declared
`read_only=False`. `can_afford` only looks, so it is `read_only=True`. Those
flags are the same signal from Track 5, set by whoever wrote the primitive.

```python
# account.py
from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Account(PlanExecute):
    @primitive(read_only=False)
    def deposit(self, balance: float, amount: float) -> float:
        """Add money to the balance."""
        return balance + amount

    @primitive(read_only=False)
    def withdraw(self, balance: float, amount: float) -> float:
        """Take money out of the balance."""
        return balance - amount

    @primitive(read_only=True)
    def can_afford(self, balance: float, price: float) -> bool:
        """Check whether the balance covers a price."""
        return balance >= price
```

## Analyze two plans

Write two plans by hand, one that only checks the balance and one that changes
it, and analyze each.

```python
# main.py
analysis = agent.analyze_plan(plan)  # PlanAnalysis, nothing runs

for call in analysis.calls:          # each is a PrimitiveCall
    flag = "read-only" if call.read_only else "mutating"
    print(f"{call.method_name}: {flag}  args={call.args}")

print("has_mutations:", analysis.has_mutations)
mutating = [c.method_name for c in analysis.calls if not c.read_only]
print("mutating primitives:", mutating)
```

```bash
uv run main.py
```

```
--- read-only plan ---
ok = can_afford(100, 30)
big = can_afford(100, 250)
  can_afford: read-only  args={'arg0': 100, 'arg1': 30}
  can_afford: read-only  args={'arg0': 100, 'arg1': 250}
has_mutations: False
mutating primitives: []

--- plan that moves money ---
balance = deposit(100, 50)
balance = withdraw(balance, 30)
ok = can_afford(balance, 200)
  deposit: mutating  args={'arg0': 100, 'arg1': 50}
  withdraw: mutating  args={'arg0': 'balance', 'arg1': 30}
  can_afford: read-only  args={'arg0': 'balance', 'arg1': 200}
has_mutations: True
mutating primitives: ['deposit', 'withdraw']
```

## What you're looking at

`analyze_plan` returns a `PlanAnalysis`. Its `.calls` are the primitive calls in
order, each a `PrimitiveCall` with a `method_name`, the `read_only` flag for that
method, and the `args` it was given. Two convenience properties sit on top:
`has_mutations` is true when any call is not read-only, and `method_names` is
just the names in order.

The two plans tell the story. The first only calls `can_afford`, a read-only
method, twice. `has_mutations` is `False`: this plan looks at the balance and
changes nothing. The second calls `deposit` and `withdraw` before checking, so
`has_mutations` is `True` and the mutating primitives are right there:
`['deposit', 'withdraw']`. You learned the plan moves money without moving any.

One detail in `args`: the analysis reads the plan as text, so it has not resolved
any variables. Literals come through as values (`100`, `50`), but a reference to
an earlier result comes through as its name, the string `'balance'`. That is
enough to see the shape of each call.

## Why look before running

`has_mutations` and the list of non-read-only calls are a gate you can put in
front of `execute`. Run a read-only plan and the worst it can do is read.
A plan that touches `deposit` or `withdraw` is one you might want a person to
sign off on first. Track 12 showed `execute` blocking plans that reach past your
primitives; this is a softer check on top: not "is this plan allowed to run" but
"what kind of plan is this," answered before a single line runs.
