"""Bank agent with read-only and mutating primitives.

`get_account` and `get_balance` are read_only=True — the mutation hook
is never called for them. `deposit` and `withdraw` are read_only=False —
every call passes through the hook before executing.
"""

from __future__ import annotations

from pydantic import BaseModel

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Account(BaseModel):
    id: str
    owner: str
    balance: float


_ACCOUNTS: dict[str, Account] = {
    "ACC-001": Account(id="ACC-001", owner="Alice", balance=1000.0),
    "ACC-002": Account(id="ACC-002", owner="Bob", balance=500.0),
}


class BankAgent(PlanExecute):
    """Answers questions about bank accounts and performs transactions."""

    @primitive(read_only=True)
    def get_account(self, account_id: str) -> Account:
        """Return the Account for the given account ID."""
        return _ACCOUNTS[account_id]

    @primitive(read_only=True)
    def get_balance(self, account: Account) -> float:
        """Return the current balance of an account."""
        return account.balance

    @primitive(read_only=False)
    def deposit(self, account: Account, amount: float) -> Account:
        """Deposit amount into account and return the updated Account."""
        updated = Account(id=account.id, owner=account.owner, balance=account.balance + amount)
        _ACCOUNTS[account.id] = updated
        return updated

    @primitive(read_only=False)
    def withdraw(self, account: Account, amount: float) -> Account:
        """Withdraw amount from account and return the updated Account."""
        updated = Account(id=account.id, owner=account.owner, balance=account.balance - amount)
        _ACCOUNTS[account.id] = updated
        return updated
