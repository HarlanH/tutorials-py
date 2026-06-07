# Track 24: pydantic model

Define a `BaseModel`, use it as a primitive param and return type, and watch
it appear automatically in the plan prompt under `## Type Definitions`.

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

Product(name: str, price: float, in_stock: bool)

============================================================
Task:   What is the price of SKU 'LAPTOP-01'?
Result: 999.0
Plan:
  product = get_product('LAPTOP-01')
  price = product.price
  return price

Task:   Apply a 15% discount to 'APPLE-01' and show the formatted result.
Result: Apple — $1.02 (in stock)
Plan:
  product = get_product('APPLE-01')
  discounted_product = apply_discount(product, 0.15)
  result = fmt_product(discounted_product)
  return result
```

## What is happening

`Product` is a plain Pydantic `BaseModel`:

```python
class Product(BaseModel):
    name: str
    price: float
    in_stock: bool
```

Because it appears as a param or return type on a `@primitive`, the framework
picks it up and adds it to the plan prompt under `## Type Definitions` — no
extra registration needed.

The plan treats `Product` as a first-class value. It reads fields with dot
notation (`product.price`) and passes the whole object to the next primitive
(`apply_discount(product, 0.15)`). The model moves through the plan the same
way any other variable does.
