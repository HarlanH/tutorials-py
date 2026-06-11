# Track 39: Unstructured memory

An agent that keeps a running diary of session notes. Each session appends
one line to `diary.txt`. When the user asks what was discussed, the agent
reads the file and answers from it.

No schema. No keys. Just text.

## The scenario

Three sessions with the same agent:

> Session 1: "I'm debugging a memory leak in my Flask app. Narrowed it to the connection pool."
> Session 2: "Fixed the pool issue by setting pool_recycle=1800. Now testing the API endpoints."
> Session 3: "Where did I leave off on my Flask project?"

Sessions 1 and 2 append a line to `diary.txt`. Session 3 reads it all.

## 1. Install

```bash
uv add opensymbolicai-core
```

```bash
ollama pull qwen2.5-coder:7b
```

## 2. The agent

Three primitives:

```python
class DiaryAgent(PlanExecute):

    @primitive(read_only=True)
    def read_diary(self) -> str:
        """Read all past session notes from diary.txt.

        Example: read_diary() -> "Debugging a memory leak in Flask app."
        """

    @primitive()
    def append_diary(self, entry: str) -> str:
        """Append one line to diary.txt.

        Example: append_diary("Fixed Flask pool with pool_recycle=1800.") -> "Logged."
        """

    @primitive(read_only=True)
    def respond(self, message: str) -> str:
        """Return the message as the final response."""
```

When the user shares an update, the LLM writes a plan that calls
`append_diary` with a one-sentence summary. When the user asks where they
left off, the diary contents are passed into the task so the LLM can
answer directly.

## 3. Run it

```bash
uv run main.py
```

## Sample output

```
Session 1
User: I'm debugging a memory leak in my Flask app. Narrowed it to the connection pool.

Plan:
  r = append_diary("Debugging a memory leak in Flask app; narrowed to the connection pool.")
  result = respond("Noted. I've logged that you're debugging a Flask memory leak.")

Agent: Noted. I've logged that you're debugging a Flask memory leak.

diary.txt after this session:
  Debugging a memory leak in Flask app; narrowed to the connection pool.

Session 2
User: Fixed the pool issue by setting pool_recycle=1800. Now testing the API endpoints.

Plan:
  r = append_diary("Fixed Flask connection pool with pool_recycle=1800; now testing API endpoints.")
  result = respond("Logged. Good progress on the Flask project!")

Agent: Logged. Good progress on the Flask project!

diary.txt after this session:
  Debugging a memory leak in Flask app; narrowed to the connection pool.
  Fixed Flask connection pool with pool_recycle=1800; now testing API endpoints.

Session 3
User: Where did I leave off on my Flask project?

Plan:
  result = respond("Based on your diary:\n- ...")

Agent: Based on your diary:
  - You were debugging a memory leak traced to the connection pool.
  - You fixed it with pool_recycle=1800 and moved on to testing the API endpoints.
```

## What just happened

Sessions 1 and 2 each create a fresh `DiaryAgent` instance and append
one summarised line. Session 3 reads the diary before calling `run`, so
the diary contents are in the task text. The agent answers from that.

The diary grows one line per session. It never shrinks.

## Where this breaks down

After many sessions the diary gets long. The full text is stuffed into the
context on every recall query. At some point it exceeds the model's context
window, or the early entries become irrelevant noise.

The structured approach in Track 38 avoids this: keys overwrite, so the
file stays the same size. The tradeoff is that free-form notes don't fit
a key-value schema. A memory leak investigation has no obvious key name.

The fixes for the diary approach are pruning (keep only the last N lines),
summarisation (collapse old entries), or retrieval (fetch only the lines
most relevant to the current question). Those add complexity. This track
shows the simple version first.

## Takeaway

A plain text file is often enough for short-lived context. Append the
session note, read it back later. The limitation is growth: you're
accumulating, never compressing.
