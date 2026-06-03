# Track 7: Type annotations are the contract

The planner never sees your method bodies. It sees their signatures, and those
signatures are built straight from your type annotations. The types you write on
each parameter and return are the contract the LLM plans against. This track
makes that contract visible by printing the plan the LLM generates.

## 1. Install

```bash
uv add opensymbolicai-core
```

## 2. Two typed primitives

```python
# textkit.py
from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class TextKit(PlanExecute):
    @primitive(read_only=True)
    def repeat(self, text: str, times: int) -> str:
        """Repeat text the given number of times."""
        return text * times

    @primitive(read_only=True)
    def shout(self, text: str) -> str:
        """Return text uppercased with an exclamation mark."""
        return text.upper() + "!"
```

The agent turns those annotations into the signatures it shows the model:

```
repeat(text: str, times: int) -> str
    """Repeat text the given number of times."""
shout(text: str) -> str
    """Return text uppercased with an exclamation mark."""
```

That is all the planner knows about `repeat`: its name, that `text` is a string
and `times` is an integer, that it returns a string, and its docstring. The body
`text * times` stays on your side.

## 3. Run it and read the plan

```python
# main.py
from textkit import TextKit
from opensymbolicai.llm import LLMConfig

llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")
agent = TextKit(llm=llm)

result = agent.run("repeat the word go 3 times, then shout the result")
print(result.plan)
if not result.success:
    print(result.error)
else:
    print(result.result)
```

```bash
uv run main.py
```

Output:

```
go_repeated = repeat(text="go", times=3)
result = shout(text=go_repeated)
GOGOGO!
```

Read the plan. The model passed `text="go"` as a quoted string and `times=3` as
a bare integer, because that is what the signature said each one was. The string
return of `repeat` then flows into `shout`, whose parameter is also a string.
The types lined up, so the plan runs. (The model chooses the intermediate
variable names, so those differ from run to run; the calls do not.)

Ollama runs locally, so **no API key is required**. Pull the model first:
`ollama pull qwen2.5-coder:7b`.

## 4. Change one type, change the plan

Annotate `times` as `str` instead of `int`. The body does not change.

```diff
-    def repeat(self, text: str, times: int) -> str:
+    def repeat(self, text: str, times: str) -> str:
```

Now the signature tells the model `times` is a string, so it plans accordingly:

```
go_thrice = repeat(text="go", times="3")
result = shout(text=go_thrice)
can't multiply sequence by non-int of type 'str'
```

The model wrote `times="3"`, a string, and `text * "3"` is not valid Python, so
the plan fails. One annotation flipped `3` into `"3"` and broke the result. The
same goes for `int` versus `float`: declare a parameter `float` and the model
writes `2.0` where `int` would have given `2`. The type is not a hint the model
may ignore; it is the shape of the call it writes.

## 5. Drop the annotations: everything becomes `Any`

Remove the annotations entirely.

```python
    @primitive(read_only=True)
    def repeat(self, text, times):
        """Repeat text the given number of times."""
        return text * times
```

A missing annotation does not mean "anything is fine." It renders as `Any`:

```
repeat(text: Any, times: Any) -> Any
```

Now the signature says nothing about what `text` and `times` are. The model has
to guess. It might pass `times=3` and succeed, or `times="3"` and fail, and
which one you get depends on the model and the wording of the task, not on a
contract you wrote. `Any` is worse than a wrong type: a wrong type fails loudly
and predictably, while `Any` removes the guardrail and leaves the plan to a
guess. The fix is the same one this track started with: annotate every parameter
and return, and let the types carry the contract.
