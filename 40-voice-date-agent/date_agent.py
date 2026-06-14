"""DateAgent: answers spoken date questions through iterative goal-seeking.

Today's date and weekday are pre-loaded into DateContext before the first
iteration, so the agent can often answer in a single plan. If the first plan
returns a raw date or number rather than a spoken sentence, the evaluator
keeps the loop running until format_response produces a complete answer.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, timedelta
from typing import Any

from opensymbolicai.blueprints import GoalSeeking
from opensymbolicai.core import decomposition, evaluator, primitive
from opensymbolicai.models import GoalContext, GoalEvaluation


class DateContext(GoalContext):
    """Structured knowledge accumulated across date-agent iterations."""

    today: str = ""
    answer: str = ""


class DateAgent(GoalSeeking):
    """Answers date and calendar questions by iterating toward the answer."""

    # ------------------------------------------------------------------
    # Primitives
    # ------------------------------------------------------------------

    @primitive(read_only=True)
    def current_date(self) -> str:
        """Return today's date as YYYY-MM-DD.

        Example: current_date() -> "2026-06-13"
        """
        return str(date.today())

    @primitive(read_only=True)
    def add_time(self, date_str: str, amount: int, unit: str) -> str:
        """Add time to a date. Unit must be 'day', 'week', 'month', or 'year'.

        Example: add_time("2026-06-13", 4, "day")  -> "2026-06-17"
        Example: add_time("2026-06-13", 1, "month") -> "2026-07-13"
        Example: add_time("2026-06-13", -1, "week") -> "2026-06-06"
        """
        d = date.fromisoformat(date_str)
        if unit == "day":
            return str(d + timedelta(days=amount))
        if unit == "week":
            return str(d + timedelta(weeks=amount))
        if unit == "month":
            month = d.month + amount
            year = d.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            day = min(d.day, calendar.monthrange(year, month)[1])
            return str(date(year, month, day))
        if unit == "year":
            return str(date(d.year + amount, d.month, d.day))
        raise ValueError(f"Unknown unit: {unit}")

    @primitive(read_only=True)
    def end_of_month(self, date_str: str) -> str:
        """Return the last day of the month for a given YYYY-MM-DD date.

        Example: end_of_month("2026-07-13") -> "2026-07-31"
        """
        d = date.fromisoformat(date_str)
        last_day = calendar.monthrange(d.year, d.month)[1]
        return str(date(d.year, d.month, last_day))

    @primitive(read_only=True)
    def last_weekday_of_month(self, date_str: str, weekday: str) -> str:
        """Return the last occurrence of a weekday in the month of date_str.

        weekday must be a full English name: 'Monday', 'Tuesday', ..., 'Sunday'.
        Example: last_weekday_of_month("2026-07-01", "Sunday") -> "2026-07-26"
        """
        d = date.fromisoformat(date_str)
        last_day = calendar.monthrange(d.year, d.month)[1]
        end = date(d.year, d.month, last_day)
        names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        target = names.index(weekday)
        delta = (end.weekday() - target) % 7
        return str(end - timedelta(days=delta))

    @primitive(read_only=True)
    def weekday_of(self, date_str: str) -> str:
        """Return the weekday name for a given YYYY-MM-DD date.

        Example: weekday_of("2026-06-13") -> "Friday"
        """
        return date.fromisoformat(date_str).strftime("%A")

    @primitive(read_only=True)
    def days_between(self, from_date: str, to_date: str) -> int:
        """Return the number of days from from_date to to_date (YYYY-MM-DD).

        Example: days_between("2026-06-13", "2026-12-25") -> 195
        """
        return (date.fromisoformat(to_date) - date.fromisoformat(from_date)).days

    @primitive(read_only=True)
    def format_response(self, question: str, result: str) -> str:
        """Use an LLM to produce a natural spoken sentence from a date or count.

        Example: format_response("When is next Tuesday?", "2026-06-17")
                 -> "Next Tuesday falls on Tuesday, 17 June 2026."
        Example: format_response("How many days until Christmas?", "195")
                 -> "There are 195 days until Christmas."
        """
        prompt = (
            f"Question: {question}\n"
            f"Computed result: {result}\n"
            f"Write one short spoken sentence that answers the question naturally. "
            f"If the result is a date, include the full day name and date. "
            f"If the result is a number of days, say how many days away that is."
        )
        return self._llm.generate(prompt).text.strip()

    # ------------------------------------------------------------------
    # GoalSeeking hooks
    # ------------------------------------------------------------------

    def create_context(self, goal: str) -> DateContext:
        today = date.today()
        return DateContext(goal=goal, today=f"{today} ({today.strftime('%A')})")

    def update_context(self, context: GoalContext, execution_result: Any) -> None:
        assert isinstance(context, DateContext)
        value = execution_result.get_value()
        if value is None:
            return
        text = str(value).strip()
        # Only store natural language sentences as the answer; ignore raw dates/numbers
        # so that failed intermediate results don't clobber context.today.
        if text and not re.fullmatch(r"[\d\-]+", text):
            context.answer = text

    @evaluator
    def _check_done(self, _, context: GoalContext) -> GoalEvaluation:
        assert isinstance(context, DateContext)
        return GoalEvaluation(goal_achieved=bool(context.answer))

    # ------------------------------------------------------------------
    # Decompositions — single-step examples that guide each iteration
    # ------------------------------------------------------------------

    @decomposition(
        intent="Get today's date.",
        expanded_intent="Call current_date and return the result.",
    )
    def _example_get_date(self):
        return self.current_date()

    @decomposition(
        intent="What date is 4 days from 2026-06-13?",
        expanded_intent=(
            "Call add_time with the date, amount, and unit to get the result date. "
            "Pass that date string (not the weekday name) to format_response. Return the result."
        ),
    )
    def _example_add(self):
        result = self.add_time("2026-06-13", 4, "day")
        return self.format_response("What date is 4 days from 2026-06-13?", result)

    @decomposition(
        intent="How many days between 2026-06-13 and 2026-12-25?",
        expanded_intent="Call days_between with both dates. Return the result.",
    )
    def _example_days(self):
        d = self.days_between("2026-06-13", "2026-12-25")
        return d

    @decomposition(
        intent="What is the last Sunday of August 2026?",
        expanded_intent=(
            "Call last_weekday_of_month with any date in the target month and the weekday name. "
            "Pass the returned date to format_response. Return the result."
        ),
    )
    def _example_last_weekday(self):
        result = self.last_weekday_of_month("2026-08-01", "Sunday")
        return self.format_response("What is the last Sunday of August 2026?", result)

    @decomposition(
        intent="Format a natural response for a date result.",
        expanded_intent="Call format_response with the original question and computed result. Return the result.",
    )
    def _example_format(self):
        return self.format_response("When is next Tuesday?", "2026-06-17")
