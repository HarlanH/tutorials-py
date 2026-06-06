# Track 18: the loop guard and max_loop_iterations

Every loop in a `DesignExecute` plan has a built-in iteration limit.
If the loop runs more times than `max_loop_iterations` allows, execution
stops and the step is recorded as failed. The default limit is 100.

## Install

```bash
uv add opensymbolicai-core
```

## Demonstrating the limit

The sum-of-squares plan from Track 17 loops exactly 100 times. Running it
with `max_loop_iterations=50` trips on iteration 51. Running it with
`max_loop_iterations=100` clears all 100 iterations and returns 338,350.

```bash
uv run main.py
```

```
--- limit too small (max_loop_iterations=50) ---
error: Loop exceeded maximum iterations (50)

--- limit sufficient (max_loop_iterations=100) ---
result: Sum of squares 1 to 100: 338350
primitive calls: 201
```

201 calls: one `square` and one `add` per iteration, plus one `format_result`
at the end.

## Setting the limit

```python
from opensymbolicai.models import DesignExecuteConfig

config = DesignExecuteConfig(max_loop_iterations=200)
agent = Accumulator(llm=llm, config=config)
```

Pick a number that fits the largest range your tasks will ever iterate.
The default of 100 works for most cases.

## Out of scope

The total number of primitive calls across the whole plan is a separate knob:
`max_total_primitive_calls`. That is Track 19.
