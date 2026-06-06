# Track 16: build_plan_prompt

Every `run()` call starts by building a prompt and sending it to the LLM.
`build_plan_prompt(task)` returns that prompt as a plain string, without calling
the LLM. This track reads it.

## Install

```bash
uv add opensymbolicai-core
```

## Three sections

The prompt is divided into three labeled sections.

**DEFINITIONS** lists every primitive the model is allowed to call, plus any
decomposition examples it can follow. This is the stable part: it changes only
when you add or remove primitives or decompositions.

**CONTEXT** contains the task. It is the part that varies per call.

**INSTRUCTIONS** explains the output format: assignment statements, a final
`return`, no imports or control flow.

## Reading it

`main.py` calls `build_plan_prompt` and replaces the section markers with
labeled dividers:

```python
prompt = agent.build_plan_prompt("what is 7 times 8 minus 3?")
print(annotate(prompt))
```

`build_plan_prompt` never calls the LLM, so Ollama does not need to be running.
Run it with:

```bash
uv run main.py
```

Output:

```
You are Calculator, an AI agent that generates Python code plans.

A tiny calculator agent.

# --- DEFINITIONS START ---

## Available Primitive Methods

You can ONLY call these methods:

```python
add(a: float, b: float) -> float
    """Add two numbers."""
multiply(a: float, b: float) -> float
    """Multiply two numbers."""
subtract(a: float, b: float) -> float
    """Subtract b from a."""
```

## Example Decompositions

Here are examples of how to compose primitives:

### Example 1
Intent: what is 2 plus 3?
Python:
result = add(2, 3)
return result

# --- DEFINITIONS END ---

# --- CONTEXT START ---
## Task

Generate Python code to accomplish this task: what is 7 times 8 minus 3?

# --- CONTEXT END ---

# --- INSTRUCTIONS START ---

## Rules

1. Output Python assignment statements, then a final `return` statement
2. Each intermediate statement must assign a result to a variable
3. You can ONLY call the primitive methods listed above
4. Do NOT use imports, loops, conditionals, or function definitions
5. Do NOT use any dangerous operations (exec, eval, open, etc.)
6. Call primitives directly (e.g. `add(a=1, b=2)`), do NOT use `self.`
7. The plan MUST end with `return <expr>` (e.g. `return total`) to specify the final result

## Output

```python

# --- INSTRUCTIONS END ---
```

## What lands where

The Calculator has three primitives and one decomposition. Here is where each
part ends up in the prompt:

- `add`, `multiply`, `subtract` appear under **Available Primitive Methods** in
  DEFINITIONS. The model sees their signatures and docstrings.
- The `@decomposition(intent="what is 2 plus 3?")` method appears under
  **Example Decompositions** in DEFINITIONS. Its body (`result = add(2, 3)`)
  is extracted and shown with `self.` stripped, so it reads as a bare call.
- The task string `"what is 7 times 8 minus 3?"` lands in CONTEXT.
- INSTRUCTIONS is fixed: it does not vary by agent or task.

## Adding a primitive changes the prompt

Add a `divide` primitive to `Calculator` and run again. The DEFINITIONS section
grows by one entry. The CONTEXT and INSTRUCTIONS sections do not change. This is
how the model learns what it can call.

## Out of scope

Filtering which primitives and decompositions appear in the prompt (`PromptProvider`)
is Track 46. Splitting the prompt string into its sections programmatically is
Track 47.
