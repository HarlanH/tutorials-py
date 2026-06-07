"""Wikipedia analyst: fetch articles by topic, analyse as variables.

The LLM generates plans like:

    python = fetch("Python programming language")
    js     = fetch("JavaScript")
    combined = concat(python, js)
    return most_common_words(text=combined, n=5)

Every fetched article lives in a Python variable. The full text — often
thousands of words — is never serialized back into a prompt.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from collections import Counter

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive



# Unambiguous Wikipedia titles for commonly shortened names.
_TITLES = {
    "python": "Python (programming language)",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "artificial intelligence": "Artificial intelligence",
    "ai": "Artificial intelligence",
    "computer science": "Computer science",
    "machine learning": "Machine learning",
    "data science": "Data science",
    "go": "Go (programming language)",
    "rust": "Rust (programming language)",
    "java": "Java (programming language)",
    "alan turing": "Alan Turing",
    "einstein": "Albert Einstein",
    "newton": "Isaac Newton",
}


def _fetch_wikipedia(topic: str) -> str:
    import time
    headers = {"User-Agent": "osai-tutorial/1.0"}

    try:
        # Step 1: resolve the title — use the disambiguation map first,
        # then fall back to Wikipedia search.
        title = _TITLES.get(topic.lower().strip())
        if title is None:
            search_url = (
                "https://en.wikipedia.org/w/api.php?action=query&list=search"
                f"&srsearch={urllib.parse.quote(topic)}&format=json&srlimit=1"
            )
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                results = json.loads(resp.read().decode("utf-8"))
            hits = results.get("query", {}).get("search", [])
            title = hits[0]["title"] if hits else topic

        time.sleep(0.5)  # be polite to the Wikipedia API

        # Step 2: fetch the full plain-text extract for that title.
        extract_url = (
            "https://en.wikipedia.org/w/api.php?action=query&prop=extracts"
            "&explaintext=1&exsectionformat=plain"
            f"&titles={urllib.parse.quote(title)}&format=json"
        )
        req = urllib.request.Request(extract_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()))
        return page.get("extract", "")

    except Exception as exc:
        return f"[fetch failed: {exc}]"


class WikipediaAnalyst(PlanExecute):
    """Answers questions by fetching Wikipedia articles and analysing the text."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cache: dict[str, str] = {}

    # ── Fetch ──────────────────────────────────────────────────────────────

    @primitive(read_only=True)
    def fetch(self, topic: str) -> str:
        """Fetch the Wikipedia article text for a topic (e.g. 'Alan Turing')."""
        if topic not in self._cache:
            self._cache[topic] = _fetch_wikipedia(topic)
        return self._cache[topic]

    # ── Word statistics ────────────────────────────────────────────────────

    @primitive(read_only=True)
    def word_count(self, text: str) -> int:
        """Number of words in the text."""
        return len(text.split())

    @primitive(read_only=True)
    def char_count(self, text: str) -> int:
        """Number of characters in the text."""
        return len(text)

    @primitive(read_only=True)
    def unique_word_count(self, text: str) -> int:
        """Number of unique lowercase words."""
        return len(set(re.findall(r"[a-z]+", text.lower())))

    @primitive(read_only=True)
    def count_mentions(self, text: str, keyword: str) -> int:
        """Number of times keyword appears in text (case-insensitive)."""
        return len(re.findall(re.escape(keyword.lower()), text.lower()))

    @primitive(read_only=True)
    def most_common_words(self, text: str, n: int = 5) -> list[str]:
        """Top n most frequent words in the text."""
        words = re.findall(r"[a-z]+", text.lower())
        return [word for word, _ in Counter(words).most_common(n)]

    # ── Sentiment (LLM-based) ──────────────────────────────────────────────

    @primitive(read_only=True)
    def sentiment_score(self, text: str) -> float:
        """Ask the LLM to score the sentiment of text from -1.0 to +1.0.
        Reply is a single float; defaults to 0.0 on parse failure."""
        prompt = (
            "Rate the overall sentiment of the following text on a scale from "
            "-1.0 (very negative) to +1.0 (very positive). "
            "Reply with only a single decimal number, nothing else.\n\n"
            f"{text}"
        )
        response = self._llm.generate(prompt)
        try:
            return round(float(response.text.strip()), 4)
        except ValueError:
            return 0.0

    @primitive(read_only=True)
    def sentiment_label(self, score: float) -> str:
        """Map a sentiment score to 'positive', 'neutral', or 'negative'."""
        if score > 0.1:
            return "positive"
        if score < -0.1:
            return "negative"
        return "neutral"

    # ── Combination ────────────────────────────────────────────────────────

    @primitive(read_only=True)
    def concat(self, a: str, b: str) -> str:
        """Concatenate two texts."""
        return a + " " + b

    # ── Comparison ─────────────────────────────────────────────────────────

    @primitive(read_only=True)
    def compare_counts(
        self, label_a: str, count_a: int, label_b: str, count_b: int
    ) -> str:
        """Return a formatted comparison: 'Python (1,247) > JavaScript (891)'."""
        if count_a > count_b:
            return f"{label_a} ({count_a:,}) > {label_b} ({count_b:,})"
        elif count_b > count_a:
            return f"{label_b} ({count_b:,}) > {label_a} ({count_a:,})"
        return f"{label_a} = {label_b} ({count_a:,})"
