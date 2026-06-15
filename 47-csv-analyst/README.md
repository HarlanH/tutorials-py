# Track 47: CSV analyst

An agent that answers plain-English questions about a CSV file using real pandas
operations and returns prose answers.

The Titanic passenger dataset (891 rows) is downloaded automatically on first run.

## The scenario

Five questions answered by the agent:

1. What was the survival rate for each passenger class?
2. What was the average age of survivors vs non-survivors?
3. Which sex had a higher survival rate, and by how much?
4. What were the top 3 embarkation towns by number of passengers?
5. What is the median fare paid by survivors vs non-survivors?

## 1. Install

```bash
uv add opensymbolicai-core pandas
```

```bash
ollama pull qwen2.5-coder:7b
```

## 2. The agent

Two primitives.

```python
class CsvAgent(PlanExecute):

    @primitive(read_only=True)
    def get_df(self) -> pd.DataFrame:
        """Return the loaded DataFrame."""

    @primitive(read_only=True)
    def to_string(self, value, question: str) -> str:
        """Convert a pandas result to a readable answer for the given question."""
```

`get_df()` hands the real DataFrame to the plan, which calls pandas methods
directly on the returned object:

```python
df = get_df()
result = df.groupby("pclass")["survived"].mean().round(3)
return to_string(result, "What was the survival rate for each passenger class?")
```

`to_string()` sends the raw pandas output and the original question to the LLM,
which writes a short prose answer.

Column names, dtypes, and three sample rows are prepended to each question so
the agent knows the shape of the data before writing any code:

```python
context = agent.data_context()

for question in QUESTIONS:
    task = f"Dataset context:\n{context}\n\nQuestion: {question}"
    result = agent.run(task)
```

## 3. Run it

```bash
uv run main.py
```

The dataset (~58 KB) is downloaded from the seaborn-data GitHub repository on
the first run.

## Sample output

```
Model  : qwen2.5-coder:7b
Dataset: titanic.csv (891 rows, 15 columns)
============================================================

Q: What was the survival rate for each passenger class?
   (6.4s  plan=710 tok  summarize=145 tok  total=855 tok)
     The survival rate for each passenger class was as follows:
     First Class: 63.0%, Second Class: 47.3%, Third Class: 24.2%.

Q: What was the average age of survivors vs non-survivors?
   (3.9s  plan=776 tok  summarize=127 tok  total=903 tok)
     The average age of survivors was 28.34 compared to 30.63 for non-survivors.

Q: Which sex had a higher survival rate, and by how much?
   (2.6s  plan=715 tok  summarize=130 tok  total=845 tok)
     Females had a higher survival rate than males by 0.553 (0.742 - 0.189).

Q: What were the top 3 embarkation towns by number of passengers?
   (2.7s  plan=716 tok  summarize=145 tok  total=861 tok)
     The top 3 embarkation towns were Southampton with 644, Cherbourg with 168,
     and Queenstown with 77.

Q: What is the median fare paid by survivors vs non-survivors?
   (3.1s  plan=756 tok  summarize=89 tok  total=845 tok)
     The median fare paid by survivors was $26.0, while non-survivors paid $10.5.
```

## What just happened

`data_context()` describes the DataFrame once. The agent uses that description
to write a short pandas plan for each question. The plan calls `get_df()` to get
the real DataFrame, runs standard pandas operations on it, and passes the result
to `to_string()` along with the original question. `to_string()` calls the LLM
a second time to turn the raw data into a readable sentence.

Each question makes two LLM calls: one to generate the plan (`plan` tokens) and
one inside `to_string()` to write the answer (`summarize` tokens). Both counts
are printed so you can see where the token budget goes.

The decomposition example shows the pattern for groupby questions:

```python
@decomposition(
    intent="Which sex had a higher survival rate, and by how much?",
    expanded_intent="Get the DataFrame, group by sex, average the survived column, then summarize.",
)
def _example(self):
    df = self.get_df()
    result = df.groupby("sex")["survived"].mean().round(3)
    return self.to_string(result, "Which sex had a higher survival rate, and by how much?")
```

## Takeaway

Returning a real DataFrame from a primitive lets the plan use the full pandas
API as method calls. No code strings, no `eval()`. The second LLM call in
`to_string()` turns raw numbers into a sentence, so the final answer reads like
a human wrote it.
