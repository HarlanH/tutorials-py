# Track 43: Parallel document research

Two agents, one inside the other. A `DocumentAgent` reads one file and
extracts a fact. A `ResearchAgent` decomposes a multi-part question into
per-person sub-tasks and runs a `DocumentAgent` for each in parallel threads.

## The scenario

Five Wikipedia articles, three research questions:

> "Which of Newton, Einstein, and Curie was born earliest, and in which country?"
> "Who among Einstein, Curie, Darwin, and Turing won a Nobel Prize, and for what?"
> "What were the main fields of work for Darwin and Turing? Did their lives overlap in time?"

For each question, `ResearchAgent` splits it into sub-tasks, looks up each
article in parallel, then combines the findings into a single answer.

## 1. Install

```bash
uv add opensymbolicai-core
```

```bash
ollama pull qwen2.5-coder:7b
```

Wikipedia articles are downloaded automatically on first run.

## 2. DocumentAgent

`DocumentAgent` handles one file and one question. It has two primitives:

```python
class DocumentAgent(PlanExecute):

    @primitive(read_only=True)
    def read_file(self, path: str) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()[:MAX_CHARS]

    @primitive(read_only=True)
    def extract_answer(self, text: str, question: str) -> str:
        prompt = (
            "Answer the following question using ONLY the text provided.\n"
            "Be concise, one or two sentences.\n\n"
            f"Text:\n{text}\n\nQuestion: {question}"
        )
        return self._llm.generate(prompt).text.strip()
```

Given the goal `"Read articles/newton.txt and answer: What year was Newton born?"`,
it generates a two-line plan:

```python
text = read_file("articles/newton.txt")
return extract_answer(text, "What year was Newton born?")
```

## 3. ResearchAgent

`ResearchAgent` coordinates multiple `DocumentAgent` instances. It has three
primitives: decompose, research in parallel, and synthesize.

```python
class ResearchAgent(PlanExecute):

    @primitive(read_only=True)
    def decompose(self, question: str) -> list:
        """Split a multi-part question into sub-tasks, each with a question and article path."""
        ...

    @primitive(read_only=True)
    def research_parallel(self, sub_tasks: list) -> list:
        """Run one DocumentAgent per sub-task in a thread pool. Returns a list of answers."""
        def run_one(task: dict) -> str:
            goal = f"Read {task['article']} and answer: {task['question']}"
            return DocumentAgent(llm=self._llm).run(goal).result or ""

        with ThreadPoolExecutor(max_workers=len(sub_tasks)) as pool:
            return list(pool.map(run_one, sub_tasks))

    @primitive(read_only=True)
    def synthesize(self, question: str, findings: list) -> str:
        """Combine individual findings into a single coherent answer."""
        ...
```

Every question generates the same three-line plan:

```python
sub_tasks = decompose("Which of Newton, Einstein, and Curie was born earliest...?")
findings  = research_parallel(sub_tasks)
return synthesize("Which of Newton, Einstein, and Curie was born earliest...?", findings)
```

## 4. Run it

```bash
uv run main.py
```

## Sample output

```
Model: qwen2.5-coder:7b
============================================================

Q: Which of Newton, Einstein, and Curie was born earliest, and in which country?
   [newton.txt]   In what year was Newton born?
      -> 1643
   [einstein.txt] In what year was Einstein born?
      -> 1879
   [curie.txt]    In what year was Curie born?
      -> 1867
   Answer: Newton was born earliest, in 1643, in England.
   (10.1s)

Q: Who among Einstein, Curie, Darwin, and Turing won a Nobel Prize, and for what?
   [einstein.txt] Did Einstein win a Nobel Prize?
      -> Yes, Albert Einstein won the 1921 Nobel Prize in Physics.
   [curie.txt]    Did Curie win a Nobel Prize?
      -> Yes, Marie Curie won two Nobel Prizes: Physics 1903, Chemistry 1911.
   [darwin.txt]   Did Darwin win a Nobel Prize?
      -> No, Darwin did not win a Nobel Prize.
   [turing.txt]   Did Turing win a Nobel Prize?
      -> No, Turing did not win a Nobel Prize.
   Answer: Einstein won the 1921 Nobel Prize in Physics for the photoelectric
           effect. Curie won two: Physics 1903 for radioactivity research,
           Chemistry 1911 for discovering radium and polonium. Darwin and
           Turing did not win a Nobel Prize.
   (26.0s)

Q: What were the main fields of work for Darwin and Turing? Did their lives overlap in time?
   [darwin.txt]   What were the main fields of work for Darwin?
      -> Natural history, geology, and biology. Best known for evolutionary
         biology and the theory of natural selection.
   [turing.txt]   What were the main fields of work for Turing?
      -> Theoretical computer science, algorithms, cryptanalysis, and logic.
   Answer: Darwin worked in natural history, geology, and biology. Turing
           worked in theoretical computer science and cryptanalysis. Darwin
           died in 1882; Turing was born in 1912. Their lives did not overlap.
   (17.9s)
```

## What just happened

`decompose` asks the LLM to split the question into per-person sub-tasks
and assigns each an article path. `research_parallel` spawns one
`DocumentAgent` per sub-task in a thread pool, so the lookups run
concurrently. Each `DocumentAgent` runs its own two-step plan independently.
`synthesize` sees only the collected text snippets and writes the final answer.

The LLM is called three times at the `ResearchAgent` level (decompose,
each synthesize) and twice per `DocumentAgent` (read + extract). For a
three-person question, that is 3 + 2*3 = 9 LLM calls, all but the first
and last running in parallel.

## Takeaway

A `PlanExecute` agent can call another `PlanExecute` agent as a primitive.
The outer agent handles decomposition and coordination. The inner agent handles
one focused task. Thread safety is straightforward because each inner agent
is a fresh instance with no shared state.

```python
def run_one(task: dict) -> str:
    goal = f"Read {task['article']} and answer: {task['question']}"
    return DocumentAgent(llm=self._llm).run(goal).result or ""

with ThreadPoolExecutor(max_workers=len(sub_tasks)) as pool:
    return list(pool.map(run_one, sub_tasks))
```

The same pattern scales to any number of documents or sub-tasks without
changing either agent class.
