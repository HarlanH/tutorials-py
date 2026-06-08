"""A shopping cart agent for multi-turn conversations."""

from __future__ import annotations

from pydantic import BaseModel

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive
from opensymbolicai.llm import LLMConfig
from opensymbolicai.models import PlanExecuteConfig


class Item(BaseModel):
    price: float
    quantity: int


class Cart(BaseModel):
    items: dict[str, Item] = {}


class ShoppingCart(PlanExecute):
    """A shopping cart. Use add_item, remove_item, cart_total, and list_items.
    The cart persists across all turns automatically.
    """

    def __init__(
        self,
        llm: LLMConfig,
        config: PlanExecuteConfig | None = None,
    ) -> None:
        super().__init__(llm=llm, config=config)
        self._cart = Cart()

    @primitive(read_only=False)
    def add_item(self, name: str, price: float, quantity: int) -> str:
        """Add an item to the cart by name, unit price, and quantity."""
        self._cart = Cart(items={**self._cart.items, name: Item(price=price, quantity=quantity)})
        return f"added {name}"

    @primitive(read_only=False)
    def remove_item(self, name: str) -> str:
        """Remove an item from the cart by name."""
        self._cart = Cart(items={k: v for k, v in self._cart.items.items() if k != name})
        return f"removed {name}"

    @primitive(read_only=True)
    def cart_total(self) -> float:
        """Return the total cost of all items in the cart."""
        return sum(item.price * item.quantity for item in self._cart.items.values())

    @primitive(read_only=True)
    def list_items(self) -> list[str]:
        """Return the names of all items currently in the cart."""
        return list(self._cart.items.keys())

    # --- decomposition examples ---

    @decomposition(intent="add notebook at $8 and pen at $3")
    def _example_add(self) -> str:
        r1 = self.add_item("notebook", 8.0, 1)
        r2 = self.add_item("pen", 3.0, 1)
        return r1 + ", " + r2

    @decomposition(intent="remove notebook")
    def _example_remove(self) -> str:
        r = self.remove_item("notebook")
        return r

    @decomposition(intent="what is the total")
    def _example_total(self) -> float:
        total = self.cart_total()
        return total
