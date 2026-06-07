"""A small product store agent that passes Pydantic models between primitives.

Defining a BaseModel as a primitive param or return type causes it to appear
automatically under ## Type Definitions in the plan prompt. The plan can then
construct, read, and pass the model without any extra wiring.
"""

from __future__ import annotations

from pydantic import BaseModel

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Product(BaseModel):
    name: str
    price: float
    in_stock: bool


_INVENTORY: dict[str, Product] = {
    "APPLE-01": Product(name="Apple",      price=1.20,   in_stock=True),
    "LAPTOP-01": Product(name="Laptop Pro", price=999.00, in_stock=True),
    "CABLE-05":  Product(name="USB-C Cable", price=12.50, in_stock=False),
}


class StoreAgent(PlanExecute):
    """Answers questions about a small product catalogue."""

    @primitive(read_only=True)
    def get_product(self, sku: str) -> Product:
        """Return the Product for a given SKU."""
        return _INVENTORY[sku]

    @primitive(read_only=True)
    def apply_discount(self, product: Product, pct: float) -> Product:
        """Return a new Product with price reduced by pct (0.0–1.0)."""
        return Product(
            name=product.name,
            price=round(product.price * (1 - pct), 2),
            in_stock=product.in_stock,
        )

    @primitive(read_only=True)
    def is_available(self, product: Product) -> bool:
        """Return True if the product is in stock."""
        return product.in_stock

    @primitive(read_only=True)
    def fmt_product(self, product: Product) -> str:
        """Format a product as a human-readable string."""
        stock = "in stock" if product.in_stock else "out of stock"
        return f"{product.name} — ${product.price:.2f} ({stock})"
