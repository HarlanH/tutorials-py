# Track 28: token accounting

Every `agent.run()` returns `result.metrics.plan_tokens` — a `TokenUsage`
with `input_tokens`, `output_tokens`, and `total_tokens`. Six tasks run
from simple to complex to show how token counts change.

## Install

```bash
uv add opensymbolicai-core
```

## Running it

```bash
uv run main.py
```

```
Provider : ollama
Model    : qwen2.5-coder:7b

Task                                                Result   In tokens  Out tokens  Total tokens
------------------------------------------------------------------------------------------------
What is 7 + 3?                                          10         421          19           440
What is 12 * 15 - 47?                                  133         427          28           455
What is 8 factorial?                                 40320         419          15           434
What is the 10th Fibonacci number?                      34         423         138           561
What is 6 factorial plus the 8th Fibonacci nu…         741         426          45           471
What is (factorial of 5) divided by (fibonacc…        27.0         437          61           498

Totals                                                            2553         306          2859
```

## What is happening

`plan_tokens` only covers the planning call — the one LLM call that writes
the plan. Executing the plan (calling the primitives) is pure Python; it
uses no tokens.

```python
result = agent.run(task)
t = result.metrics.plan_tokens
print(t.input_tokens, t.output_tokens, t.total_tokens)
```

**Input tokens** are nearly constant across all six tasks (~420). The input
is the system prompt plus the list of primitives — it barely changes no
matter how hard the task is.

**Output tokens** are the tokens in the plan the LLM wrote. A one-liner
(`return add(7, 3)`) costs 19. A multi-step plan costs more.
