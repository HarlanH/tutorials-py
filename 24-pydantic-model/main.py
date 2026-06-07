"""Show how a Pydantic BaseModel appears in the plan prompt and flows between primitives.

Prints the ## Type Definitions section first so you can see how Product is
described to the LLM, then runs two tasks that pass Product between primitives.

Usage:
    uv run main.py
"""

from __future__ import annotations

from store import StoreAgent
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

TASKS = [
    "What is the price of SKU 'LAPTOP-01'?",
    "Apply a 15% discount to 'APPLE-01' and show the formatted result.",
]


def print_type_definitions(agent: StoreAgent, task: str) -> None:
    prompt = agent.build_plan_prompt(task)
    in_section = False
    for line in prompt.splitlines():
        if "## Type Definitions" in line:
            in_section = True
        elif line.startswith("##") and in_section:
            break
        if in_section:
            print(line)


def run(llm: LLMConfig, task: str) -> None:
    agent = StoreAgent(llm=llm)
    result = agent.run(task)
    print(f"Task:   {task}")
    print(f"Result: {result.result}")
    print(f"Plan:")
    for line in result.plan.splitlines():
        print(f"  {line}")
    print()


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    print("=" * 60)
    print("## Type Definitions seen by the LLM\n")
    print_type_definitions(StoreAgent(llm=llm), TASKS[0])

    print("=" * 60)
    for task in TASKS:
        run(llm, task)


if __name__ == "__main__":
    main()
