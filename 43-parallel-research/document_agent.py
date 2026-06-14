"""DocumentAgent: reads one file and answers a question about it.

Primitives:
  read_file      -- load a text file (truncated to keep context manageable)
  extract_answer -- ask the LLM for a concise answer grounded in that text
"""

from __future__ import annotations

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive

class DocumentAgent(PlanExecute):

    @primitive(read_only=True)
    def read_file(self, path: str) -> str:
        """Load a text file. Returns the first 4000 characters."""
        with open(path, encoding="utf-8") as f:
            return f.read()

    @primitive(read_only=True)
    def extract_answer(self, text: str, question: str) -> str:
        """Answer `question` using only the supplied `text`. One or two sentences."""
        prompt = (
            "Answer the following question using ONLY the text provided.\n"
            "Be concise — one or two sentences.\n\n"
            f"Text:\n{text}\n\n"
            f"Question: {question}"
        )
        return self._llm.generate(prompt).text.strip()

    @decomposition(
        intent="Read articles/newton.txt and answer: What year was Newton born?",
        expanded_intent=(
            "Call read_file with the article path to get the text. "
            "Call extract_answer with the text and the question. Return the result."
        ),
    )
    def _example(self):
        text = self.read_file("articles/newton.txt")
        return self.extract_answer(text, "What year was Newton born?")
