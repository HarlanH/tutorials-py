# Track 19: max_total_primitive_calls and allow_break_continue

Track 18 covered `max_loop_iterations`. This track covers the other two
`DesignExecute` config knobs.

## Install

```bash
uv add opensymbolicai-core
```

## max_total_primitive_calls

A cap on the total number of primitive calls across the entire plan, no matter
how they arise. The default is 1000.

```bash
uv run main.py
```

```
=== max_total_primitive_calls ===
limit=3, calls made before stop: 4
error: Exceeded maximum total primitive calls (3). Plan may contain too many iterations.

limit=15, calls made: 11
result: Total: $56.88
```

```python
config = DesignExecuteConfig(max_total_primitive_calls=200)
agent = Cart(llm=llm, config=config)
```

## allow_break_continue

Controls whether `break` and `continue` are allowed in plans. When `False`,
the plan is rejected at validation time before any primitive runs.

```
=== allow_break_continue ===
allow_break_continue=True, calls made: 5
result: Total: $11.97

allow_break_continue=False: Break statements are not allowed in plans
```

```python
config = DesignExecuteConfig(allow_break_continue=False)
```

## Out of scope

Track 18 covers `max_loop_iterations`.
