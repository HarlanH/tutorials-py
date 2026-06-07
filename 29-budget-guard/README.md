# Track 29: budget guard

A `BudgetedRunner` wraps any agent and tracks cumulative token usage across
a batch of tasks. Before each task it checks whether enough tokens remain
to make a planning call. If not, it raises `BudgetExceeded` and the batch stops.

## Install

```bash
uv add opensymbolicai-core
```

## Running it

```bash
uv run main.py
```

```
Budget: 1300 tokens

  ✓  What is 7 + 3?
     result=10  cumulative tokens used=442  tokens remaining=858

  ✓  What is 12 * 15 - 47?
     result=133  cumulative tokens used=902  tokens remaining=398

  ✓  What is 8 factorial?
     result=40320  cumulative tokens used=1336  tokens remaining=0

  ✗  What is the 10th Fibonacci number?
     BudgetExceeded: 0 tokens remaining — need at least 200 to plan

  Stopping — 2 task(s) skipped.
```

## What is happening

`BudgetedRunner` is a thin wrapper — no framework changes needed:

```python
class BudgetedRunner:
    def run(self, task: str) -> OrchestrationResult:
        if self.tokens_remaining < MIN_PLANNING_TOKENS:
            raise BudgetExceeded(...)
        result = self._agent.run(task)
        self._used += result.metrics.plan_tokens.total_tokens
        return result
```

The guard fires before the task runs, so a blocked task costs zero tokens.
The third task runs even though it pushes the total over the budget — the guard
only checks what has been spent so far, not what a task will spend. Once
`remaining` hits zero, nothing more runs.

`MIN_PLANNING_TOKENS` is a floor: any task needs at least that many tokens to
produce a plan. Set it to a value below your typical input token count (~420
here) to avoid starting a task that is almost certain to fail mid-plan.
