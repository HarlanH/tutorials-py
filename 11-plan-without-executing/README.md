# Track 11: Plan without executing

`agent.run(task)` does two things back to back: it asks the model for a plan,
then runs that plan. Most of the time that is exactly what you want. Sometimes
you want to see the plan first. `agent.plan(task)` does only the first half. It
returns the plan and runs nothing.

## Install

```bash
uv add opensymbolicai-core pydantic
```

## Same agent as Track 9

The same [shopping cart](../09-read-the-trace/): `new_cart`, `add_item`, and
`cart_total`, with `Item` and `Cart` as Pydantic models. Nothing about it
changes. This track just calls it in two steps instead of one.

## Plan, look, then run

Call `plan` to get the program, print it, then call `execute` to run it.

```python
# main.py
print(QUERY)                     # PlanResult has no task field, print the query

plan_result = agent.plan(QUERY)  # PlanResult, nothing has run yet

print(plan_result.plan)          # the program, as text
print(plan_result.usage)         # tokens the planning cost
print(plan_result.time_seconds)  # seconds it took

# Review the plan here: read it, log it, gate it.

exec_result = agent.execute(plan_result.plan)  # now it runs
print(exec_result.get_value())
```

```bash
uv run main.py
```

Ollama is local, so there's no API key. Pull the model once with
`ollama pull qwen2.5-coder:7b`.

```
--- intent ---
add 2 apples at 3 dollars each, 2 loaves of bread at 2 dollars each, and 3 cartons of milk at 4 dollars each, then total it up

--- plan ---
cart = new_cart()
cart = add_item(cart, "apples", 3, 2)
cart = add_item(cart, "bread", 2, 2)
cart = add_item(cart, "milk", 4, 3)
total = cart_total(cart)
--- planning cost ---
usage: input_tokens=396 output_tokens=63
time (s): 1.4777

--- result ---
22.0
```

## What you're looking at

`agent.plan(QUERY)` returns a `PlanResult`. It holds the plan as a string in
`.plan`, the tokens the planning cost in `.usage`, and the seconds it took in
`.time_seconds`. Those last two are the same planning numbers Track 10 read off
`result.metrics`, here on their own because planning is all that happened.

And that is the thing to notice: nothing ran. A `PlanResult` has no result value
and no trace, because there is nothing to trace. No `new_cart` was called, no
cart was built, no total was computed. You are holding the program the model
wrote, as text, and it has not touched your primitives.

The cart only gets built at `agent.execute(plan_result.plan)`. That call runs the
five lines and gives back an `ExecutionResult`, whose `get_value()` is the `22.0`
you would have gotten straight from `agent.run`.

## Review before execute

The space between `plan` and `execute` is a checkpoint. The plan is just a
string sitting in a variable, so you can do anything you like with it before it
runs: print it for a human to approve, log it, compare it against the last plan,
or decide not to run it at all. The model proposed a program; you choose whether
to run it.

`execute` checks the plan too. It will only run calls to your primitives and a
small set of allowed operations, and it raises rather than run a plan that
reaches for anything else. So even an unreviewed plan cannot call out to
whatever it likes. The review step is for your judgment on top of that.

## plan and execute, or just run

`agent.run(task)` is `plan` followed by `execute` in one call, with the metrics
bundled onto the result. Reach for `run` when you are happy to plan and execute
in one step. Reach for `plan` and `execute` when you want to look at the plan,
or hold it, before it runs.
