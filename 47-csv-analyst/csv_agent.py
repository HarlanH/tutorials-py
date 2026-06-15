"""CsvAgent: answers questions about a pandas DataFrame.

The caller loads the CSV and calls data_context() to build a schema+sample
string prepended to each question. Two primitives: get_df() returns the
DataFrame; to_string() converts a pandas result to a printable string.
"""

from __future__ import annotations

import pandas as pd

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class CsvAgent(PlanExecute):

    def __init__(self, df: pd.DataFrame, llm) -> None:
        super().__init__(llm=llm)
        self._df = df
        self.last_summarize_tokens: int = 0

    def data_context(self) -> str:
        """Return column names, dtypes, and a few sample rows."""
        lines = ["Columns:"]
        for col, dtype in self._df.dtypes.items():
            lines.append(f"  {col} ({dtype})")
        lines.append("\nSample rows (first 3):")
        lines.append(self._df.head(3).to_string(index=False))
        return "\n".join(lines)

    @decomposition(
        intent="Which sex had a higher survival rate, and by how much?",
        expanded_intent="Get the DataFrame, group by sex, average the survived column, then summarize.",
    )
    def _example(self):
        df = self.get_df()
        result = df.groupby("sex")["survived"].mean().round(3)
        return self.to_string(result, "Which sex had a higher survival rate, and by how much?")

    @primitive(read_only=True)
    def get_df(self) -> pd.DataFrame:
        """Return the loaded DataFrame."""
        return self._df

    @primitive(read_only=True)
    def to_string(self, value, question: str) -> str:
        """Convert a pandas result to a readable answer for the given question."""
        prompt = (
            f"Question: {question}\n\n"
            f"Data:\n{value}\n\n"
            "Write a concise, plain-English answer to the question using only the data above. "
            "No preamble, no markdown."
        )
        response = self._llm.generate(prompt)
        self.last_summarize_tokens = response.usage.total_tokens
        return response.text.strip()
