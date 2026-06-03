# Track 1: Hello, OpenSymbolicAI

The five-minute first win: a working agent that plans and executes a small
arithmetic task. Two files: [`calculator.py`](calculator.py) (the agent) and
[`main.py`](main.py) (runs it).

## 1. Install

OpenSymbolicAI is published to PyPI as `opensymbolicai-core` (the import name is
`opensymbolicai`). Requires Python 3.12+.

```bash
uv add opensymbolicai-core
```

## 2. Write a three-primitive agent

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

## 3. Run it

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

Ollama runs locally, so **no API key is required**. Pull the model first:
`ollama pull qwen2.5-coder:7b`.

## What just happened

The LLM didn't do the arithmetic. It wrote a **plan**, a small program like
`result = subtract(multiply(7, 8), 3)`, and your primitives ran it in plain
Python.
