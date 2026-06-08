# Track 32: Multi-turn shopping cart

Every previous track runs a single task: call `agent.run()` once and read the
result. This track calls `agent.run()` four times in a row, and the cart
accumulates across all four turns.

## Install

```bash
uv add opensymbolicai-core pydantic
```

## The agent

`cart.py` has four primitives: `add_item`, `remove_item`, `cart_total`, and
`list_items`. There is no `new_cart` primitive. The cart is a hidden instance
variable created when the agent is instantiated:

```python
class ShoppingCart(PlanExecute):
    def __init__(self, llm, config=None):
        super().__init__(llm=llm, config=config)
        self._cart = Cart()
```

The primitives operate on `self._cart` directly. The model never sees the cart
object and never has to create or pass it around:

```python
@primitive(read_only=False)
def add_item(self, name: str, price: float, quantity: int) -> str:
    self._cart = Cart(items={**self._cart.items, name: Item(price=price, quantity=quantity)})
    return f"added {name}"

@primitive(read_only=True)
def cart_total(self) -> float:
    return sum(item.price * item.quantity for item in self._cart.items.values())
```

`add_item` and `remove_item` are `read_only=False` because they mutate state.
`cart_total` and `list_items` are `read_only=True`.

## Multi-turn config

```python
config = PlanExecuteConfig(multi_turn=True)
agent = ShoppingCart(llm=llm, config=config)
```

With `multi_turn=True`, the model receives the full conversation history in its
prompt on each turn, so it knows what was done in previous turns. The cart
itself persists simply because `self._cart` lives on the agent object.

## Run it

```bash
uv run main.py
```

```
--- Add to the cart: milk at $2.50, eggs at $3.99, bread at $4.50, ...
plan:
  r1 = add_item('milk', 2.50, 1)
  r2 = add_item('eggs', 3.99, 1)
  r3 = add_item('bread', 4.50, 1)
  r4 = add_item('butter', 5.99, 1)
  r5 = add_item('yogurt', 1.99, 1)
  r6 = add_item('cheese', 6.50, 1)
  return r1 + ', ' + r2 + ', ' + r3 + ', ' + r4 + ', ' + r5 + ', ' + r6
result: added milk, added eggs, added bread, added butter, added yogurt, added cheese

--- Add to the cart: chicken at $8.99, pasta at $2.25, tomatoes at $3.50, ...
plan:
  r1 = add_item('chicken', 8.99, 1)
  r2 = add_item('pasta', 2.25, 1)
  r3 = add_item('tomatoes', 3.50, 1)
  r4 = add_item('garlic', 1.50, 1)
  r5 = add_item('olive oil', 7.99, 1)
  r6 = add_item('onions', 1.25, 1)
  return r1 + ', ' + r2 + ', ' + r3 + ', ' + r4 + ', ' + r5 + ', ' + r6
result: added chicken, added pasta, added tomatoes, added garlic, added olive oil, added onions

--- Remove eggs and butter from the cart.
plan:
  r1 = remove_item('eggs')
  r2 = remove_item('butter')
  return r1 + ', ' + r2
result: removed eggs, removed butter

--- What is the total?
plan:
  total = cart_total()
  return total
result: 40.97
```

The plans have no `cart` variable. Each primitive just does its job and returns
a string or a number. The cart persists as `self._cart` on the agent object,
invisible to the model.
