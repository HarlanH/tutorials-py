"""Track 43: parallel document research.

ResearchAgent decomposes a research question into per-person sub-tasks,
runs each through a DocumentAgent in parallel, and synthesizes the findings.

Wikipedia articles are downloaded automatically on first run.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

from opensymbolicai.llm import InMemoryCache, LLMConfig, create_llm

from ollama import check_ollama
from research_agent import ResearchAgent

MODEL = "qwen2.5-coder:7b"

WIKIPEDIA_TOPICS = {
    "newton":   "Isaac Newton",
    "einstein": "Albert Einstein",
    "curie":    "Marie Curie",
    "darwin":   "Charles Darwin",
    "turing":   "Alan Turing",
}

QUESTIONS = [
    "Which of Newton, Einstein, and Curie was born earliest, and in which country?",
    "Who among Einstein, Curie, Darwin, and Turing won a Nobel Prize, and for what?",
    "What were the main fields of work for Darwin and Turing? Did their lives overlap in time?",
]


def fetch_article(topic: str, key: str) -> None:
    url = (
        "https://en.wikipedia.org/w/api.php"
        "?action=query&prop=extracts&exchars=4000&explaintext=true"
        f"&titles={topic.replace(' ', '_')}&format=json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "osai-tutorials/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    pages = data["query"]["pages"]
    text = next(iter(pages.values())).get("extract", "")
    Path(f"articles/{key}.txt").write_text(text, encoding="utf-8")
    print(f"  Fetched {topic}")


def ensure_articles() -> None:
    Path("articles").mkdir(exist_ok=True)
    missing = [
        (topic, key)
        for key, topic in WIKIPEDIA_TOPICS.items()
        if not Path(f"articles/{key}.txt").exists()
    ]
    if missing:
        print("Downloading Wikipedia articles...")
        for topic, key in missing:
            fetch_article(topic, key)
        print()


def main() -> None:
    if not check_ollama(MODEL):
        sys.exit(1)

    ensure_articles()

    llm = create_llm(LLMConfig(provider="ollama", model=MODEL), cache=InMemoryCache())
    agent = ResearchAgent(llm=llm)

    print(f"Model: {MODEL}")
    print("=" * 60)

    for question in QUESTIONS:
        print(f"\nQ: {question}")
        t0 = time.time()
        result = agent.run(question)
        print(f"   Answer: {result.result}")
        print(f"   ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
