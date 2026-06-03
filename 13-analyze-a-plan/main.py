"""Look at what a plan would do, without running it.

`agent.analyze_plan(plan)` parses a plan and reports every primitive call it
makes: the method name, whether that method is read-only, and the arguments. It
runs nothing. The model is not called either; this is pure static inspection of
the plan text.

The payoff is the question you can answer up front: which mutating primitives
does this plan touch? For a bank account, that is "does this plan move money?"
You can check before you ever execute.

Usage:
    uv run main.py
"""

from __future__ import annotations

from account import Account
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

# Two plans we wrote by hand. One only checks the balance; one changes it.
READ_ONLY_PLAN = """ok = can_afford(100, 30)
big = can_afford(100, 250)"""

MUTATING_PLAN = """balance = deposit(100, 50)
balance = withdraw(balance, 30)
ok = can_afford(balance, 200)"""


def show(label: str, plan: str, agent: Account) -> None:
    print(f"--- {label} ---")
    print(plan)
    analysis = agent.analyze_plan(plan)  # PlanAnalysis, nothing runs
    for call in analysis.calls:  # each is a PrimitiveCall
        flag = "read-only" if call.read_only else "mutating"
        print(f"  {call.method_name}: {flag}  args={call.args}")
    print("has_mutations:", analysis.has_mutations)
    mutating = [c.method_name for c in analysis.calls if not c.read_only]
    print("mutating primitives:", mutating)
    print()


def main() -> None:
    model = "qwen2.5-coder:7b"
    # Kept for parity with the other native tracks; analyze_plan never calls the model.
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)
    agent = Account(llm=llm)

    show("read-only plan", READ_ONLY_PLAN, agent)
    show("plan that moves money", MUTATING_PLAN, agent)


if __name__ == "__main__":
    main()
