# Track 10: Read the metrics

Track 8 read `result.plan`, the code the LLM wrote. Track 9 read `result.trace`,
that code running. This track reads `result.metrics`: what the run cost. The
numbers split cleanly in two. Planning, the one LLM call that wrote the plan,
took almost all of the time and all of the tokens. Executing the plan, your
primitives running in plain Python, took almost no time and no tokens at all.

## Install

```bash
uv add opensymbolicai-core pydantic
```

## Same agent as Track 9

The same [shopping cart](../09-read-the-trace/): `new_cart`, `add_item`, and
`cart_total`, with `Item` and `Cart` as Pydantic models. Nothing about it
changes. This track just asks a different question of the result it returns.

## Read the metrics

Run the cart, then read the fields off `result.metrics`.

```python
# main.py
m = result.metrics  # ExecutionMetrics

print("provider:", m.provider)
print("model:", m.model)
print("steps executed:", m.steps_executed)
print("plan tokens:", m.plan_tokens)  # a TokenUsage object
print("  input:", m.plan_tokens.input_tokens)
print("  output:", m.plan_tokens.output_tokens)
print("  total:", m.plan_tokens.total_tokens)
print("plan time (s):", round(m.plan_time_seconds, 4))
print("execute time (s):", round(m.execute_time_seconds, 4))
print("total time (s):", round(m.total_time_seconds, 4))
```

```bash
uv run main.py
```

Ollama is local, so there's no API key. Pull the model once with
`ollama pull qwen2.5-coder:7b`.

```
--- intent ---
add 2 apples at 3 dollars each, 2 loaves of bread at 2 dollars each, and 3 cartons of milk at 4 dollars each, then total it up

--- metrics ---
provider: ollama
model: qwen2.5-coder:7b
steps executed: 5
plan tokens: input_tokens=396 output_tokens=63
  input: 396
  output: 63
  total: 459
plan time (s): 1.5179
execute time (s): 0.0047
total time (s): 1.5226
```

The times are rounded to four decimal places. These exact numbers will not be
yours. Token counts and timings depend on the model, the provider, the machine
the model runs on, its current load, and the wording of the task; they move from
run to run even with everything else held fixed. Read them for shape and
proportion, not as fixed values.

## What you're looking at

Look at the two times. `plan_time_seconds` is 1.5179, `execute_time_seconds` is
0.0047. The model spent about a second and a half writing the plan. Running that
plan took under five thousandths of a second. Planning was about 99.7% of the
wall clock; your five primitive calls were the rounding error. `total_time_seconds`
is just the two added together.

That gap is the whole idea of the library in one statistic. Thinking is slow and
happens once, up front, in the LLM. Doing is fast and happens in your process,
in plain Python you wrote and tested.

## A first look at TokenUsage

`plan_tokens` is not a number, it's a `TokenUsage` object with `input_tokens`,
`output_tokens`, and a `total_tokens` property. The input tokens (396) are the
prompt the model read: your primitive signatures and the task. The output tokens
(63) are the plan it wrote back, the same `result.plan` you printed in Track 8,
measured in tokens.

Notice the field is called `plan_tokens`, not `total_tokens`. Planning is the
only thing that spends tokens. Executing the plan cost zero, because nothing
went back to the model: the cart was built and totalled in your process, not in
a prompt. There is no `execute_tokens`, because it would always be zero.

## provider, model, steps

The last three are the run's label. `provider` and `model` record what answered,
`ollama` and `qwen2.5-coder:7b` here, which is worth having when the same agent
can run on different models. `steps_executed` is 5, the same five steps you
walked in the trace.

## What else is on the result

That is the last field this module opens. The `OrchestrationResult` carries the
outcome (`result.success`, `result.result`, `result.error`), the plan, the
trace, and these metrics. You have now read all of them.
