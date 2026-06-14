# Track 40: Voice date agent

Speak a date question out loud, hear the answer spoken back.

The agent transcribes your voice with Whisper, reasons about the calendar
with a GoalSeeking loop, and reads the result aloud with the macOS `say`
command (or pyttsx3 on other platforms).

No hardcoded offsets. No special-cased logic. Each question is a goal the
agent pursues across one or more iterations until it produces a spoken answer.

## The scenario

Four questions asked by voice (or `--demo` mode):

> "What day is next Tuesday?"
> "When is the last Sunday of next month?"
> "How many days until Christmas?"
> "What date is two weeks from today?"

## 1. Install

```bash
uv add opensymbolicai-core faster-whisper pyttsx3 sounddevice soundfile numpy
```

```bash
ollama pull qwen2.5-coder:7b
```

## 2. The agent

Seven primitives:

```python
class DateAgent(GoalSeeking):

    @primitive(read_only=True)
    def current_date(self) -> str:
        """Return today's date as YYYY-MM-DD."""

    @primitive(read_only=True)
    def add_time(self, date_str: str, amount: int, unit: str) -> str:
        """Add time to a date. unit: 'day', 'week', 'month', or 'year'."""

    @primitive(read_only=True)
    def weekday_of(self, date_str: str) -> str:
        """Return the weekday name for a YYYY-MM-DD date."""

    @primitive(read_only=True)
    def end_of_month(self, date_str: str) -> str:
        """Return the last day of the month for a given date."""

    @primitive(read_only=True)
    def last_weekday_of_month(self, date_str: str, weekday: str) -> str:
        """Return the last occurrence of a weekday in the month of date_str."""

    @primitive(read_only=True)
    def days_between(self, from_date: str, to_date: str) -> int:
        """Return the number of days between two YYYY-MM-DD dates."""

    @primitive(read_only=True)
    def format_response(self, question: str, result: str) -> str:
        """Use an LLM to produce a natural spoken sentence from a date or count."""
```

GoalSeeking wraps these primitives in an iterate-until-done loop. Each
iteration the agent writes a plan, executes it, and checks whether the
result is a complete spoken answer. If not, it tries again with the
knowledge accumulated so far.

### Goal context

```python
class DateContext(GoalContext):
    today: str = ""   # pre-populated: "2026-06-13 (Friday)"
    answer: str = ""  # set once the agent produces a spoken sentence
```

`today` is set when the goal starts, so the agent never needs to fetch the
current date as a separate iteration step. `answer` is set when a spoken
sentence (not a raw date or number) comes back from a plan. The evaluator
marks the goal achieved as soon as `answer` is non-empty.

## 3. Run it

Demo mode (no microphone required):

```bash
uv run main.py --demo
```

Live mic input:

```bash
uv run main.py
```

Press Enter to record, speak your question, and wait for the reply.

## Sample output

```
Voice Date Agent
========================================

Question: What day is next Tuesday?
  Iteration 1: result = add_time('2026-06-13', 4, 'day')
               return format_response('What day is next Tuesday?', result)
Answer:   Next Tuesday will be June 17th.

Question: When is the last Sunday of next month?
  Iteration 1: result = last_weekday_of_month('2026-07-01', 'Sunday')
               return format_response('When is the last Sunday of next month?', result)
Answer:   The last Sunday of next month will be July 26th, 2026.

Question: How many days until Christmas?
  Iteration 1: d = days_between('2026-06-13', '2026-12-25')
               return d
  Iteration 2: days_until_christmas = days_between(current_date(), '2026-12-25')
               return format_response('How many days until Christmas?', str(days_until_christmas))
Answer:   Christmas is in 195 days!

Question: What date is two weeks from today?
  Iteration 1: result = add_time('2026-06-13', 2, 'week')
               return format_response('What date is two weeks from today?', result)
Answer:   Two weeks from today is June 27th, 2026.
```

## What just happened

The agent pursues each question as a goal. An iteration that returns a raw
date like `"2026-07-26"` does not satisfy the evaluator, so the loop
continues. An iteration that calls `format_response` produces a spoken
sentence, which satisfies the evaluator and ends the loop.

`last_weekday_of_month` lets the agent answer "last Sunday of next month"
cleanly in one step: add one month to get a date in July, then call the
primitive to find July's last Sunday. Without that primitive, the model
would have to walk backward day-by-day — which it reliably gets wrong.

## Takeaway

GoalSeeking fits date questions because the agent does not know the right
answer before it calls the primitives. With PlanExecute the LLM writes the
full plan up front; any date it hardcodes in the plan may be wrong. With
GoalSeeking each iteration sees what the previous one produced, so the LLM
can call `current_date()` first and compute offsets from that real value
in the next step.

The tradeoff: more iterations mean more LLM calls and more latency. Design
your primitives to be expressive enough that most questions finish in one or
two iterations.
