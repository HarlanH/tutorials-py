"""Demonstrate the on_mutation policy hook.

The hook fires only for read_only=False primitives (deposit, withdraw).
It receives a MutationHookContext with the method name and arguments.
Return None to allow the call; return a string to block it.

Every call — allowed or blocked — is recorded in an audit log. Read-only
primitives never appear in the log at all.

Usage:
    uv run main.py
"""

from __future__ import annotations

from bank import BankAgent
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig
from opensymbolicai.models import MutationHookContext, PlanExecuteConfig

TASKS = [
    "What is the balance of ACC-001?",
    "Deposit $200 into ACC-001.",
    "Withdraw $800 from ACC-001.",
]

LIMIT = 500.0

_AUDIT: list[str] = []


def policy(ctx: MutationHookContext) -> str | None:
    # Keyword call → "amount"; positional call → "arg1" (account is arg0).
    amount = float(ctx.args.get("amount", ctx.args.get("arg1", 0.0)))
    if ctx.method_name == "withdraw" and amount > LIMIT:
        reason = f"${amount:.2f} exceeds the ${LIMIT:.0f} single-transaction limit"
        _AUDIT.append(f"BLOCKED  {ctx.method_name:<10} ${amount:>8.2f}  {reason}")
        return reason
    _AUDIT.append(f"ALLOWED  {ctx.method_name:<10} ${amount:>8.2f}")
    return None


def run(llm: LLMConfig, task: str) -> None:
    config = PlanExecuteConfig(on_mutation=policy)
    agent = BankAgent(llm=llm, config=config)
    print(f"Task:   {task}")
    result = agent.run(task)
    if result.success:
        print(f"Result: {result.result}")
    else:
        print(f"Result: {result.error}")
    print("Plan:")
    for line in result.plan.splitlines():
        print(f"  {line}")
    print()


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    print("=" * 60)
    print("Primitives and their read_only setting:\n")
    print("  get_account  read_only=True   (hook never fires)")
    print("  get_balance  read_only=True   (hook never fires)")
    print("  deposit      read_only=False  (hook fires)")
    print("  withdraw     read_only=False  (hook fires)")
    print()

    print("=" * 60)
    for task in TASKS:
        run(llm, task)

    print("=" * 60)
    print("Audit log (read_only primitives never appear here):\n")
    for entry in _AUDIT:
        print(f"  {entry}")
    print()


if __name__ == "__main__":
    main()
