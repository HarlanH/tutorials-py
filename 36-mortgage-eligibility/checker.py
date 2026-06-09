"""MortgageChecker: uses Z3 to verify mortgage eligibility rules.

Four rules encoded as Z3 constraints (US standard lending guidelines):
  - Age:             applicant must be at least 18
  - Credit score:    FICO score must be at least 620
  - Debt-to-income:  monthly debt must not exceed 43% of monthly income
  - Loan-to-income:  loan amount must not exceed 4.5x annual income

check_eligibility runs all four simultaneously — SAT means approved, UNSAT
identifies exactly which rules the applicant failed.

minimum_income uses Z3 Optimize to find the smallest annual income that
would satisfy the DTI and LTI rules for a given debt and loan amount.
"""

from __future__ import annotations

import z3

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class MortgageChecker(PlanExecute):
    """Z3-backed mortgage eligibility checker."""

    _RULES = {
        "minimum age (18+)":        "applicant must be at least 18 years old",
        "credit score (620+)":      "FICO credit score must be at least 620",
        "debt-to-income (≤43%)":    "monthly debt must not exceed 43% of monthly income",
        "loan-to-income (≤4.5×)":   "loan amount must not exceed 4.5× annual income",
    }

    @primitive(read_only=True)
    def check_eligibility(
        self,
        age: int,
        credit_score: int,
        annual_income: float,
        monthly_debt: float,
        loan_amount: float,
    ) -> str:
        """Check all four mortgage rules simultaneously using Z3.

        Returns an approval or a denial listing every failed rule by name.
        Example: check_eligibility(35, 720, 85000, 1500, 280000) -> "Approved ..."
        """
        age_v   = z3.IntVal(age)
        cs_v    = z3.IntVal(credit_score)
        ai_v    = z3.RealVal(annual_income)
        md_v    = z3.RealVal(monthly_debt)
        la_v    = z3.RealVal(loan_amount)

        rules = {
            "minimum age (18+)":      age_v >= 18,
            "credit score (620+)":    cs_v >= 620,
            "debt-to-income (≤43%)":  md_v * 12 <= z3.RealVal(0.43) * ai_v,
            "loan-to-income (≤4.5×)": la_v <= z3.RealVal(4.5) * ai_v,
        }

        solver = z3.Solver()
        solver.add(z3.And(list(rules.values())))

        if solver.check() == z3.sat:
            return "Approved — all eligibility rules satisfied."

        failed = []
        for name, rule in rules.items():
            s = z3.Solver()
            s.add(rule)
            if s.check() != z3.sat:
                failed.append(name)

        return f"Denied — failed: {', '.join(failed)}."

    @primitive(read_only=True)
    def minimum_income(self, monthly_debt: float, loan_amount: float) -> str:
        """Use Z3 Optimize to find the minimum annual income that satisfies DTI and LTI rules.

        Example: minimum_income(2200, 320000) -> "$71,111.11/year minimum annual income required."
        """
        ai = z3.Real("annual_income")
        opt = z3.Optimize()
        opt.add(ai > 0)
        opt.add(z3.RealVal(monthly_debt) * 12 <= z3.RealVal(0.43) * ai)
        opt.add(z3.RealVal(loan_amount) <= z3.RealVal(4.5) * ai)
        opt.minimize(ai)

        if opt.check() == z3.sat:
            val = opt.model()[ai]
            min_income = float(val.as_decimal(6).rstrip("?"))
            return f"${min_income:,.2f}/year minimum annual income required."
        return "Cannot determine minimum income."

    @decomposition(
        intent="Age 45, credit score 750, income $80,000, monthly debt $1,200, loan $250,000. Is this applicant eligible?",
        expanded_intent=(
            "Call check_eligibility with the applicant's age, credit score, annual income, "
            "monthly debt, and loan amount. Return the result directly."
        ),
    )
    def _example_check(self):
        result = self.check_eligibility(
            age=45, credit_score=750, annual_income=80000,
            monthly_debt=1200, loan_amount=250000,
        )
        return result

    @decomposition(
        intent="Monthly debt $2,000, loan amount $350,000. What is the minimum annual income needed to qualify?",
        expanded_intent=(
            "Call minimum_income with the monthly debt and loan amount. Return the result directly."
        ),
    )
    def _example_income(self):
        result = self.minimum_income(monthly_debt=2000, loan_amount=350000)
        return result
