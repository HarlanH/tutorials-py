"""Track 47: CSV analyst.

CsvAgent answers plain-English questions about the Titanic passenger dataset.
The CSV is downloaded automatically on first run.
"""

from __future__ import annotations

import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

from opensymbolicai.llm import LLMConfig, create_llm

from csv_agent import CsvAgent
from ollama import check_ollama

MODEL = "qwen2.5-coder:7b"
CSV_PATH = "titanic.csv"
CSV_URL = (
    "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"
)

QUESTIONS = [
    "What was the survival rate for each passenger class?",
    "What was the average age of survivors vs non-survivors?",
    "Which sex had a higher survival rate, and by how much?",
    "What were the top 3 embarkation towns by number of passengers?",
    "What is the median fare paid by survivors vs non-survivors?",
]


def ensure_csv() -> None:
    if Path(CSV_PATH).exists():
        return
    print("Downloading Titanic dataset...")
    urllib.request.urlretrieve(CSV_URL, CSV_PATH)
    print(f"  Saved {CSV_PATH} ({Path(CSV_PATH).stat().st_size // 1024} KB)\n")


def main() -> None:
    if not check_ollama(MODEL):
        sys.exit(1)

    ensure_csv()

    df = pd.read_csv(CSV_PATH)
    llm = create_llm(LLMConfig(provider="ollama", model=MODEL))
    agent = CsvAgent(df=df, llm=llm)
    context = agent.data_context()

    print(f"Model  : {MODEL}")
    print(f"Dataset: {CSV_PATH} ({len(df)} rows, {len(df.columns)} columns)")
    print("=" * 60)

    for question in QUESTIONS:
        print(f"\nQ: {question}")
        t0 = time.time()
        task = f"Dataset context:\n{context}\n\nQuestion: {question}"
        result = agent.run(task)
        elapsed = time.time() - t0

        output = result.result if isinstance(result.result, str) else "(none)"
        plan_tok = result.metrics.plan_tokens.total_tokens if result.metrics else 0
        summ_tok = agent.last_summarize_tokens
        print(f"   ({elapsed:.1f}s  plan={plan_tok} tok  summarize={summ_tok} tok  total={plan_tok + summ_tok} tok)")
        for line in output.splitlines():
            print(f"     {line}")


if __name__ == "__main__":
    main()
