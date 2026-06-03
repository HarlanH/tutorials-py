# Track 6: `deterministic`

Every primitive also carries a `deterministic` flag. It signals one thing: is
this primitive a pure function, the same inputs always giving the same output?
This track puts a pure primitive next to one that reads the clock.

## 1. Install

```bash
uv add opensymbolicai-core
```

## 2. Two primitives, one flag apart

The agent finds the next Monday. One primitive computes it from a given date,
the other reads today's date off the system clock.

```python
# dates.py
from datetime import date, timedelta

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Calendar(PlanExecute):
    @primitive(read_only=True, deterministic=False)  # depends on the clock
    def today(self) -> date:
        """Return today's date."""
        return date.today()

    @primitive(read_only=True)  # deterministic defaults to True: a pure function
    def next_monday(self, d: date) -> date:
        """Return the date of the first Monday after `d`."""
        days_ahead = (0 - d.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return d + timedelta(days=days_ahead)
```

`next_monday` is pure: hand it `2026-06-02` and it always returns `2026-06-08`,
today or next year. So it keeps the default, `deterministic=True`. `today` is
not pure: it returns a different date depending on when it runs, because it
reads state outside its arguments. That is what `deterministic=False` declares.

Both primitives are also marked `read_only=True`, the flag from the previous
track: neither one changes the agent's state. The two flags are independent, and
the new one here is `deterministic`.

## 3. Run it

```python
# main.py
from dates import Calendar
from opensymbolicai.llm import LLMConfig

llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")
agent = Calendar(llm=llm)

result = agent.run("calculate the date of the next Monday from the current date")
if not result.success:
    print(result.error)
else:
    print(result.result)
```

```bash
uv run main.py
```

Run on Tuesday 2026-06-02, the output is:

```
2026-06-08
```

Run it next week and the answer changes, because `today` reads a new date.
`next_monday` did not change at all. That split, one primitive whose output
moves with the clock and one whose output never does, is exactly what the
`deterministic` flag records.

Ollama runs locally, so **no API key is required**. Pull the model first:
`ollama pull qwen2.5-coder:7b`.

## Why the flag matters, and what it does not do

On its own, `deterministic` changes nothing about this run. Both primitives
executed for real, and the plan produced a date. The flag is metadata: the
agent records it per primitive and folds it into its signature, but the normal
execution path never branches on it.

It earns its keep in tooling that can lean on purity. The property that defines
a deterministic primitive, same inputs always giving the same output, means its
result can be cached: compute `next_monday(2026-06-02)` once and every later call
with that date can reuse the stored `2026-06-08` instead of recomputing. `today`
cannot be cached that way, since its correct answer changes from day to day, so
the flag is also what keeps it out of such a cache.

Validation and replay tooling rests on the same property. To check that an agent
still behaves correctly, such tooling re-runs captured plans against their
recorded traces. A pure primitive like `next_monday` can be safely re-run: same
date in, same date out, so the comparison holds. Calling `today` again is
different. A trace captured last week recorded last week's date; re-running
`today` now returns a new date, and the plan's output would no longer match what
was recorded. Marking it `deterministic=False` tells the tooling not to call it
live during replay, and to reuse the captured result instead.

The clearest case for `deterministic=False` is a primitive that calls an LLM or
an external API, where the same call rarely returns the same bytes twice.
`today` stands in for that here. Writing such a primitive is its own topic; the
point for now is the declaration: pure, or not.
