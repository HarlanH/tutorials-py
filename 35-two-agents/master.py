"""MasterAgent: expands the problem text, then routes arithmetic to the CalculatorAgent."""

from __future__ import annotations

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive
from opensymbolicai.llm import LLMConfig

from abbrev_agent import AbbreviationAgent
from calc_agent import CalculatorAgent


class MasterAgent(PlanExecute):
    """Master: passes the full problem to AbbreviationAgent, arithmetic to CalculatorAgent."""

    def __init__(self, llm: LLMConfig, verbose: bool = False, **kwargs) -> None:
        super().__init__(llm=llm, **kwargs)
        self._abbrev = AbbreviationAgent(llm=llm)
        self._calc = CalculatorAgent(llm=llm)
        self._verbose = verbose

    @primitive(read_only=True)
    def expand_problem(self, text: str) -> str:
        """Send the full problem text to the abbreviation agent for expansion.

        Example: expand_problem("I drove 300km at 60kph") -> "I drove 300 kilometers at 60 kilometers per hour"
        """
        result = self._abbrev.run(f"Expand all abbreviations in: {text}")
        if self._verbose:
            print(f"  [AbbreviationAgent plan]\n{result.plan}")
        return str(result.result) if result.success else text

    @primitive(read_only=True)
    def ask_calculator(self, expression: str) -> float:
        """Ask the calculator to evaluate an arithmetic expression.

        Example: ask_calculator("300 / 60") -> 5.0
        """
        result = self._calc.run(f"Calculate: {expression}")
        if self._verbose:
            print(f"  [CalculatorAgent plan]\n{result.plan}")
        return float(result.result) if result.success else 0.0

    @primitive(read_only=True)
    def report(self, expanded_problem: str, answer: float, answer_label: str) -> str:
        """Combine the expanded problem text and the numeric answer into a final result.

        Example: report("I drove 300 kilometers at 60 kilometers per hour ...", 5.0, "hours")
        """
        return f"{expanded_problem} Answer: {answer:.2f} {answer_label}."

    @decomposition(
        intent="I cycled 45km in 1.5hrs. What do km and hrs mean and what was my speed?",
        expanded_intent=(
            "Always call expand_problem first with the full problem text — this replaces every abbreviation. "
            "Then call ask_calculator with the arithmetic expression as a plain string. "
            "Finally call report with the expanded text, the numeric answer, and its unit label. "
            "Every call must be assigned to a variable. Never skip expand_problem."
        ),
    )
    def _example_cycling(self):
        expanded = self.expand_problem("I cycled 45km in 1.5hrs. What do km and hrs mean and what was my speed?")
        speed = self.ask_calculator("45 / 1.5")
        result = self.report(expanded_problem=expanded, answer=speed, answer_label="km/h")
        return result
