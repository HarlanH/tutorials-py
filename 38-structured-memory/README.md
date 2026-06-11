# Track 38: Structured memory

An agent that remembers facts across sessions by writing them to a JSON
file. The next time it runs, it reads that file before responding.

No vector database. No embeddings. Just a file.

## The scenario

Five sessions with the same agent:

> Session 1: "My name is Sam and I work mainly in Go."
> Session 2: "I also prefer light mode and use VS Code."
> Session 3: "What do you know about me?"
> Session 4: "What editor do I use?"
> Session 5: "What coffee brand do I drink?"

Sessions 1 and 2 write to `memory.json`. Sessions 3–5 read from it.
Session 5 asks about something that was never stored.

## 1. Install

```bash
uv add opensymbolicai-core
```

```bash
ollama pull qwen2.5-coder:7b
```

## 2. The agent

Six primitives:

```python
class MemoryAgent(PlanExecute):

    @primitive(read_only=True)
    def load_memory(self) -> str:
        """Read all stored facts from memory.json.

        Example: load_memory() -> "name: Sam\\neditor: VS Code"
        """

    @primitive(read_only=False)
    def save_fact(self, key: str, value: str) -> str:
        """Save a single fact to memory.json, overwriting if the key exists.

        Example: save_fact("name", "Sam") -> "Saved: name = Sam"
        """

    @primitive(read_only=True)
    def load_keys(self) -> str:
        """Return all stored keys as a comma-separated string.

        Example: load_keys() -> "name, editor, language"
        """

    @primitive(read_only=True)
    def select_relevant_keys(self, question: str, available_keys: str) -> str:
        """Use an LLM to pick which keys are relevant to a question.

        Example: select_relevant_keys("What editor?", "name, editor") -> "editor"
        """

    @primitive(read_only=True)
    def get_facts_for_keys(self, keys: str) -> str:
        """Fetch values for a comma-separated list of keys.

        Example: get_facts_for_keys("editor") -> "editor: VS Code"
        Returns "No results found." if none of the keys exist.
        """

    @primitive(read_only=True)
    def respond(self, message: str) -> str:
        """Return the message as the final response."""
```

For broad recall ("what do you know about me?"), the plan calls `load_memory`
and passes everything to `respond`. For specific questions, the plan calls
`load_keys`, lets `select_relevant_keys` pick which ones matter, fetches their
values with `get_facts_for_keys`, and responds. If nothing matches, the agent
responds with "No results found."

## 3. Run it

```bash
uv run main.py
```

## Sample output

```
Session 1
User: My name is Sam and I work mainly in Go.

Plan:
  r1 = save_fact('name', 'Sam')
  r2 = save_fact('primary_language', 'Go')
  return respond("Got it! I've saved your name and primary programming language.")

Agent: Got it! I've saved your name and primary programming language.

memory.json after this session:
  name: Sam
  primary_language: Go

Session 2
User: I also prefer light mode and use VS Code.

Plan:
  r1 = save_fact('light_mode_preference', 'on')
  r2 = save_fact('editor', 'VS Code')
  return respond("Got it! I've saved your preference for light mode and editor.")

Agent: Got it! I've saved your preference for light mode and editor.

memory.json after this session:
  name: Sam
  primary_language: Go
  light_mode_preference: on
  editor: VS Code

Session 3
User: What do you know about me?

Plan:
  memory = load_memory()
  return respond(memory)

Agent: name: Sam
primary_language: Go
light_mode_preference: on
editor: VS Code

Session 4
User: What editor do I use?

Plan:
  keys = load_keys()
  relevant = select_relevant_keys('What editor do I use?', keys)
  values = get_facts_for_keys(relevant)
  return respond(values)

Agent: editor: VS Code

Session 5
User: What coffee brand do I drink?

Plan:
  keys = load_keys()
  relevant = select_relevant_keys('What coffee brand do I drink?', keys)
  values = get_facts_for_keys(relevant)
  return respond(values)

Agent: No results found.
```

## What just happened

Each session creates a fresh `MemoryAgent` instance. There is no state
in memory between instantiations. The persistence comes entirely from
the file on disk.

For session 4, `select_relevant_keys` uses an LLM internally to match
"What editor do I use?" against the stored keys and returns `editor`.
For session 5, no stored key relates to coffee, so `get_facts_for_keys`
returns "No results found."

## Takeaway

Structured memory works best when the information has a natural key-value
shape: name, preference, setting. Each fact overwrites the previous value
for that key, so the file stays compact. If the same user says "actually I
switched to Rust", a new `save_fact("language", "Rust")` replaces the old
value cleanly.

The tradeoff: facts that don't fit a key are hard to store. For free-form
notes, see Track 39.
