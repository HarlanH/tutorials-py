"""A finance acronym glossary agent.

The point of this agent is its intermediate step. You cannot define an acronym
directly: `define` is keyed on the full term, not the short form. So a plan has
to expand the acronym first, then define the expansion, then phrase the two
together. That two-stage approach is what the decomposition's expanded_intent
spells out.
"""

from __future__ import annotations

from difflib import get_close_matches

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive

# Obscure finance acronyms: short form -> full form
ACRONYMS = {
    "AAD":    "adjoint algorithmic differentiation",
    "CBBC":   "callable bull/bear contract",
    "CDRAN":  "callable daily range accrual note",
    "CDXIG":  "CDX investment grade index",
    "CGMY":   "Carr-Geman-Madan-Yor model",
    "CLN":    "credit linked note",
    "CMBX":   "commercial mortgage-backed securities index",
    "CVA":    "credit valuation adjustment",
    "DV01":   "dollar value of one basis point",
    "DVA":    "debt valuation adjustment",
    "DRAN":   "daily range accrual note",
    "EFFR":   "effective federal funds rate",
    "EONIA":  "euro overnight index average",
    "GCF":    "general collateral financing",
    "ITRAXX": "international index of credit default swaps",
    "KIKO":   "knock-in knock-out",
    "NDFs":   "non-deliverable forwards",
    "OBPI":   "option-based portfolio insurance",
    "OIS":    "overnight indexed swap",
    "PRDC":   "power reverse dual currency note",
    "PVBP":   "price value of a basis point",
    "SABRW":  "SABR model with weights",
    "SARON":  "Swiss average rate overnight",
    "SHIBOR": "Shanghai interbank offered rate",
    "SOFR":   "secured overnight financing rate",
    "SONIA":  "sterling overnight index average",
    "SSR":    "skew stickiness ratio",
    "STRIP":  "separate trading of registered interest and principal",
    "SWAPTION": "swap option",
    "TARN":   "targeted accrual redemption note",
    "TBA":    "to-be-announced",
    "TONAR":  "Tokyo overnight average rate",
    "VANNA":  "vega-delta sensitivity",
    "VOMMA":  "vega-gamma sensitivity",
}

# Full form -> plain-English one-liner
DEFINITIONS = {
    "adjoint algorithmic differentiation": "a technique that accelerates sensitivity calculations in derivatives pricing",
    "callable bull/bear contract": "a leveraged structured product tracking an underlying asset that can be called early",
    "callable daily range accrual note": "a note that accrues interest only on days the underlying stays within a set range, and can be called by the issuer",
    "CDX investment grade index": "a credit default swap index tracking the credit risk of investment-grade North American companies",
    "Carr-Geman-Madan-Yor model": "an option pricing model that captures jumps and heavy tails in asset returns",
    "credit linked note": "a structured product that combines a bond with a credit default swap on a reference entity",
    "commercial mortgage-backed securities index": "an index tracking the credit risk of pools of commercial real estate loans",
    "credit valuation adjustment": "an adjustment to a derivative's fair value to account for the risk that a counterparty may default",
    "dollar value of one basis point": "how much a fixed-income position gains or loses when yields move by one hundredth of a percent",
    "debt valuation adjustment": "an adjustment reflecting the risk that the derivative writer itself may default",
    "daily range accrual note": "a structured note that pays interest only for each day the underlying rate stays within a predefined band",
    "effective federal funds rate": "the volume-weighted median rate on overnight unsecured borrowing between US banks",
    "euro overnight index average": "the former overnight benchmark rate for euro interbank lending, replaced by EUR-STR in 2022",
    "general collateral financing": "a repurchase agreement where the borrower can deliver any high-quality security as collateral",
    "international index of credit default swaps": "a family of benchmark indices tracking credit risk across European, Asian, and other markets",
    "knock-in knock-out": "an exotic option that activates only if the underlying hits one barrier and cancels if it hits another",
    "non-deliverable forwards": "currency forward contracts that settle in a major currency rather than the restricted local currency",
    "option-based portfolio insurance": "a strategy protecting a portfolio's downside by combining risky assets with put options",
    "overnight indexed swap": "an interest rate swap where one leg pays a fixed rate and the other pays compounded overnight rates",
    "power reverse dual currency note": "a structured bond that pays high foreign-currency coupons converted back at a leveraged exchange rate",
    "price value of a basis point": "the change in a bond's price for a one basis point move in its yield",
    "SABR model with weights": "an extension of the SABR volatility model that fits the observed volatility surface more accurately",
    "Swiss average rate overnight": "Switzerland's risk-free overnight lending rate, secured by Swiss franc repurchase agreements",
    "Shanghai interbank offered rate": "the benchmark interest rate for short-term lending between banks in China",
    "secured overnight financing rate": "the US risk-free overnight rate based on Treasury repo transactions, replacing USD LIBOR",
    "sterling overnight index average": "the UK's risk-free overnight rate for unsecured sterling lending between banks",
    "skew stickiness ratio": "a measure of how much implied volatility shifts when the spot price moves",
    "separate trading of registered interest and principal": "a zero-coupon security created by stripping the coupons from a Treasury bond",
    "swap option": "the right, but not the obligation, to enter into an interest rate swap at a future date",
    "targeted accrual redemption note": "a structured note that redeems early once cumulative coupon payments hit a preset target",
    "to-be-announced": "a forward market for mortgage-backed securities where the specific bonds are identified just before settlement",
    "Tokyo overnight average rate": "Japan's risk-free overnight rate based on actual unsecured call money market transactions",
    "vega-delta sensitivity": "a second-order derivative measuring how a position's delta changes as implied volatility moves",
    "vega-gamma sensitivity": "a second-order derivative measuring how a position's vega changes as implied volatility moves",
}

# Reverse map: full form -> acronym, derived from ACRONYMS.
REVERSE = {v: k for k, v in ACRONYMS.items()}


class Glossary(PlanExecute):
    """Expand or abbreviate a finance term, define it, and phrase the answer."""

    @primitive(read_only=True)
    def expand(self, acronym: str) -> str:
        """Expand a finance acronym to its full form."""
        full = ACRONYMS.get(acronym)
        if full is None:
            raise ValueError(f"Unknown acronym: {acronym}")
        return full

    @primitive(read_only=True)
    def define(self, term: str) -> str:
        """Define a full financial term in plain words."""
        meaning = DEFINITIONS.get(term)
        if meaning is None:
            raise ValueError(f"No definition for: {term}")
        return meaning

    @primitive(read_only=True)
    def abbreviate(self, term: str) -> str:
        """Return the acronym for a given full financial term, using fuzzy matching."""
        hits = get_close_matches(term, REVERSE.keys(), n=1, cutoff=0.6)
        if not hits:
            raise ValueError(f"No acronym found for: {term}")
        return REVERSE[hits[0]]

    @primitive(read_only=True)
    def phrase(self, acronym: str, full: str, meaning: str) -> str:
        """Phrase an acronym, its full form, and its meaning as one sentence."""
        return f"{acronym} ({full}): {meaning}"

    @decomposition(
        intent="what does CVA mean?",
        expanded_intent=(
            "A finance acronym can't be defined directly. Expand it to its full "
            "form first, then define that full form, then phrase the acronym, "
            "full form, and meaning together into one answer."
        ),
    )
    def _example_cva(self) -> str:
        full = self.expand("CVA")
        meaning = self.define(full)
        cva_result = self.phrase("CVA", full, meaning)
        return cva_result

    @decomposition(
        intent="what is the acronym for Carr-Geman-Madan-Yor model?",
        expanded_intent=(
            "When given a full term rather than an acronym, the lookup runs in "
            "reverse. Abbreviate the full term to find its acronym, define the "
            "full term directly, then phrase the acronym, full form, and meaning "
            "together."
        ),
    )
    def _example_cgmy_reverse(self) -> str:
        acronym = self.abbreviate("Carr-Geman-Madan-Yor model")
        meaning = self.define("Carr-Geman-Madan-Yor model")
        cgmy_result = self.phrase(acronym, "Carr-Geman-Madan-Yor model", meaning)
        return cgmy_result
