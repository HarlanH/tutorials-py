# Track 20: conditional logic end to end

No new API. This track combines a loop and an `if/elif/else` in one plan,
then reads the trace to see which branch fired.

The cart applies a tiered discount: 15% over $100, 10% over $50, nothing
otherwise. Three tasks exercise one tier each.

## Install

```bash
uv add opensymbolicai-core
```

## Running it

```bash
uv run main.py
```

## No discount

Subtotal $26.94, below both thresholds. The trace shows `apply_discount` was
called with `pct=0`: the `else` branch ran.

```
result: Total: $26.94 (no discount)
```

## 10% tier

Add 5 books. Subtotal $91.89, clears $50. The trace shows `pct=10`.

```
result: Subtotal: $91.89. Discount: 10%. Total: $82.70
```

## 15% tier

Add 2 keyboards. Subtotal $249.89, clears $100. The trace shows `pct=15`.

```
result: Subtotal: $249.89. Discount: 15%. Total: $212.41
```

## Reading the branch from the trace

The conditional lives in the plan. The trace records only primitive calls.
To see which branch ran, look at the arguments passed to `apply_discount` in
`result.trace.steps`.
