# Track 36: Mortgage eligibility (Z3)

Legal rules are constraints. Z3 checks whether an applicant satisfies all of
them simultaneously — and when they don't, it tells you exactly which ones failed.

The task:

> Age 42, credit score 680, annual income $55,000, monthly debt $2,200,
> loan amount $320,000. Is Casey eligible for a mortgage?

Z3 returns UNSAT and identifies the two rules Casey violated.

## The rules

Four standard US lending guidelines encoded as Z3 constraints:

| Rule | Constraint |
|------|-----------|
| Minimum age | age ≥ 18 |
| Credit score | FICO ≥ 620 |
| Debt-to-income | monthly debt ≤ 43% of monthly income |
| Loan-to-income | loan amount ≤ 4.5× annual income |

## 1. Install

```bash
uv add opensymbolicai-core z3-solver
```

## 2. The agent

Two primitives:

```python
class MortgageChecker(PlanExecute):

    @primitive(read_only=True)
    def check_eligibility(
        self, age, credit_score, annual_income, monthly_debt, loan_amount
    ) -> str:
        """Check all four rules simultaneously using Z3.

        Returns approval or denial with every failed rule named.
        Example: check_eligibility(35, 720, 85000, 1500, 280000) -> "Approved ..."
        """

    @primitive(read_only=True)
    def minimum_income(self, monthly_debt, loan_amount) -> str:
        """Use Z3 Optimize to find the minimum annual income that satisfies
        the DTI and LTI rules for a given debt and loan amount.

        Example: minimum_income(2200, 320000) -> "$71,111.11/year ..."
        """
```

## 3. Run it

```bash
uv run main.py
```

Four problems — approved, denied (one rule), denied (two rules), and a minimum
income query:

```
[Alex — qualified applicant]
  result: Approved — all eligibility rules satisfied.

[Jordan — low credit score]
  result: Denied — failed: credit score (620+).

[Casey — high debt and large loan]
  result: Denied — failed: debt-to-income (≤43%), loan-to-income (≤4.5×).

[Casey — minimum income to qualify]
  result: $71,111.11/year minimum annual income required.
```

## What just happened

**check_eligibility** adds all four rules as Z3 constraints and calls
`solver.check()`. If the result is SAT, every rule is satisfied — approved.
If UNSAT, it re-checks each rule individually to find which ones failed and
names them in the denial.

**minimum_income** uses `z3.Optimize()` instead of `z3.Solver()`. It encodes
the DTI and LTI rules as inequalities, sets the objective to minimise annual
income, and lets Z3 find the exact threshold. For Casey's case, the LTI rule
is the binding constraint: $320,000 ÷ 4.5 = $71,111.

## Takeaway

Rules encoded as Z3 constraints give you more than a yes/no answer. SAT tells
you the applicant qualifies. UNSAT tells you exactly which rules they failed.
And `z3.Optimize()` can answer "what would it take to qualify?" — turning a
rejection into actionable guidance.
