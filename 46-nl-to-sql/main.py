"""Track 46: natural language to SQL.

The full database schema is loaded once and prepended to each question, so
the agent can write SQL in one shot without needing to discover the schema.
The Chinook database is downloaded automatically on first run.
"""

from __future__ import annotations

import io
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

from opensymbolicai.llm import GenerationParams, InMemoryCache, LLMConfig, create_llm

from ollama import check_ollama
from sql_agent import SQLAgent

MODEL = "qwen2.5-coder:7b"
DB_PATH = "chinook.db"
DB_URL = "https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip"

QUESTIONS = [
    "Who are the top 5 artists by total sales revenue?",
    "List the top 3 genres by number of tracks.",
    "Which billing countries generate the most revenue? Show the top 5 by total invoice amount.",
    "What are the 3 best-selling albums?",
    "Which employee supports the most customers? Show their full name and the count.",
]


def ensure_db() -> None:
    if Path(DB_PATH).exists():
        return
    print("Downloading Chinook database...")
    req = urllib.request.Request(DB_URL, headers={"User-Agent": "osai-tutorials/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".db"))
        Path(DB_PATH).write_bytes(zf.read(name))
    print(f"  Saved {DB_PATH} ({Path(DB_PATH).stat().st_size // 1024} KB)\n")


def main() -> None:
    if not check_ollama(MODEL):
        sys.exit(1)

    ensure_db()

    llm = create_llm(
        LLMConfig(provider="ollama", model=MODEL, params=GenerationParams(temperature=0)),
        cache=InMemoryCache(),
    )
    agent = SQLAgent(db_path=DB_PATH, llm=llm)
    schema = agent.full_schema()

    print(f"Model   : {MODEL}")
    print(f"Database: {DB_PATH}")
    print("=" * 60)

    for question in QUESTIONS:
        print(f"\nQ: {question}")
        t0 = time.time()
        task = f"Database schema:\n{schema}\n\nQuestion: {question}"
        result = agent.run(task)
        elapsed = time.time() - t0

        attempts = len(result.plan_attempts) if result.plan_attempts else 1
        print(f"   Attempts: {attempts}  ({elapsed:.1f}s)")
        output = result.result
        if not isinstance(output, str):
            output = "(none)"
        print(f"   Results:")
        for line in output.splitlines():
            print(f"     {line}")


if __name__ == "__main__":
    main()
