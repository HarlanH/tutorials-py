# Track 5: `read_only`

Every primitive carries a `read_only` flag. It signals one thing: does this
primitive modify the agent's state or only read it? This track puts a read-only
primitive next to a mutating one so the difference is visible.

## 1. Install

```bash
uv add opensymbolicai-core
```

## 2. Two primitives, one flag apart

The agent keeps a list of notes. One primitive reads that list, the other adds
to it.

```python
# notebook.py
from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive
from opensymbolicai.llm import LLM, LLMConfig


class Notebook(PlanExecute):
    def __init__(self, llm: LLM | LLMConfig) -> None:
        super().__init__(llm=llm)
        self.notes: list[str] = []

    @primitive(read_only=True)
    def list_notes(self) -> list[str]:
        """Return every note saved so far."""
        return list(self.notes)

    @primitive()  # read_only defaults to False: saving a note changes state.
    def save_note(self, text: str) -> str:
        """Save a note and return a confirmation."""
        self.notes.append(text)
        return f"saved: {text}"
```

`list_notes` only reads, so it is marked `read_only=True`. `save_note` appends
to `self.notes`, so it keeps the default. Writing `@primitive()` with no
argument is the same as `@primitive(read_only=False)`: the default is `False`,
meaning "this may modify state."

## 3. Run it

```python
# main.py
from notebook import Notebook
from opensymbolicai.llm import LLMConfig

llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")
agent = Notebook(llm=llm)

result = agent.run(
    "save notes that say buy milk, walk the dog, and call mom, "
    "then list every note"
)
if not result.success:
    print(result.error)
else:
    print(result.result)  # ['buy milk', 'walk the dog', 'call mom']
```

```bash
uv run main.py
```

Output:

```
['buy milk', 'walk the dog', 'call mom']
```

Ollama runs locally, so **no API key is required**. Pull the model first:
`ollama pull qwen2.5-coder:7b`.

## What the flag does, and what it does not

`read_only` is a declaration of intent. Marking `list_notes` as `read_only=True`
says "calling this never changes state"; leaving `save_note` at the default says
"calling this might." That is all it does on its own. It does not stop, gate, or
prompt for anything. Both primitives ran here without ceremony, and `save_note`
changed `self.notes` exactly as written.

The flag earns its keep later: a policy that asks a human to approve state
changes keys off `read_only=False` to know which calls need sign-off. That
gating is a separate piece of machinery, covered in its own track. Here the job
is just to declare, per primitive, which calls read and which calls write.
