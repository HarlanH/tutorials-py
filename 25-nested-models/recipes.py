"""A recipe agent that shows nested models and list[Model] in primitives.

Both Nutrition and Recipe appear under ## Type Definitions automatically.
Plans read nested fields (recipe.nutrition.calories) and work with
list[Recipe] returned from search.
"""

from __future__ import annotations

from pydantic import BaseModel

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Nutrition(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float


class Recipe(BaseModel):
    title: str
    servings: int
    nutrition: Nutrition


_RECIPES: dict[str, Recipe] = {
    "oatmeal": Recipe(
        title="Oatmeal",
        servings=1,
        nutrition=Nutrition(calories=150, protein_g=5.0, carbs_g=27.0),
    ),
    "pasta": Recipe(
        title="Pasta Bolognese",
        servings=2,
        nutrition=Nutrition(calories=480, protein_g=22.0, carbs_g=65.0),
    ),
    "chicken salad": Recipe(
        title="Chicken Salad",
        servings=1,
        nutrition=Nutrition(calories=320, protein_g=35.0, carbs_g=12.0),
    ),
    "egg scramble": Recipe(
        title="Egg Scramble",
        servings=1,
        nutrition=Nutrition(calories=280, protein_g=20.0, carbs_g=3.0),
    ),
}


class RecipeAgent(PlanExecute):
    """Answers questions about a recipe collection."""

    @primitive(read_only=True)
    def get_recipe(self, name: str) -> Recipe:
        """Return the Recipe for a given name (case-insensitive)."""
        return _RECIPES[name.lower()]

    @primitive(read_only=True)
    def scale_servings(self, recipe: Recipe, factor: float) -> Recipe:
        """Return a new Recipe scaled to factor × the original serving count."""
        n = recipe.nutrition
        return Recipe(
            title=recipe.title,
            servings=round(recipe.servings * factor),
            nutrition=Nutrition(
                calories=round(n.calories * factor),
                protein_g=round(n.protein_g * factor, 1),
                carbs_g=round(n.carbs_g * factor, 1),
            ),
        )

    @primitive(read_only=True)
    def get_nutrition(self, recipe: Recipe) -> Nutrition:
        """Return the Nutrition data for a recipe."""
        return recipe.nutrition

    @primitive(read_only=True)
    def search_recipes(self, keyword: str) -> list[Recipe]:
        """Return all recipes whose title contains keyword (case-insensitive)."""
        kw = keyword.lower()
        return [r for r in _RECIPES.values() if kw in r.title.lower()]

    @primitive(read_only=True)
    def highest_protein(self, recipes: list[Recipe]) -> Recipe:
        """Return the Recipe with the most protein per serving."""
        return max(recipes, key=lambda r: r.nutrition.protein_g)

    @primitive(read_only=True)
    def fmt_recipe(self, recipe: Recipe) -> str:
        """Format a recipe as a human-readable string."""
        n = recipe.nutrition
        return (
            f"{recipe.title} ({recipe.servings} serving(s)) — "
            f"{n.calories} kcal, {n.protein_g}g protein, {n.carbs_g}g carbs"
        )
