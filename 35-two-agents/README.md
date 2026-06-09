# Track 35: Two agents, one problem

Some problems have parts that belong to different domains. This track uses two
specialist agents — one that knows what words mean, one that knows how to
calculate — and a master that routes between them.

The task:

> I drove 300km at 60kph. What do km and kph mean, and how long did the trip take?

## 1. Install

```bash
uv add opensymbolicai-core
```

## 2. The agents

### AbbreviationAgent

One primitive: `expand_all(text) -> str`. It replaces every known abbreviation
in the text with its full written form.

```python
class AbbreviationAgent(PlanExecute):

    @primitive(read_only=True)
    def expand_all(self, text: str) -> str:
        """Replace every known abbreviation in text with its full written form.

        Example: expand_all("300km at 60kph") -> "300 kilometers at 60 kilometers per hour"
        """
```

### CalculatorAgent

Four primitives: `add`, `subtract`, `multiply`, `divide`. Nothing else.

```python
class CalculatorAgent(PlanExecute):

    @primitive(read_only=True)
    def divide(self, a: float, b: float) -> float:
        """Divide a by b. Example: divide(300, 60) -> 5.0"""
        return a / b
```

### MasterAgent

Holds both specialists and exposes three primitives:

```python
class MasterAgent(PlanExecute):

    def __init__(self, llm, verbose=False, **kwargs):
        super().__init__(llm=llm, **kwargs)
        self._abbrev = AbbreviationAgent(llm=llm)
        self._calc   = CalculatorAgent(llm=llm)

    @primitive(read_only=True)
    def expand_problem(self, text: str) -> str:
        """Send the full problem text to AbbreviationAgent for expansion."""

    @primitive(read_only=True)
    def ask_calculator(self, expression: str) -> float:
        """Ask CalculatorAgent to evaluate an arithmetic expression."""

    @primitive(read_only=True)
    def report(self, expanded_problem: str, answer: float, answer_label: str) -> str:
        """Combine the expanded text and numeric result into a final answer."""
```

## 3. Run it

```bash
uv run main.py
```

The plan the master writes for the road trip problem:

```python
expanded = expand_problem("I drove 300km at 60kph. What do km and kph mean, and how long did the trip take?")
time     = ask_calculator("300 / 60")
result   = report(expanded_problem=expanded, answer=time, answer_label="hours")
```

Output:

```
I drove 300 kilometers at 60 kilometers per hour. Answer: 5.00 hours.
```

## 4. See the plans

Set `SHOW_PLANS = True` in `main.py` to print every agent's plan as it runs —
the master's plan plus the plan each specialist wrote internally:

```
[AbbreviationAgent plan]
result = expand_all("I drove 300km at 60kph ...")

[CalculatorAgent plan]
result = divide(300, 60)

[MasterAgent plan]
expanded = expand_problem("I drove 300km at 60kph ...")
time     = ask_calculator("300 / 60")
result   = report(expanded_problem=expanded, answer=time, answer_label="hours")
```

## What just happened

The master's LLM read the question and split it into two jobs. It sent the
full problem text to AbbreviationAgent, which rewrote every abbreviation in
place. It sent the arithmetic to CalculatorAgent, which picked the right
operation. The master assembled both results into one answer.

Each specialist saw only its slice. AbbreviationAgent never saw any numbers.
CalculatorAgent never saw any words.

## Takeaway

Agents can be small and single-purpose. When a primitive delegates to another
`PlanExecute` instance, that agent writes its own plan for its own slice of the
problem. You can see every agent's reasoning separately by setting `SHOW_PLANS = True`.
