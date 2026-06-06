"""A number guessing agent.

Follows the same GoalSeeking pattern as the function_optimizer example:
- primitive takes an explicit argument the model picks
- rich context fields the model reads as literals
- decomposition shows the strategy (binary search via midpoint)
- update_context maintains the search range and last hint
"""

from __future__ import annotations

from opensymbolicai.blueprints import GoalSeeking
from opensymbolicai.core import decomposition, evaluator, primitive
from opensymbolicai.models import ExecutionResult, GoalContext, GoalEvaluation, GoalSeekingConfig

SECRET = 742

GOAL = "Guess the secret number between 1 and 1000."


def _hint(n: int) -> str:
    diff = SECRET - n
    distance = abs(diff)
    direction = "go higher" if diff > 0 else "go lower"
    if distance == 0:   return "correct"
    if distance < 25:   return f"burning — {direction}"
    if distance < 100:  return f"hot — {direction}"
    if distance < 200:  return f"warm — {direction}"
    if distance < 400:  return f"cold — {direction}"
    return f"freezing — {direction}"


class HintContext(GoalContext):
    low: int = 1
    high: int = 1000
    last_hint: str = "no guess yet"


class Guesser(GoalSeeking):
    """An agent that converges on a hidden number using binary search."""

    def __init__(self, **kwargs) -> None:
        cfg = kwargs.pop("config", None) or GoalSeekingConfig(max_iterations=20)
        super().__init__(config=cfg, **kwargs)

    def create_context(self, goal: str) -> HintContext:
        return HintContext(goal=goal)

    def update_context(self, context: HintContext, execution_result: ExecutionResult) -> None:
        for step in execution_result.trace.steps:
            if step.primitive_called == "guess" and step.success:
                n_arg = step.args.get("n") or step.args.get("arg0")
                if n_arg is None:
                    continue
                n = int(n_arg.resolved_value)
                hint = str(step.result_value)
                context.last_hint = hint
                if "go higher" in hint:
                    context.low = max(context.low, n + 1)
                elif "go lower" in hint:
                    context.high = min(context.high, n - 1)

    @primitive(read_only=True)
    def midpoint(self, low: int, high: int) -> int:
        """Return the midpoint of [low, high]."""
        return (low + high) // 2

    @primitive(read_only=True)
    def guess(self, n: int) -> str:
        """Guess n. Returns a temperature hint and direction, e.g. 'hot — go lower'."""
        return _hint(n)

    @decomposition(
        intent="guess the midpoint of [low, high] from context",
        expanded_intent=(
            "Each iteration the context shows updated low and high values. "
            "Substitute those exact integers into midpoint(), then call guess(n)."
        ),
    )
    def _example(self) -> str:
        # context: low=501, high=1000 after a 'cold — go higher' on 500
        n = self.midpoint(501, 1000)
        result = self.guess(n)
        return result

    @evaluator
    def _check(self, goal: str, context: HintContext) -> GoalEvaluation:
        return GoalEvaluation(goal_achieved=context.last_hint == "correct")
