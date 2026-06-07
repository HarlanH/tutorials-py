"""Show nested Pydantic models and list[Model] as primitive types.

Prints the ## Type Definitions section first — both Nutrition and Recipe
appear, showing the nesting. Then runs three tasks that access nested
fields and work with lists of models.

Usage:
    uv run main.py
"""

from __future__ import annotations

from recipes import RecipeAgent
from ollama import check_ollama

from opensymbolicai.llm import LLMConfig

TASKS = [
    "How many calories are in a serving of oatmeal?",
    "Scale the pasta recipe to 4 servings and return the formatted result.",
    "Which recipe has the highest protein per serving?",
]


def print_type_definitions(agent: RecipeAgent, task: str) -> None:
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
    agent = RecipeAgent(llm=llm)
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
    print_type_definitions(RecipeAgent(llm=llm), TASKS[0])

    print("=" * 60)
    for task in TASKS:
        run(llm, task)


if __name__ == "__main__":
    main()
