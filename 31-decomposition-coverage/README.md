# Track 31: Decomposition coverage

A decomposition is a few-shot example of how a user expects a query to work.
You write it once to show the shape of the answer (which primitives to call,
in what order, with what template) and the planner uses it as a reference when
it sees a similar question. This track shows what happens when you have none,
one, and two of them, and how the planner matches on question shape rather than
on the specific book title in the intent string.

## Install

```bash
uv add opensymbolicai-core
```

## The catalog

Four primitives over a small hardcoded book catalog:

```python
find(query: str) -> str          # fuzzy-match a title; return the canonical form
author(title: str) -> str        # who wrote it
pages(title: str) -> int         # how many pages
format(template, title, author, pages) -> str   # fill a sentence template
```

## Stage 1: no decompositions

Without any few-shot examples the planner has only docstrings to go on. Ask it
"tell me about Dune" and it will probably produce a valid plan, but the shape is
unpredictable: it might skip `author`, it might skip `format`, it might call
things in a different order each run.

There is nothing to point it toward a specific path.

## Stage 2: one decomposition

Add one few-shot example:

```python
@decomposition(intent="tell me about Foundation")
def _example_about(self) -> str:
    title = self.find("Foundation")
    auth = self.author(title)
    pg = self.pages(title)
    return self.format("{title} by {author} has {pages} pages", title=title, author=auth, pages=pg)
```

The library injects this into the planner's prompt as:

```
## Example Decompositions

### Example 1
Intent: tell me about Foundation
Python:
title = find("Foundation")
auth = author(title)
pg = pages(title)
return format("{title} by {author} has {pages} pages", title=title, author=auth, pages=pg)
```

Now ask "tell me about Dune". The planner matches the question shape, not the
book title, and follows the example:

```
title = find("Dune")
auth = author(title)
pg = pages(title)
result = format("{title} by {author} has {pages} pages", title=title, author=auth, pages=pg)
```

```
Dune by Frank Herbert has 412 pages
```

But ask "how many pages is 1984?" and the planner is back to guessing. There is
no example for that shape, so it picks its own path.

## Stage 3: two decompositions

Add a second few-shot example with a structurally different path:

```python
@decomposition(intent="how many pages is Neuromancer?")
def _example_pages(self) -> str:
    title = self.find("Neuromancer")
    pg = self.pages(title)
    return self.format("{title} has {pages} pages", title=title, pages=pg)
```

The two intents are "tell me about Foundation" and "how many pages is
Neuromancer?", opposite books. A query about Foundation would route to the
pages example, and a query about Neuromancer would route to the about example.
The routing is on question shape, not title.

Now the planner has two patterns to choose from. Ask "how many pages is 1984?"
and it matches the second shape: shorter path, no `author` call, different
template:

```
title = find("1984")
pg = pages(title)
result = format("{title} has {pages} pages", title=title, pages=pg)
```

```
1984 has 328 pages
```

The two decompositions cover two shapes:
- **about**: find -> author -> pages -> format with author in the template
- **pages**: find -> pages -> format without author

Any question that fits either shape gets the right path. Questions outside both
shapes fall back to docstrings only, which is a signal to write a third
decomposition.

## Running it

```python
QUERIES = [
    "tell me about Dune",
    "how many pages is 1984?",
    "what can you tell me about Hyperion?",
    "how long is Dune?",
]
```

None of these appear in either intent string. The first and third match the
"about" shape; the second and fourth match the "pages" shape. Run them:

```bash
uv run main.py
```

```
--- intent ---
tell me about Dune
--- plan ---
title = find("Dune")
auth = author(title)
pg = pages(title)
result = format("{title} by {author} has {pages} pages", title=title, author=auth, pages=pg)
--- result ---
Dune by Frank Herbert has 412 pages

--- intent ---
how many pages is 1984?
--- plan ---
title = find("1984")
pg = pages(title)
result = format("{title} has {pages} pages", title=title, pages=pg)
--- result ---
1984 has 328 pages
```

Two question shapes, two few-shot examples, and the planner routes correctly
across four books it never saw in either.

## Try it yourself

Open `catalog.py` and comment out one or both decompositions, then rerun:

- Comment out `_example_pages`: the "how many pages" queries lose their guide
  and the plan shape becomes unpredictable.
- Comment out both: all four queries fall back to docstrings only and the
  planner picks a different path each time.

This makes the effect of each few-shot example visible in isolation.
