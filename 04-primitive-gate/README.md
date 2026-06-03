# Track 4: What `@primitive` actually does

`@primitive` is a gate. It registers a method so the planner is allowed to call
it. A plain method, with no decorator, is invisible to the planner. This track
shows that gate by taking one method through the before and after.

The task is the kind of thing a language model gets wrong on its own: counting
the letters in a word. With a primitive doing the counting, the answer is exact.

## 1. Install

```bash
uv add opensymbolicai-core
```

## 2. Start with a plain method, no decorator

Here is a one-method agent. The method is ordinary Python, with no `@primitive`
on it.

```python
# counter.py
from opensymbolicai.blueprints import PlanExecute


class LetterCounter(PlanExecute):
    def count_letter(self, word: str, letter: str) -> int:
        """Count how many times `letter` appears in `word`."""
        return word.count(letter)
```

Run it against the task `"how many times does the letter r appear in
strawberry"` and it fails:

```python
from opensymbolicai.llm import LLMConfig

llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")
agent = LetterCounter(llm=llm)

result = agent.run("how many times does the letter r appear in strawberry")
print(result.success)  # False
print(result.error)    # Function '...' is not allowed. Only primitive
                       # methods and allowed builtins can be called.
```

The planner had no registered primitive to call, so the plan it wrote reached
for a function that was never registered, and execution refused it. A method the
planner cannot see is a method it cannot use.

## 3. Add the decorator

Mark the same method with `@primitive`. Nothing else changes.

```python
# counter.py
from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class LetterCounter(PlanExecute):
    @primitive(read_only=True)
    def count_letter(self, word: str, letter: str) -> int:
        """Count how many times `letter` appears in `word`."""
        return word.count(letter)
```

## 4. Run it

```python
# main.py
from counter import LetterCounter
from opensymbolicai.llm import LLMConfig

llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")
agent = LetterCounter(llm=llm)

result = agent.run("how many times does the letter r appear in strawberry")
if not result.success:
    print(result.error)
else:
    print(result.result)  # 3
```

```bash
uv run main.py
```

Output:

```
3
```

Ollama runs locally, so **no API key is required**. Pull the model first:
`ollama pull qwen2.5-coder:7b`.

## Takeaway

The planner may only call registered primitives. `@primitive` is what moves a
method from ordinary Python, which the planner never sees, to a building block
the plan can call. The type annotations are the contract the planner reads, and
the docstring is its guidance. No decorator, no call.
