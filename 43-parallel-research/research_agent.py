"""ResearchAgent: decomposes a multi-part question and researches each part in parallel.

Three primitives:
  decompose         -- LLM splits the question into sub-tasks (question + article)
  research_parallel -- ThreadPoolExecutor runs one DocumentAgent per sub-task
  synthesize        -- LLM combines the individual findings into a single answer

The plan for any research question is always the same three lines:
  sub_tasks = decompose(question)
  findings  = research_parallel(sub_tasks)
  return synthesize(question, findings)
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive

from document_agent import DocumentAgent

ARTICLES = {
    "newton":   "articles/newton.txt",
    "einstein": "articles/einstein.txt",
    "curie":    "articles/curie.txt",
    "darwin":   "articles/darwin.txt",
    "turing":   "articles/turing.txt",
}


class ResearchAgent(PlanExecute):

    @primitive(read_only=True)
    def decompose(self, question: str) -> list:
        """Split a multi-part research question into independent sub-tasks.

        Each sub-task covers exactly one person and one article.
        Returns a list of dicts: [{"question": "...", "article": "..."}, ...]
        """
        article_list = "\n".join(f"  {k}: {v}" for k, v in ARTICLES.items())
        prompt = (
            "Split this research question into independent sub-tasks.\n"
            "Each sub-task asks one specific thing about ONE person using ONE article.\n"
            "Do NOT include a step that combines or compares results.\n"
            f"Available articles:\n{article_list}\n\n"
            'Return only a JSON array. Each item: {"question": "...", "article": "..."}\n'
            'Example: [{"question": "What year was Newton born?", "article": "articles/newton.txt"}]\n\n'
            f"Research question: {question}"
        )
        text = self._llm.generate(prompt).text.strip()
        match = re.search(r"\[.*?\]", text, re.DOTALL)
        return json.loads(match.group())

    @primitive(read_only=True)
    def research_parallel(self, sub_tasks: list) -> list:
        """Run each sub-task through a DocumentAgent in its own thread.

        Returns a list of answer strings, one per sub-task.
        """
        def run_one(task: dict) -> str:
            goal = f"Read {task['article']} and answer: {task['question']}"
            result = DocumentAgent(llm=self._llm).run(goal)
            return result.result or ""

        with ThreadPoolExecutor(max_workers=len(sub_tasks)) as pool:
            results = list(pool.map(run_one, sub_tasks))

        for task, finding in zip(sub_tasks, results):
            article = task["article"].split("/")[-1]
            print(f"   [{article}] {task['question']}")
            print(f"      -> {finding}")

        return results

    @primitive(read_only=True)
    def synthesize(self, question: str, findings: list) -> str:
        """Combine individual findings into a single coherent answer."""
        bullets = "\n".join(f"- {f}" for f in findings)
        prompt = (
            f"You have gathered these research findings:\n{bullets}\n\n"
            f"Answer this question in two or three sentences:\n{question}"
        )
        return self._llm.generate(prompt).text.strip()

    @decomposition(
        intent="Which of Newton and Einstein was born earlier?",
        expanded_intent=(
            "Call decompose with the question to get the list of sub-tasks. "
            "Call research_parallel with the sub-tasks to get findings from each article in parallel. "
            "Return the synthesize call with the original question and the findings."
        ),
    )
    def _example(self):
        sub_tasks = self.decompose("Which of Newton and Einstein was born earlier?")
        findings = self.research_parallel(sub_tasks)
        return self.synthesize("Which of Newton and Einstein was born earlier?", findings)
