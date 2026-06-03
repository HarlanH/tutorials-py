# Track 9: Read the execution trace

The previous track, [Track 8](../08-read-the-plan/), read `result.plan`: the
code the LLM wrote, before any of it ran. This track reads `result.trace`, that
same code after it ran. Each line of the plan becomes a step, and each step
keeps a record: the statement it executed, the value that statement produced,
and the namespace just before and just after. Read it and you watch the work
happen one line at a time.

A calculator folds its math into a single nested expression, which makes for a
short, dull trace. So this track uses a shopping cart instead. Building a cart
is a sequence of distinct steps, make it, add an item, add another, total it,
and the trace gets one step for each.

## Install

```bash
uv add opensymbolicai-core pydantic
```

## A small shopping-cart agent

Three primitives. `new_cart` starts an empty cart, `add_item` puts something in
it and hands back the updated cart, and `cart_total` works out what you owe.
Both the cart and the items in it are Pydantic objects: an `Item` holds a unit
price and a quantity, and a `Cart` holds its items keyed by name. `cart_total`
sums price times quantity across the items.

```python
# cart.py
from pydantic import BaseModel

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


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
```

## Walk the trace

Ask for a few items, then print the plan and walk `result.trace.steps`.

```python
# main.py
from cart import ShoppingCart
from opensymbolicai.llm import LLMConfig

QUERY = (
    "add 2 apples at 3 dollars each, 2 loaves of bread at 2 dollars each, "
    "and 3 cartons of milk at 4 dollars each, then total it up"
)

agent = ShoppingCart(llm=LLMConfig(provider="ollama", model="qwen2.5-coder:7b"))
result = agent.run(QUERY)

print(result.task)  # the intent: the query, echoed back on the result
print(result.plan)  # the whole program, as a string

for step in result.trace.steps:
    print(step.step_number, step.statement)
    print("  before:", step.namespace_before)
    print("  value: ", step.result_value)
    print("  after: ", step.namespace_after)

print("all succeeded:", result.trace.all_succeeded)
```

```bash
uv run main.py
```

Ollama is local, so there's no API key. Pull the model once with
`ollama pull qwen2.5-coder:7b`.

```
--- intent ---
add 2 apples at 3 dollars each, 2 loaves of bread at 2 dollars each, and 3 cartons of milk at 4 dollars each, then total it up

--- plan ---
cart = new_cart()
cart = add_item(cart, "apples", 3.0, 2)
cart = add_item(cart, "bread", 2.0, 2)
cart = add_item(cart, "milk", 4.0, 3)
total = cart_total(cart)

--- trace ---
step 1: cart = new_cart()
  namespace before: {}
  value:            items={}
  namespace after:  {'cart': Cart(items={})}

step 2: cart = add_item(cart, 'apples', 3.0, 2)
  namespace before: {'cart': Cart(items={})}
  value:            items={'apples': Item(price=3.0, quantity=2)}
  namespace after:  {'cart': Cart(items={'apples': Item(price=3.0, quantity=2)})}

step 3: cart = add_item(cart, 'bread', 2.0, 2)
  namespace before: {'cart': Cart(items={'apples': Item(price=3.0, quantity=2)})}
  value:            items={'apples': Item(price=3.0, quantity=2), 'bread': Item(price=2.0, quantity=2)}
  namespace after:  {'cart': Cart(items={'apples': Item(price=3.0, quantity=2), 'bread': Item(price=2.0, quantity=2)})}

step 4: cart = add_item(cart, 'milk', 4.0, 3)
  namespace before: {'cart': Cart(items={'apples': Item(price=3.0, quantity=2), 'bread': Item(price=2.0, quantity=2)})}
  value:            items={'apples': Item(price=3.0, quantity=2), 'bread': Item(price=2.0, quantity=2), 'milk': Item(price=4.0, quantity=3)}
  namespace after:  {'cart': Cart(items={'apples': Item(price=3.0, quantity=2), 'bread': Item(price=2.0, quantity=2), 'milk': Item(price=4.0, quantity=3)})}

step 5: total = cart_total(cart)
  namespace before: {'cart': Cart(items={'apples': Item(price=3.0, quantity=2), 'bread': Item(price=2.0, quantity=2), 'milk': Item(price=4.0, quantity=3)})}
  value:            22.0
  namespace after:  {'cart': Cart(items={'apples': Item(price=3.0, quantity=2), 'bread': Item(price=2.0, quantity=2), 'milk': Item(price=4.0, quantity=3)}), 'total': 22.0}

every step succeeded: True
failed steps: []
```

## What you're looking at

Five lines in the plan, five steps in the trace, one per line. Read down the
value column and you can watch the cart get built: an empty `Cart`, then one
`Item` inside it, then two, then three, then the total, `22.0`.

The namespace is where it clicks. It starts empty. Step 2 opens with the empty
cart from step 1, adds apples, and leaves
`Cart(items={'apples': Item(price=3.0, quantity=2)})` behind. Step 3 picks up
exactly that, adds bread, and passes the two-item cart to step 4. Each step's
cart is sitting right there in the next step's `before`. That is `add_item`
working through the namespace: it takes the cart it was handed, returns a bigger
one, and the next step runs on the new value.

Step 5 is where `cart_total` earns its keep. The cart never carried a running
total; it carried items. Only at the end does `cart_total` walk those items and
multiply price by quantity: 6 + 4 + 12, landing on `22.0`. That arithmetic
happened in your primitive, in plain Python. None of it went back to the model.
The cart was assembled here, item by item, and the trace is the receipt.

The model picks the variable names. Here it kept reassigning `cart` and called
the total `total`; another run might name them differently, or write a price as
`3.0` instead of `3`. The steps and the values come out the same.

## Did every line run

`trace.all_succeeded` is the quick health check: `True` means every step ran
without raising. When a step does go wrong, `trace.failed_steps` hands you just
the ones that failed, each with its own `error`, so you don't scan the whole
list to find it. Here nothing failed, so `failed_steps` is empty.

## What else is on a step

A step carries more than the four fields above: the primitive it called, the
arguments with both the expression and the value they resolved to, how long it
took, the type of the result. The trace sits next to `result.metrics` on the
same result object. This track stays on the trace and the namespace.
