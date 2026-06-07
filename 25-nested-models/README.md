# Track 25: nested models

A model that holds another model. Both appear under `## Type Definitions`.
Plans read nested fields with dot notation and work with `list[Recipe]`
returned from a search primitive.

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
## Type Definitions seen by the LLM

## Type Definitions

Nutrition(calories: int, protein_g: float, carbs_g: float)
Recipe(title: str, servings: int, nutrition: Nutrition)

============================================================
Task:   How many calories are in a serving of oatmeal?
Result: 150
Plan:
  oatmeal_recipe = get_recipe("Oatmeal")
  nutrition_data = get_nutrition(oatmeal_recipe)
  calories_per_serving = nutrition_data.calories
  return calories_per_serving

Task:   Scale the pasta recipe to 4 servings and return the formatted result.
Result: Pasta Bolognese (8 serving(s)) — 1920 kcal, 88.0g protein, 260.0g carbs
Plan:
  pasta_recipe = get_recipe("Pasta")
  scaled_recipe = scale_servings(pasta_recipe, 4)
  formatted_recipe = fmt_recipe(scaled_recipe)
  return formatted_recipe

Task:   Which recipe has the highest protein per serving?
Result: title='Chicken Salad' servings=1 nutrition=Nutrition(calories=320, protein_g=35.0, carbs_g=12.0)
Plan:
  highest_protein_recipe = highest_protein(search_recipes(""))
  return highest_protein_recipe
```

## What is happening

Two models are defined — `Nutrition` is nested inside `Recipe`:

```python
class Nutrition(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float

class Recipe(BaseModel):
    title: str
    servings: int
    nutrition: Nutrition
```

Because `Nutrition` appears as a primitive return type (`get_nutrition`),
and `Recipe` appears in several primitives, both are listed under
`## Type Definitions`. The LLM sees the full shape of each model before
it writes a single line of plan.

The plan accesses nested fields with standard dot notation
(`nutrition_data.calories`), passes whole models between primitives
(`scale_servings(pasta_recipe, 4)`), and works with `list[Recipe]`
from `search_recipes` just as naturally as a scalar.
