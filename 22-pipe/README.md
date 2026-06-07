# Track 22: pipe

A large intermediate list passes from one primitive to another as a Python variable. The list never appears in any prompt — not when it is produced, not when it is consumed.

## Install

```bash
uv add opensymbolicai-core
```

## Running it

```bash
uv run main.py
```

```
============================================================
Task: What is the mean monthly return?

  n=    100  Result ->  0.010329
  pipe:  monthly_returns() produced 100 floats
         passed as a variable into the aggregator
         100 floats in Python namespace, 0 in any LLM prompt
  plan:
    returns = monthly_returns()
    mean_return = mean_of(values=returns)
    return mean_return

  n=100,000  Result ->  0.00809
  pipe:  monthly_returns() produced 100,000 floats
         passed as a variable into the aggregator
         100,000 floats in Python namespace, 0 in any LLM prompt
  plan:
    mean_monthly_return = mean_of(monthly_returns())
    return mean_monthly_return


============================================================
Task: What fraction of months had a positive return?

  n=    100  Result ->  0.63
  pipe:  monthly_returns() produced 100 floats
         passed as a variable into the aggregator
         100 floats in Python namespace, 0 in any LLM prompt
  plan:
    positive_count = count_positive(monthly_returns())
    total_months = len_of(monthly_returns())
    fraction_with_positive_return = divide(positive_count, total_months)
    return fraction_with_positive_return

  n=100,000  Result ->  0.58112
  pipe:  monthly_returns() produced 100,000 floats
         passed as a variable into the aggregator
         100,000 floats in Python namespace, 0 in any LLM prompt
  plan:
    positive_count = count_positive(monthly_returns())
    total_months = len_of(monthly_returns())
    fraction_positive = divide(positive_count, total_months)
    return fraction_positive


============================================================
Task: What is the range between the best and worst monthly return?

  n=    100  Result ->  0.198228
  pipe:  monthly_returns() produced 100 floats
         passed as a variable into the aggregator
         100 floats in Python namespace, 0 in any LLM prompt
  plan:
    best_return = max_of(monthly_returns())
    worst_return = min_of(monthly_returns())
    range_between_best_and_worst = subtract(a=best_return, b=worst_return)
    return range_between_best_and_worst

  n=100,000  Result ->  0.376076
  pipe:  monthly_returns() produced 100,000 floats
         passed as a variable into the aggregator
         100,000 floats in Python namespace, 0 in any LLM prompt
  plan:
    max_return = max_of(monthly_returns())
    min_return = min_of(monthly_returns())
    range_return = subtract(max_return, min_return)
    return range_return
```

## What is happening

OSAI generates a plan once, then executes it in pure Python. The list of
100,000 floats lives in the plan's namespace and is passed by variable name.
The LLM never sees the data — only the two lines of code it wrote.

In a tool-calling loop (ReAct), every intermediate value is a message. The
list travels through the context window twice: once as the tool output, and
again as the argument to the next call.

```
OSAI — data as a Python variable
──────────────────────────────────────────────────
  monthly_returns()
        │
        │  100,000 floats
        │  (Python namespace — invisible to LLM)
        ▼
  mean_of(values=returns)  ──►  result
──────────────────────────────────────────────────
  OSAI LLM sees: 2 lines of code, 0 floats


Tool-calling loop — data through the context window
──────────────────────────────────────────────────
  monthly_returns()
        │
        ▼
  ┌─────────────────────────────────────────────┐
  │  context: [0.023, -0.041, 0.012, 0.008,     │
  │            -0.019, 0.034, 0.007, -0.052,    │  ← 100,000 floats
  │            0.015, 0.041, ...                │
  │            ... (100,000 entries total) ]    │
  └─────────────────────────────────────────────┘
        │
        │  LLM copies all 100,000 floats into the next call
        ▼
  mean_of(values=[0.023, -0.041, 0.012, ...])   ← 100,000 floats again
──────────────────────────────────────────────────
  LLM sees: 100,000 floats × 2
```

The plan is identical whether `n` is 100 or 100,000. Only the data size
changes — and that data never crosses the LLM boundary either way.
