"""The shopping cart, now with a worked example for the planner.

The three primitives are unchanged. What is new is the `@decomposition` method:
a worked example that shows how to compose those primitives to fill a cart and
total it. The planner never runs this method. It reads it as an example of the
pattern, tagged with the natural-language intent it answers.
"""

from __future__ import annotations

from pydantic import BaseModel

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive


class Item(BaseModel):
    price: float
    quantity: int


class Cart(BaseModel):
    items: dict[str, Item] = {}


class ShoppingCart(PlanExecute):
    @primitive(read_only=True)
    def new_cart(self) -> Cart:
        """Make a new, empty shopping cart."""
        return Cart()

    @primitive(read_only=True)
    def add_item(self, cart: Cart, name: str, price: float, quantity: int) -> Cart:
        """Add an item to the cart with its unit price and quantity."""
        return Cart(items={**cart.items, name: Item(price=price, quantity=quantity)})

    @primitive(read_only=True)
    def cart_total(self, cart: Cart) -> float:
        """Total the cart: sum price times quantity for every item."""
        return sum(item.price * item.quantity for item in cart.items.values())

    @primitive(read_only=True)
    def describe(self, cart: Cart, total: float) -> str:
        """Describe the cart's items and what they come to, as a sentence."""
        parts = [
            f"{item.quantity} {name} at {item.price:g} dollars each"
            for name, item in cart.items.items()
        ]
        return f"{' and '.join(parts)} is {total:g} dollars"

    @decomposition(
        intent="what do 2 apples at 3 dollars each and 1 loaf of bread at 2 dollars come to?"
    )
    def _example_small_order(self) -> str:
        cart = self.new_cart()
        cart = self.add_item(cart, "apples", 3, 2)
        cart = self.add_item(cart, "bread", 2, 1)
        total = self.cart_total(cart)
        text = self.describe(cart, total)
        return text

    @decomposition(intent="how much for 4 bananas at 2 dollars each?")
    def _example_single_item(self) -> str:
        cart = self.new_cart()
        cart = self.add_item(cart, "bananas", 2, 4)
        total = self.cart_total(cart)
        text = self.describe(cart, total)
        return text
