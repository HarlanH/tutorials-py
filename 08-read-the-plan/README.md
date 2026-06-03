# Track 8: Read the generated plan

Track 1 printed `result.result`, showed `53`, and stopped there. But `53` is
just the last line of the story. `run` hands back an `OrchestrationResult`, and
the most interesting thing on it is `result.plan`: the actual code the model
wrote to answer you. Let's read it.

## Install

```bash
uv add opensymbolicai-core
```

## Same agent as Track 1

Nothing here changes. It's the same three-primitive calculator, copied across as
is:

```python
# calculator.py
from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Calculator(PlanExecute):
    @primitive(read_only=True)
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    @primitive(read_only=True)
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b

    @primitive(read_only=True)
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b
```

## Print the plan

This time you ask a handful of different questions, and for each one print three
things: what you asked (`result.task`), the plan the model wrote, and the answer
your primitives came back with.

```python
# main.py
from calculator import Calculator
from opensymbolicai.llm import LLMConfig

QUERIES = [
    "what is 7 times 8 minus 3",
    "subtract 5 from 100",
    "multiply 6 by 4, add 2, then subtract 5",
    "I have 3 boxes of 12 apples and eat 5, how many are left",
]

agent = Calculator(llm=LLMConfig(provider="ollama", model="qwen2.5-coder:7b"))

for query in QUERIES:
    result = agent.run(query)
    print(result.task)    # what you asked
    print(result.plan)    # the code the model wrote
    print(result.result)  # what your primitives computed
```

```bash
uv run main.py
```

Ollama is local, so there's no API key. Pull the model once with
`ollama pull qwen2.5-coder:7b`.

```
--- intent ---
what is 7 times 8 minus 3
--- plan ---
step1 = multiply(7, 8)
result = subtract(step1, 3)
--- result ---
53

--- intent ---
subtract 5 from 100
--- plan ---
result = subtract(100, 5)
--- result ---
95

--- intent ---
multiply 6 by 4, add 2, then subtract 5
--- plan ---
result = multiply(6, 4)
result = add(result, 2)
result = subtract(result, 5)
--- result ---
21

--- intent ---
I have 3 boxes of 12 apples and eat 5, how many are left
--- plan ---
total_apples = multiply(3, 12)
apples_left = subtract(total_apples, 5)
--- result ---
31
```

## What you're looking at

Four questions, four plans, all built from the same three primitives.

The first took two steps: multiply 7 and 8, then subtract 3 from that. The
second collapsed to one call, and notice the model put `100` first, because you
asked to subtract *from* it. The third chained three calls, feeding each answer
into the next. The apples question is my favorite: the model read `3` and `12`
straight out of the sentence, gave them names, and worked from there. A plan is
just Python, so it can do any of that.

Run it again and the plans shift a little. That first one might come back as a
single nested line; the variable names change every time. Doesn't matter. What
holds steady is which primitives get called, and in what order.

## The part that matters

The model never multiplied anything. It never worked out `56`, and it never
worked out `53`. It wrote the calls and stopped. Your `multiply` returned `56`,
your `subtract` returned `53`, both in plain Python, right here in your process.

And this is the whole point: those numbers never went back to the model. `56`
traveled from `multiply` into `subtract` through a Python variable, not through
another prompt. You ask the model once, for the plan. After that the running is
yours. A model that's shaky at multiplying big numbers never gets asked to. It
only picks which of your primitives to call, and in what order. Your code, the
code you've tested, does the actual work.

## What else is on the result

`plan` is one field. The same `OrchestrationResult` also tells you whether the
run worked (`result.success`), what went wrong if it didn't (`result.error`), a
step-by-step trace of the run, and metrics like token counts and timing. This
track stays on `result.plan`.
