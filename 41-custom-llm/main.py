"""Track 41: custom LLM class with an in-memory cache.

Run 1 — three calculator questions hit the LLM (cache misses).
Run 2 — the same three questions are served from the cache (cache hits).
"""

from __future__ import annotations

import sys

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive

from my_ollama import InMemoryCache, MyOllamaLLM
from ollama import check_ollama

MODEL = "qwen2.5-coder:7b"

QUESTIONS = [
    "What is 12 multiplied by 8?",
    "What is 144 divided by 12?",
    "What is 50 plus 37?",
]


# ---------------------------------------------------------------------------
# Calculator agent
# ---------------------------------------------------------------------------

class CalculatorAgent(PlanExecute):

    @primitive(read_only=True)
    def add(self, a: float, b: float) -> float:
        """Add two numbers. Example: add(3, 4) -> 7"""
        return a + b

    @primitive(read_only=True)
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a. Example: subtract(10, 3) -> 7"""
        return a - b

    @primitive(read_only=True)
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers. Example: multiply(3, 4) -> 12"""
        return a * b

    @primitive(read_only=True)
    def divide(self, a: float, b: float) -> float:
        """Divide a by b. Example: divide(12, 4) -> 3"""
        return a / b

    @decomposition(
        intent="What is 6 plus 9?",
        expanded_intent="Call the correct arithmetic primitive and return the result.",
    )
    def _example(self):
        return self.add(6, 9)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def run(label: str, llm: MyOllamaLLM, cache: InMemoryCache) -> None:
    print(f"\n{label}")
    print("-" * 40)
    cache.reset()

    for question in QUESTIONS:
        agent = CalculatorAgent(llm=llm)
        result = agent.run(question)
        print(f"Q: {question}")
        print(f"   Plan   : {result.plan.strip()}")
        print(f"   Answer : {result.result}")

    print(f"\nCache — hits: {cache.hits}  misses: {cache.misses}")


def main() -> None:
    if not check_ollama(MODEL):
        sys.exit(1)

    cache = InMemoryCache()
    llm = MyOllamaLLM(model=MODEL, cache=cache)

    run("Run 1 (cold cache)", llm, cache)
    run("Run 2 (warm cache)", llm, cache)


if __name__ == "__main__":
    main()
