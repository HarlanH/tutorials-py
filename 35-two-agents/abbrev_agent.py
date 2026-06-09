"""AbbreviationAgent: expands abbreviations in text to their full written form."""

from __future__ import annotations

import re

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class AbbreviationAgent(PlanExecute):
    """Specialist: replaces abbreviations in text with their full form, nothing else."""

    _ABBREVIATIONS: dict[str, str] = {
        "kph": "kilometers per hour",
        "mph": "miles per hour",
        "km": "kilometers",
        "hr": "hours",
        "hrs": "hours",
        "min": "minutes",
        "sec": "seconds",
        "kg": "kilograms",
        "lb": "pounds",
        "lbs": "pounds",
        "mL": "milliliters",
        "cm": "centimeters",
        "mm": "millimeters",
    }

    @primitive(read_only=True)
    def expand_all(self, text: str) -> str:
        """Replace every known abbreviation in text with its full written form.

        Longer abbreviations are replaced first to avoid partial matches.
        Example: expand_all("300km at 60kph") -> "300 kilometers at 60 kilometers per hour"
        """
        result = text
        for abbr in sorted(self._ABBREVIATIONS, key=len, reverse=True):
            full = self._ABBREVIATIONS[abbr]
            # digit immediately before: "300km" -> "300 kilometers"
            result = re.sub(
                rf"(\d){re.escape(abbr)}(?![a-zA-Z])",
                lambda m, f=full: m.group(1) + " " + f,
                result,
            )
            # space or start before: "at km/h" -> "at kilometers/h"
            result = re.sub(rf"(?<![a-zA-Z\d]){re.escape(abbr)}(?![a-zA-Z])", full, result)
        return result

    @decomposition(
        intent="Expand all abbreviations in: I drove 300km at 60kph.",
        expanded_intent=(
            "Call expand_all with the full text exactly as given. Return the result directly."
        ),
    )
    def _example_expand(self):
        result = self.expand_all("I drove 300km at 60kph.")
        return result
