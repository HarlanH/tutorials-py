"""Demonstrate max_total_primitive_calls and allow_break_continue.

max_total_primitive_calls is a whole-plan circuit breaker: it counts every
primitive call across the entire execution, regardless of how they arise. It
complements the per-loop max_loop_iterations from Track 18.

allow_break_continue controls whether break and continue are legal in plans.
When False, validate_plan raises ValueError if the LLM writes either keyword.

Usage:
    uv run main.py
"""

from __future__ import annotations

from cart import Cart

from opensymbolicai.llm import LLMConfig
from opensymbolicai.models import DesignExecuteConfig

# Five items, each iteration calls item_total + add. Plus format_total at end.
# Total primitive calls: 5 * 2 + 1 = 11.
LOOP_PLAN = """\
total = 0.0
items = [('pen', 2), ('notebook', 3), ('stapler', 1), ('apple', 4), ('book', 2)]
for name, qty in items:
    line = item_total(name, qty)
    total = add(total, line)
return format_total(total)
"""

# Accumulate items until running total exceeds $10, then stop.
BREAK_PLAN = """\
total = 0.0
items = [('stapler', 1), ('pen', 2), ('notebook', 3)]
for name, qty in items:
    line = item_total(name, qty)
    total = add(total, line)
    if total > 10:
        break
return format_total(total)
"""


def demo_max_calls() -> None:
    print("=== max_total_primitive_calls ===")
    llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")

    # Limit of 3: trips on the 4th primitive call.
    config = DesignExecuteConfig(max_total_primitive_calls=3)
    agent = Cart(llm=llm, config=config)
    result = agent.execute(LOOP_PLAN)
    last = result.trace.steps[-1]
    print(f"limit=3, calls made before stop: {len(result.trace.steps)}")
    print(f"error: {last.error}")
    print()

    # Limit of 15: all 11 calls fit.
    config = DesignExecuteConfig(max_total_primitive_calls=15)
    agent = Cart(llm=llm, config=config)
    result = agent.execute(LOOP_PLAN)
    print(f"limit=15, calls made: {len(result.trace.steps)}")
    print(f"result: {result.get_value()}")
    print()


def demo_break_continue() -> None:
    print("=== allow_break_continue ===")
    llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")

    # True (default): break is allowed; loop stops early once total > $10.
    config = DesignExecuteConfig(allow_break_continue=True)
    agent = Cart(llm=llm, config=config)
    result = agent.execute(BREAK_PLAN)
    print(f"allow_break_continue=True, calls made: {len(result.trace.steps)}")
    print(f"result: {result.get_value()}")
    print()

    # False: validate_plan rejects the plan before execution.
    config = DesignExecuteConfig(allow_break_continue=False)
    agent = Cart(llm=llm, config=config)
    try:
        agent.validate_plan(BREAK_PLAN)
    except ValueError as e:
        print(f"allow_break_continue=False: {e}")
    print()


def main() -> None:
    demo_max_calls()
    demo_break_continue()


if __name__ == "__main__":
    main()
