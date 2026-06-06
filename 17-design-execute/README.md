# Track 17: when you need DesignExecute

`PlanExecute` generates plans made of assignment statements only. It forbids
`for`, `while`, `if`, and similar constructs. When a task requires iteration,
use `DesignExecute` instead. The switch is one line.

## Install

```bash
uv add opensymbolicai-core
```

## The task requires a loop

The task is: sum the squares of all integers from 1 to 100. The answer is
338,350. There is no way to write a plan for this without a loop: no model
will write 100 inline `square()` calls. `PlanExecute` rejects any plan that
contains `for` or `while`:

```
PlanExecute rejects the plan: For statements are not allowed in plans
```

`DesignExecute` allows it.

## The only change is the base class

```python
# before
class Accumulator(PlanExecute):
    ...

# after
class Accumulator(DesignExecute):
    ...
```

The three primitives (`square`, `add`, `format_result`) are unchanged. The
task string is unchanged. The `LLMConfig` is unchanged.

## Running it

```bash
uv run main.py
```

```
--- plan ---
total = 0
for i in range(1, 101):
    square_value = square(i)
    total = add(total, square_value)

result_line = format_result("Sum of squares from 1 to 100", total)
return result_line

--- result ---
Sum of squares from 1 to 100: 338350
(201 primitive calls)

PlanExecute rejects the plan: For statements are not allowed in plans
```

The loop runs 100 times, each iteration calling `square` and `add`: 200 calls,
plus one `format_result` at the end, for 201 total. `PlanExecute` rejects the
plan at validation time, before a single primitive runs.

## What DesignExecute permits

`DesignExecute` allows `for`, `while`, `if/elif/else`, `try/except`, and
`raise` in LLM-generated plans. Everything else that `PlanExecute` blocks
remains blocked: no imports, no function definitions, no `exec` or `eval`.

Loop safety is enforced by injecting iteration counters into the plan's AST
before execution. Each loop gets a counter; if it exceeds `max_loop_iterations`
(default 100), execution stops with an error.

## Out of scope

The loop guard and its config knob (`max_loop_iterations`) are Track 18. The
other two `DesignExecute` config knobs (`max_total_primitive_calls`,
`allow_break_continue`) are Track 19.
