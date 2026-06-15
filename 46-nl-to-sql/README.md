# Track 46: Natural language to SQL

An agent that translates a plain-English question into a SQL query and runs it
against a real database. No hand-written SQL required.

The Chinook database (a digital music store) is downloaded automatically on first run.

## The scenario

Five business questions answered by the agent:

1. Who are the top 5 artists by total sales revenue?
2. Which genres have the most tracks?
3. Which billing countries generate the most revenue?
4. What are the 3 best-selling albums?
5. Which employee supports the most customers?

## 1. Install

```bash
uv add opensymbolicai-core
```

```bash
ollama pull qwen2.5-coder:7b
```

## 2. The agent

One primitive.

```python
class SQLAgent(PlanExecute):

    @primitive(read_only=True)
    def run_query(self, sql: str) -> str:
        """Execute a SQL SELECT query and return the results as a formatted table."""
```

The full database schema is loaded once and prepended to each question, so the
agent has everything it needs to write correct SQL on the first attempt:

```python
schema = agent.full_schema()

for question in QUESTIONS:
    task = f"Database schema:\n{schema}\n\nQuestion: {question}"
    result = agent.run(task)
```

`full_schema()` returns a compact one-line-per-table format showing column
names and foreign key references:

```
albums(AlbumId, Title, ArtistId -> artists.ArtistId)
artists(ArtistId, Name)
customers(CustomerId, FirstName, ..., SupportRepId -> employees.EmployeeId)
invoice_items(InvoiceLineId, InvoiceId -> invoices.InvoiceId, TrackId -> tracks.TrackId, UnitPrice, Quantity)
...
```

## 3. Run it

```bash
uv run main.py
```

The database (~860 KB) is downloaded from the SQLite tutorial site on the first run.

## Sample output

```
Model   : qwen2.5-coder:7b
Database: chinook.db
============================================================

Q: Who are the top 5 artists by total sales revenue?
   Attempts: 1  (3.8s)
   Results:
     Name          TotalSales
     ------------  ----------
     Iron Maiden   138.6
     U2            105.93
     Metallica     90.09
     Led Zeppelin  86.13
     Lost          81.59

Q: List the top 3 genres by number of tracks.
   Attempts: 1  (1.8s)
   Results:
     Name   TrackCount
     -----  ----------
     Rock   1297
     Latin  579
     Metal  374

Q: What are the 3 best-selling albums?
   Attempts: 1  (3.7s)
   Results:
     Title                 TotalSales
     --------------------  ----------
     Battlestar Galactica  35.82
     The Office, Season 3  31.84
     Minha Historia        26.73

Q: Which employee supports the most customers?
   Attempts: 1  (2.0s)
   Results:
     FirstName  LastName  SupportCount
     ---------  --------  ------------
     Jane       Peacock   21
```

## What just happened

`main.py` calls `agent.full_schema()` once, then prepends the schema to every
question before passing it to the agent. The agent sees the complete table
structure — column names, types, and foreign key links — and writes the right
SQL without needing to explore the database first.

The plan for each question is two lines:

```python
result = run_query("SELECT ...")
return result
```

## Takeaway

Putting the schema in the task string is the simplest approach: one primitive,
no decompositions, and the agent writes correct SQL on the first attempt for
every question. The schema is small enough to fit comfortably in the prompt,
so there is no reason to discover it at runtime.
