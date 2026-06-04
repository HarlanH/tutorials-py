# Track 15: expanded_intent

Track 14 gave the planner a worked example: an `intent` and a body. A
decomposition takes one more field, `expanded_intent`, a sentence describing the
**approach** the example uses. It renders as an `Approach:` line in the prompt,
right above the code, so the planner reads the reasoning before the steps.

## Install

```bash
uv add opensymbolicai-core
```

## A finance acronym glossary, forward and reverse

Finance is full of acronyms that are impossible to look up directly: KIKO,
TARN, VOMMA, CDXIG. The glossary has 34 of them, each with an expansion and a
plain-English definition. It supports both directions: given an acronym, explain
it; given a full term, find its acronym.

```python
expand(acronym: str) -> str      # "CVA" -> "credit valuation adjustment"
abbreviate(term: str) -> str     # "Carr-Geman-Madan-Yor model" -> "CGMY"
define(term: str) -> str         # full form -> plain-English sentence
phrase(acronym, full, meaning)   # combines all three into one line
```

`abbreviate` uses fuzzy matching (`difflib.get_close_matches`) so the model
does not need to pass the exact string.

## Two decompositions, two approaches

The forward decomposition teaches the planner to expand an acronym first, then
define the expansion:

```python
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
```

The reverse decomposition teaches the planner to abbreviate a full term, then
define it:

```python
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
```

Each decomposition has a `-> str` return annotation and ends with `return`.
The variable names are unique per example (`cva_result`, `cgmy_result`): the
model follows the pattern but names its own variables per query.

## What the planner sees

The library renders both as prompt examples, each with an `Approach:` line:

```
### Example 1
Intent: what does CVA mean?
Approach: A finance acronym can't be defined directly. Expand it to its full form first, ...
Python:
full = expand('CVA')
meaning = define(full)
cva_result = phrase('CVA', full, meaning)
return cva_result

### Example 2
Intent: what is the acronym for Carr-Geman-Madan-Yor model?
Approach: When given a full term rather than an acronym, the lookup runs in reverse. ...
Python:
acronym = abbreviate('Carr-Geman-Madan-Yor model')
meaning = define('Carr-Geman-Madan-Yor model')
cgmy_result = phrase(acronym, 'Carr-Geman-Madan-Yor model', meaning)
return cgmy_result
```

The `Approach:` line is your `expanded_intent`, verbatim. The `Python:` block
is the method body with `self.` stripped. The planner reads the reasoning before
the code, so it knows which direction to take before it writes a single call.

## The planner follows each approach

Five queries, three forward and two reverse:

```
--- intent ---
what does KIKO mean?
--- plan ---
full = expand('KIKO')
meaning = define(full)
kiko_result = phrase('KIKO', full, meaning)
return kiko_result
--- result ---
KIKO (knock-in knock-out): an exotic option that activates only if the underlying hits one barrier and cancels if it hits another

--- intent ---
what does TARN mean?
--- plan ---
full = expand('TARN')
meaning = define(full)
tarn_result = phrase('TARN', full, meaning)
return tarn_result
--- result ---
TARN (targeted accrual redemption note): a structured note that redeems early once cumulative coupon payments hit a preset target

--- intent ---
what does CDXIG mean?
--- plan ---
full = expand('CDXIG')
meaning = define(full)
cdxig_result = phrase('CDXIG', full, meaning)
return cdxig_result
--- result ---
CDXIG (CDX investment grade index): a credit default swap index tracking the credit risk of investment-grade North American companies

--- intent ---
what is the acronym for Carr-Geman-Madan-Yor model?
--- plan ---
acronym = abbreviate('Carr-Geman-Madan-Yor model')
meaning = define('Carr-Geman-Madan-Yor model')
cgmy_result = phrase(acronym, 'Carr-Geman-Madan-Yor model', meaning)
return cgmy_result
--- result ---
CGMY (Carr-Geman-Madan-Yor model): an option pricing model that captures jumps and heavy tails in asset returns

--- intent ---
what is the acronym for vega-gamma sensitivity?
--- plan ---
acronym = abbreviate('vega-gamma sensitivity')
meaning = define('vega-gamma sensitivity')
vgs_result = phrase(acronym, 'vega-gamma sensitivity', meaning)
return vgs_result
--- result ---
VOMMA (vega-gamma sensitivity): a second-order derivative measuring how a position's vega changes as implied volatility moves
```

The forward queries route through `expand`; the reverse queries route through
`abbreviate`. The planner picks the right path from the `Approach:` line before
it writes a call. Each plan ends with `return`, which the executor evaluates to
produce the final value. The variable names differ per query; the model follows
the example's pattern but names its own variables.

## What expanded_intent is for

`intent` is the question; `expanded_intent` is the method. Reach for it when the
right composition is not obvious from the code: an order that matters, a step
that has to come first, a reason one primitive feeds another. With two
decompositions that go in opposite directions, it is the `Approach:` line that
tells the planner which way to go.
