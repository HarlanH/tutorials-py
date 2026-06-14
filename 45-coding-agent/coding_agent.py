"""CodingAgent: reads a source file, rewrites it per an instruction, then runs it.

Primitives:
  read_file   -- load a Python source file
  rewrite     -- ask the LLM to produce a new version of the source
  write_file  -- save the new version in place
  run_code    -- execute the file and return its output
  respond     -- return the final result
"""

from __future__ import annotations

import subprocess
import sys

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class CodingAgent(PlanExecute):

    @primitive(read_only=True)
    def read_file(self, path: str) -> str:
        """Return the contents of a Python source file."""
        with open(path, encoding="utf-8") as f:
            return f.read()

    @primitive(read_only=True)
    def rewrite(self, source: str, instruction: str) -> str:
        """Apply instruction to source and return the new Python source code."""
        prompt = (
            f"{instruction}\n\n"
            "Return ONLY the new Python source code, no explanation, no markdown fences.\n\n"
            f"Source:\n{source}"
        )
        raw = self._llm.generate(prompt).text.strip()
        # Strip markdown fences if the model adds them anyway
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        return raw.strip()

    @primitive(read_only=False)
    def write_file(self, path: str, content: str) -> str:
        """Write content to path."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"wrote {path}"

    @primitive(read_only=True)
    def run_code(self, path: str) -> str:
        """Run a Python file and return stdout, or stderr on failure."""
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return f"ERROR:\n{result.stderr.strip()}"
        return result.stdout.strip()

    @primitive(read_only=True)
    def respond(self, message: str) -> str:
        """Return message as the final response."""
        return message

    @decomposition(
        intent="Convert programs/fib.py from recursive to iterative.",
        expanded_intent=(
            "Call read_file to load the source. "
            "Call rewrite with the source and a clear instruction. "
            "Call write_file to save the new version. "
            "Call run_code to validate. "
            "Return respond with the run output."
        ),
    )
    def _example(self):
        source = self.read_file("programs/fib.py")
        updated = self.rewrite(source, "Convert the recursive function to iterative. Keep the same interface and output.")
        write_result = self.write_file("programs/fib.py", updated)
        output = self.run_code("programs/fib.py")
        return self.respond(output)
