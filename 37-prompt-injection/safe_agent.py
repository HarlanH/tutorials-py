"""SafeSummarizerAgent: summarises documents using pure Python primitives.

The plan is generated from the task description (a filename) before any
document content is read. Injected text in the document reaches only pure
Python functions — it cannot alter the plan or call new primitives.
"""

from __future__ import annotations

import os
import re

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class SafeSummarizerAgent(PlanExecute):
    """Reads and summarises a document. All primitives are pure Python."""

    @primitive(read_only=True)
    def read_document(self, filename: str) -> str:
        """Read a document from the documents/ directory.

        Directory traversal is blocked — only filenames are accepted.
        Example: read_document("clean_report.txt") -> "Q3 Financial Report ..."
        """
        safe_name = os.path.basename(filename)
        path = os.path.join("documents", safe_name)
        if not os.path.exists(path):
            return f"[File not found: {safe_name}]"
        with open(path) as f:
            return f.read()

    @primitive(read_only=True)
    def extract_facts(self, content: str) -> str:
        """Extract lines containing financial figures from the document.

        Pure Python regex — document content cannot influence this function's logic.
        Example: extract_facts("Revenue: $2.4M\\nExpenses: $1.8M") -> "• Revenue ..."
        """
        facts = [
            line.strip()
            for line in content.splitlines()
            if re.search(r"\$[\d,.]+|\d+%|[\d,]+\s*(M|K|B)\b", line)
        ]
        return "\n".join(f"• {f}" for f in facts) if facts else "No figures found."

    @primitive(read_only=True)
    def format_report(self, filename: str, facts: str) -> str:
        """Format the extracted facts into a final summary.

        Example: format_report("clean_report.txt", "• Revenue: $2.4M") -> "[clean_report.txt] ..."
        """
        return f"[{filename}]\n{facts}"

    @decomposition(
        intent="Summarize the document at documents/clean_report.txt",
        expanded_intent=(
            "Call read_document with the filename to get the content. "
            "Call extract_facts on the content to pull out key figures. "
            "Call format_report with the filename and facts to produce the summary. "
            "Every call must be assigned to a variable."
        ),
    )
    def _example_summarize(self):
        content = self.read_document("clean_report.txt")
        facts = self.extract_facts(content)
        result = self.format_report("clean_report.txt", facts)
        return result
