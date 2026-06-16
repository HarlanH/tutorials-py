# Track 48: Chat SQL

A chat interface over a SQL database. Ask questions in plain English, get
answers back as formatted tables, and see the SQL the agent wrote. Follow-up
questions are automatically rephrased using conversation history.

The Chinook database (a digital music store) is downloaded automatically on
first run.

## The scenario

A browser-based chat UI talks to a FastAPI backend. The backend runs an
NL-to-SQL agent against the Chinook database and returns three things: the
answer table, the SQL that produced it, and the rephrased question (when
the message was a follow-up).

Example conversation:

```
You:  Top 5 artists by total sales
AI:   Iron Maiden  138.6
      U2           105.9
      Metallica     90.1
      ...

You:  What about their top albums?
AI:   ↳ Rephrased as: "What are the top albums by Iron Maiden, U2, and Metallica?"
      ...
```

## 1. Install

```bash
uv add opensymbolicai-core fastapi uvicorn
```

```bash
ollama pull qwen2.5-coder:7b
```

## 2. Run

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8048
```

Open [http://127.0.0.1:8048](http://127.0.0.1:8048).

The Chinook database (~860 KB) is downloaded on the first run.

## 3. How it works

### Follow-up rephrasing

Before each agent call, if there is conversation history, the LLM rewrites
the message as a standalone question:

```python
def rephrase(question, history):
    prompt = (
        f"Conversation so far:\n{turns}\n\n"
        f"Follow-up question: {question}\n\n"
        "Rewrite the follow-up as a complete, standalone question..."
    )
    return llm.generate(prompt).text.strip()
```

If the rewritten question is identical to the original it is treated as
already standalone and no rephrased label is shown.

### The agent

One primitive — the same pattern as Track 46:

```python
class SQLAgent(PlanExecute):

    @primitive(read_only=True)
    def run_query(self, sql: str) -> str:
        """Execute a SQL SELECT query and return the results as a formatted table."""
```

The full database schema is prepended to each question so the agent can
write correct SQL without exploring the database first:

```python
task = f"Database schema:\n{schema}\n\nQuestion: {question}"
result = agent.run(task)
```

### The API

```
POST /chat
{ "message": "...", "history": [{"role": "user"|"assistant", "content": "..."}] }

→ { "answer": "...", "sql": "...", "rephrased": "..." | null }
```

The backend retries once if the agent produces a SQL error, which handles
occasional model hallucinations (referencing tables that do not exist).

### The frontend

A single `chat.html` served by FastAPI — no build step, no framework. Chat
bubbles show the answer; a collapsible "View SQL" block shows the query. A
"↳ Rephrased as" line appears when the question was rewritten.

## Sample output

```
You:  Which employee supports the most customers?
AI:   FirstName  LastName  SupportCount
      ---------  --------  ------------
      Jane       Peacock   21

      View SQL ▸
        SELECT e.FirstName, e.LastName, COUNT(c.CustomerId) AS SupportCount
        FROM employees e
        JOIN customers c ON e.EmployeeId = c.SupportRepId
        GROUP BY e.EmployeeId
        ORDER BY SupportCount DESC
        LIMIT 1

You:  What country are most of her customers from?
AI:   ↳ Rephrased as: "What country are most of Jane Peacock's customers from?"
      Country  CustomerCount
      -------  -------------
      USA      13
```

## Takeaway

Conversation history lets a stateless agent handle follow-ups without any
session state on the backend. Each request is self-contained: rephrase the
question, prepend the schema, run the agent, return the result. The LLM does
the context tracking; the server stays simple.
