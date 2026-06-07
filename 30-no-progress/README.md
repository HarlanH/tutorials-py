# Track 30: no-progress circuit breaker

`max_iterations` in `GoalSeekingConfig` stops a GoalSeeking agent that hasn't
converged. The same agent with a tight limit hits `MAX_ITERATIONS`; with enough
headroom it reaches `ACHIEVED`.

## Install

```bash
uv add opensymbolicai-core
```

## Running it

```bash
uv run main.py
```

```
Run: max_iterations=3 
    iteration 0: [501, 1000]  hint='cold — go higher'
    iteration 1: [501, 749]  hint='burning — go lower'
    iteration 2: [626, 749]  hint='warm — go higher'
  Status: MAX_ITERATIONS — circuit breaker fired after 3 iteration(s)

Run: max_iterations=15
    iteration 0: [1, 1000]  hint='no guess yet'
    iteration 1: [501, 1000]  hint='cold — go higher'
    iteration 2: [501, 749]  hint='burning — go lower'
    iteration 3: [626, 749]  hint='warm — go higher'
    iteration 4: [626, 749]  hint='warm — go higher'
    iteration 5: [688, 749]  hint='burning — go higher'
    iteration 6: [719, 749]  hint='burning — go higher'
    iteration 7: [735, 749]  hint='burning — go higher'
    iteration 8: [735, 749]  hint='correct'
  Status: ACHIEVED in 9 iteration(s)
```

## What is happening

`GoalSeekingConfig(max_iterations=N)` is the only change between the two runs:

```python
config = GoalSeekingConfig(max_iterations=3)
result = agent.seek(GOAL)

if result.status == GoalStatus.ACHIEVED:
    print(f"ACHIEVED in {result.iteration_count} iteration(s)")
else:
    print(f"MAX_ITERATIONS — circuit breaker fired after {result.iteration_count} iteration(s)")
```

Binary search on 1–1000 needs ~9 iterations to find 742. With `max_iterations=3`
the search range is still [626, 749] when the limit fires — far from the answer.
With `max_iterations=15` there is enough room and the agent converges.

`result.status` is `ACHIEVED` or `MAX_ITERATIONS`. `result.iteration_count`
tells you exactly how many iterations ran. The circuit breaker is a clean stop —
no exception, no crash.
