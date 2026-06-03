# Track 12: Execute a plan you already have

Track 11 ran a plan the model wrote. But `agent.execute(plan)` does not care
where the plan came from. A plan is just text, and `execute` will run any plan
text you hand it: one you wrote by hand, one loaded from a file, one a teammate
edited. The model is never called. And before it runs a single line, `execute`
validates the plan.

## Install

```bash
uv add opensymbolicai-core pydantic
```

## Same agent as Track 9

The same [shopping cart](../09-read-the-trace/): `new_cart`, `add_item`, and
`cart_total`, with `Item` and `Cart` as Pydantic models. The track keeps the
Ollama preflight the other native tracks use, but `execute` never calls the
model, so nothing here actually needs Ollama running.

## Run a plan you wrote

Write the plan as a plain string and pass it to `execute`.

```python
# main.py
PLAN = """cart = new_cart()
cart = add_item(cart, "pens", 5, 3)
cart = add_item(cart, "notebook", 8, 1)
total = cart_total(cart)"""

result = agent.execute(PLAN)  # ExecutionResult
print(result.get_value())     # 23.0
```

```bash
uv run main.py
```

```
--- plan ---
cart = new_cart()
cart = add_item(cart, "pens", 5, 3)
cart = add_item(cart, "notebook", 8, 1)
total = cart_total(cart)
--- result ---
23.0
```

No model wrote that plan and no model ran it. You wrote four lines of Python,
`execute` ran them against your primitives, and `result.get_value()` is the
`23.0` they produced: 3 pens at 5 plus 1 notebook at 8. The `ExecutionResult` you
get back is the same kind of object from Track 9, trace and all.

## execute validates first

Running arbitrary text sounds risky, so `execute` checks the plan before it runs
it. The rule is narrow: a plan may only be assignment statements that call your
primitives, plus a few safe builtins. Anything else raises a `ValueError` and
nothing runs. Here are four plans `execute` refuses:

```python
BAD_PLANS = {
    "imports a module": 'x = __import__("os")',
    "opens a file": 'x = open("/etc/passwd")',
    "runs a loop": "for i in range(3):\n    x = i",
    "reaches a dunder": "x = cart_total.__globals__",
}

for label, bad in BAD_PLANS.items():
    try:
        agent.execute(bad)
    except ValueError as e:
        print(f"{label}: {e}")
```

```
--- rejected plans ---
imports a module: Calling '__import__' is not allowed
opens a file: Calling 'open' is not allowed
runs a loop: For statements are not allowed in plans
reaches a dunder: Accessing private/dunder attributes not allowed: __globals__
```

No imports, no file access, no loops, no private or dunder attributes, and no
calls to anything that is not one of your primitives. A plan that tries any of
those never reaches your code. (This is the same check `agent.run` and
`agent.execute` from Track 11 ran for you under the hood; here you can see it
fire.)

## Plan, review, run

This is what makes a plan worth holding as data. It can come from anywhere: the
model, a file, a queue, a person. You read it, edit it, or store it, and run it
later with `execute`. Whatever review you put in front, the validation is the
backstop underneath: an approved-looking plan still cannot reach past your
primitives. The plan is a proposal; `execute` is where you decide to run it, and
it only runs the parts you allowed.
