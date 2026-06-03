"""A small shopping-cart agent.

Three primitives that build a cart up and total it. Each one returns a value,
so a plan that uses them reads as a sequence of individual statements: make a
cart, add an item, add another, then total it. That sequence is what makes the
execution trace worth reading.
"""

from __future__ import annotations

from pydantic import BaseModel

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Item(BaseModel):
    """One line in the cart: a unit price and how many of it."""

    price: float
    quantity: int


class Cart(BaseModel):
    """A shopping cart: items keyed by name."""

    items: dict[str, Item] = {}


class ShoppingCart(PlanExecute):
    """A cart you can add items to and total up."""

    @primitive(read_only=True)
    def new_cart(self) -> Cart:
        """Make a new, empty shopping cart."""
        return Cart()

    @primitive(read_only=True)
    def add_item(self, cart: Cart, name: str, price: float, quantity: int) -> Cart:
        """Add an item to the cart with its unit price and quantity.

        Returns a new cart with the item added under its name.
        """
        return Cart(items={**cart.items, name: Item(price=price, quantity=quantity)})

    @primitive(read_only=True)
    def cart_total(self, cart: Cart) -> float:
        """Total the cart: sum price times quantity for every item."""
        return sum(item.price * item.quantity for item in cart.items.values())
