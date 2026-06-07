# Track 26: on_mutation

A policy function that runs before every non-read-only primitive. Return `None`
to allow the call. Return a string to block it — that string becomes the error.
Every call is recorded in an audit log; read-only primitives never appear in it.

## Install

```bash
uv add opensymbolicai-core
```

## Running it

```bash
uv run main.py
```

```
============================================================
Primitives and their read_only setting:

  get_account  read_only=True   (hook never fires)
  get_balance  read_only=True   (hook never fires)
  deposit      read_only=False  (hook fires)
  withdraw     read_only=False  (hook fires)

============================================================
Task:   What is the balance of ACC-001?
Result: 1000.0
Plan:
  account = get_account("ACC-001")
  balance = get_balance(account)
  return balance

Task:   Deposit $200 into ACC-001.
Result: id='ACC-001' owner='Alice' balance=1200.0
Plan:
  account = get_account("ACC-001")
  updated_account = deposit(account, 200)
  return updated_account

Task:   Withdraw $800 from ACC-001.
Result: Mutation rejected: $800.00 exceeds the $500 single-transaction limit
Plan:
  account = get_account("ACC-001")
  updated_account = withdraw(account, 800)
  return updated_account

============================================================
Audit log (read_only primitives never appear here):

  ALLOWED  deposit    $  200.00
  BLOCKED  withdraw   $  800.00  $800.00 exceeds the $500 single-transaction limit
```

## What is happening

The hook is a plain function attached via `PlanExecuteConfig`:

```python
_AUDIT: list[str] = []

def policy(ctx: MutationHookContext) -> str | None:
    amount = float(ctx.args.get("amount", ctx.args.get("arg1", 0.0)))
    if ctx.method_name == "withdraw" and amount > 500:
        reason = f"${amount:.2f} exceeds the $500 single-transaction limit"
        _AUDIT.append(f"BLOCKED  {ctx.method_name:<10} ${amount:>8.2f}  {reason}")
        return reason
    _AUDIT.append(f"ALLOWED  {ctx.method_name:<10} ${amount:>8.2f}")
    return None

config = PlanExecuteConfig(on_mutation=policy)
agent = BankAgent(llm=llm, config=config)
```

The hook fires **before** the primitive executes — `ctx.result` is always `None`
inside it. A blocked call never touches the account data.

`ctx.args` holds the arguments from the plan. Keyword arguments appear by name
(`"amount"`); positional arguments appear as `"arg0"`, `"arg1"`, etc. The
fallback `ctx.args.get("arg1")` handles plans that call `withdraw(account, 800)`
without naming the second argument.

Task 1 uses only `get_account` and `get_balance` — both `read_only=True`. The
hook is never called, and nothing appears in the audit log for that task.
