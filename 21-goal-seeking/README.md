# Track 21: your first @evaluator and seek()

`GoalSeeking` runs a plan-execute-evaluate loop. Instead of `run()`, you call
`seek(goal)`. After each execution, a method marked `@evaluator` decides
whether the goal is achieved. If not, the loop continues.

## Install

```bash
uv add opensymbolicai-core
```

## The task

The agent must find a secret number between 1 and 1000. After each guess it
receives a temperature hint and a direction — `"cold — go higher"`,
`"burning — go lower"`, etc. The context tracks the current search range
(`low`, `high`). Each iteration the agent picks the midpoint, guesses it, and
the evaluator checks if the hint is `"correct"`.

## Running it

```bash
uv run main.py
```

```
Secret number: 742

iteration  1: guess= 500  hint=cold — go higher
    n = midpoint(1, 1000)
    result = guess(n)
    return result

    [ok  ] midpoint(low=1, high=1000)                ->  500
    [ok  ] guess(n=500)                              -> 'cold — go higher'

iteration  2: guess= 750  hint=burning — go lower
    ...

iteration  7: guess= 742  hint=correct               ✓

status:     achieved
iterations: 7
```

Set `SHOW_PLANS = False` in `main.py` for the compact view.

## The three new pieces

**`@evaluator`** marks the method that decides if the goal is done. It receives
the goal string and the context, and returns a `GoalEvaluation`:

```python
@evaluator
def _check(self, goal: str, context: HintContext) -> GoalEvaluation:
    return GoalEvaluation(goal_achieved=context.last_hint == "correct")
```

**`seek(goal)`** runs the loop and returns a `GoalSeekingResult` with the
final status, iteration count, and every iteration's plan and trace.

**`GoalStatus`** tells you how the loop ended — `achieved` when the evaluator
returned `True`, `max_iterations` if it hit the limit (default 10).

## Context and update_context

`HintContext` is a `GoalContext` subclass with three fields: `low`, `high`, and
`last_hint`. `update_context` is called after each execution — it reads the
hint from the trace and narrows the range:

```python
def update_context(self, context: HintContext, execution_result: ExecutionResult) -> None:
    for step in execution_result.trace.steps:
        if step.primitive_called == "guess" and step.success:
            ...
            if "go higher" in hint:
                context.low = max(context.low, n + 1)
            elif "go lower" in hint:
                context.high = min(context.high, n - 1)
```

The planner sees `low` and `high` in its prompt each iteration and substitutes
them as literal integers into `midpoint(low, high)`. This is the only place
where raw execution results are read — the evaluator and planner never touch
`ExecutionResult` directly.

## Out of scope

Track 22 covers `GoalContext` and `update_context` in depth. Track 23 covers
LLM-generated evaluators. Track 24 covers `max_iterations`, all four
`GoalStatus` values, and lifecycle hooks.
