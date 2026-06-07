# Track 23: wikipedia

Ask questions that span multiple Wikipedia articles. The agent fetches each
article as a Python variable, analyses the text, and returns an answer — the
article content never re-enters the LLM context.

## Install

```bash
uv add opensymbolicai-core
```

## Running it

```bash
uv run main.py
```

```
============================================================
Task:   Which has a longer Wikipedia article: Python or JavaScript?
Pipe:   fetched "Python" (40,249 chars), "JavaScript" (33,736 chars)
        73,985 chars total in Python namespace, 0 in the planning prompt
Result: Python (6,143) > JavaScript (5,079)
Plan:
  python_text = fetch(topic="Python")
  javascript_text = fetch(topic="JavaScript")
  python_word_count = word_count(text=python_text)
  javascript_word_count = word_count(text=javascript_text)
  return compare_counts("Python", python_word_count, "JavaScript", javascript_word_count)

============================================================
Task:   Does 'algorithm' appear more in the Artificial Intelligence article or the Computer Science article?
Pipe:   fetched "Artificial Intelligence" (84,083 chars), "Computer Science" (29,882 chars)
        113,965 chars total in Python namespace, 0 in the planning prompt
Result: AI (25) > CS (12)
Plan:
  ai_article = fetch(topic='Artificial Intelligence')
  cs_article = fetch(topic='Computer Science')
  ai_count = count_mentions(text=ai_article, keyword='algorithm')
  cs_count = count_mentions(text=cs_article, keyword='algorithm')
  return compare_counts('AI', ai_count, 'CS', cs_count)

============================================================
Task:   What are the 5 most common words across the Python and JavaScript articles combined?
Pipe:   fetched "Python" (40,249 chars), "JavaScript" (33,736 chars)
        73,985 chars total in Python namespace, 0 in the planning prompt
Result: ['the', 'a', 'and', 'to', 'in']
Plan:
  python_text = fetch(topic="Python")
  javascript_text = fetch(topic="JavaScript")
  combined_text = concat(a=python_text, b=javascript_text)
  return most_common_words(text=combined_text, n=5)

============================================================
Task:   What is the sentiment of the Alan Turing Wikipedia article?
Pipe:   fetched "Alan Turing" (60,200 chars)
        60,200 chars total in Python namespace, 0 in the planning prompt
Result: positive
Plan:
  article_text = fetch(topic="Alan Turing")
  score = sentiment_score(text=article_text)
  return sentiment_label(score=score)
```

## What is happening

The LLM writes a plan before any data exists. When the plan runs, each
`fetch()` call downloads a full Wikipedia article and stores it in a Python
variable. Everything after that — word counts, mention counts, word
frequency — operates on those variables in pure Python.

The article text never touches the planning LLM. The plan prompt contains
only the task question and the list of available primitives.

`sentiment_score()` is the exception: it makes a direct LLM call with the
article text to score sentiment. That call is inside the primitive, not part
of the plan generation step. The planning LLM still never sees the content.

```
OSAI — articles as Python variables
──────────────────────────────────────────────────────────
  fetch("Artificial Intelligence")    fetch("Computer Science")
            │                                  │
            │  84,083 chars                    │  29,882 chars
            │  (Python namespace)              │  (Python namespace)
            ▼                                  ▼
  count_mentions(ai_article, "algorithm")    count_mentions(cs_article, "algorithm")
            │                                  │
            └──────────────┬───────────────────┘
                           ▼
          compare_counts("AI", 25, "CS", 12)  ──►  "AI (25) > CS (12)"
──────────────────────────────────────────────────────────
  LLM sees: 5 lines of code, 0 chars of article text


Tool-calling loop — articles through the context window
──────────────────────────────────────────────────────────
  fetch("Artificial Intelligence")
            │
            ▼
  ┌──────────────────────────────────────────────────────┐
  │  context: "Artificial intelligence (AI) is the       │
  │  simulation of human intelligence processes by        │  ← 84,083 chars
  │  machines, especially computer systems...             │
  │  ... (full article)"                                  │
  └──────────────────────────────────────────────────────┘
            │  LLM reads 84,083 chars, then calls next fetch
            ▼
  ┌──────────────────────────────────────────────────────┐
  │  context: (AI article, 84,083 chars)                  │
  │  + "Computer science is the study of computation,    │  ← +29,882 chars
  │    information, and automation..."                    │
  └──────────────────────────────────────────────────────┘
            │  LLM copies both articles into count_mentions() calls
            ▼
  count_mentions("Artificial intelligence (AI) is...", "algorithm")
  count_mentions("Computer science is the study...", "algorithm")
──────────────────────────────────────────────────────────
  LLM sees: 113,965 chars of article text, multiple times over
```

## Primitives

| Primitive | What it does |
|-----------|-------------|
| `fetch(topic)` | Download a full Wikipedia article by topic name |
| `word_count(text)` | Count words |
| `char_count(text)` | Count characters |
| `unique_word_count(text)` | Count distinct words |
| `count_mentions(text, keyword)` | Count occurrences of a keyword |
| `most_common_words(text, n)` | Top n most frequent words |
| `sentiment_score(text)` | Ask the LLM to score sentiment from -1.0 to +1.0 |
| `sentiment_label(score)` | Map score to positive / neutral / negative |
| `concat(a, b)` | Join two texts |
| `compare_counts(label_a, count_a, label_b, count_b)` | Format a comparison |
