# Track 1: Hello, OpenSymbolicAI

The five-minute first win: a working agent that plans and executes a small
arithmetic task. Two files: [`calculator.py`](calculator.py) (the agent) and
[`main.py`](main.py) (runs it).

## 1. Install Ollama

Download the Mac app from [ollama.com](https://ollama.com/download/mac) and open
it. The `curl | sudo sh` installer requires permission to write to `/Applications`,
which may be blocked on managed Macs. If you have Homebrew: `brew install ollama`.

Models are stored in `~/.ollama/models/`. To free space when you're done:

```bash
ollama rm qwen2.5-coder:7b
```

Pull the model before running:

```bash
ollama pull qwen2.5-coder:7b
```

## 2. Install the package

OpenSymbolicAI is published to PyPI as `opensymbolicai-core` (the import name is
`opensymbolicai`). Requires Python 3.12+.

```bash
uv add opensymbolicai-core
```

## 3. Write a three-primitive agent

A **primitive** is the core building block: a typed, documented method the
planner is allowed to call. The base class `PlanExecute` turns a task into a
plan and executes it.

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

The type annotations are the LLM's contract, and the docstrings are its
guidance.

## 4. Run it

```python
# main.py
from calculator import Calculator
from opensymbolicai.llm import LLMConfig

llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")
agent = Calculator(llm=llm)

result = agent.run("what is 7 times 8 minus 3")
print(result.result)  # 53
```

```bash
uv run main.py
```

Ollama runs locally, so **no API key is required**.

The `result` object has five attributes: `result` (the final value), `success`
(bool), `error` (string if it failed), `plan` (the generated code), and `trace`
(the execution log). In a debugger, use `result.result` or `print(result.plan)`
rather than inspecting the raw object.

## What just happened

The LLM didn't do the arithmetic. It wrote a **plan**, a small program like
`result = subtract(multiply(7, 8), 3)`, and your primitives ran it in plain
Python.

`.run()` is inherited from `PlanExecute` (the base class in
`opensymbolicai.blueprints`). The library source is in the `opensymbolicai-core`
package installed by uv; you can browse it with `python -c "import opensymbolicai; print(opensymbolicai.__file__)"`.

## Limits

The agent can only solve what its primitives cover. Try:

```python
result = agent.run("what number multiplied by 7 gives 56")
print(result.success, result.result)
```

The plan needs division, but `Calculator` has no `divide` primitive. Depending on
the model, it may fail with an error, return `None`, or occasionally guess the
answer directly. Add a `divide` primitive and it reliably works.
