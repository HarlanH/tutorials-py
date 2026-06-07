"""Two question shapes, two decompositions, four different books.

The two decompositions use Foundation and Neuromancer. The queries below ask
about Dune, 1984, and Hyperion — none of them named in any intent string. The
planner routes each query to the right decomposition shape by matching the
question structure, not the book title.

Usage:
    uv run main.py
"""

from __future__ import annotations

from catalog import BookCatalog
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

QUERIES = [
    "tell me about Dune",
    "how many pages is 1984?",
    "what can you tell me about Hyperion?",
    "how long is Dune?",
]


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)
    agent = BookCatalog(llm=llm)

    for query in QUERIES:
        result = agent.run(query)
        print("--- intent ---")
        print(result.task)
        print("--- plan ---")
        print(result.plan)
        if not result.success:
            print("--- error ---")
            print(result.error)
        else:
            print("--- result ---")
            print(result.result)
        print()


if __name__ == "__main__":
    main()
