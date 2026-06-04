# Track 14: Your first decomposition

Until now the planner had two things to go on: your primitive signatures and
their docstrings. You can give it a third: worked examples. A decomposition is a
method you write that composes your primitives into an answer, tagged with the
natural-language query it answers. The planner does not run it. It reads it as a
pattern, an example of how the pieces fit together.

## Install

```bash
uv add opensymbolicai-core pydantic
```

## Two worked examples on the cart

The cart from [Track 9](../09-read-the-trace/) gains one more primitive,
`describe`, which turns a cart and its total into a sentence. Then come the new
part: two methods marked with `@decomposition`, each composing the primitives
into a worked example, one for a multi-item order and one for a single item.

```python
# cart.py
from opensymbolicai.core import decomposition, primitive

class ShoppingCart(PlanExecute):
    # new_cart, add_item, cart_total as before ...

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
```

Each is ordinary Python: a method that calls your primitives through `self` and
returns a sentence. You will never call them yourself, and neither will the
planner. Their job is to be read. The `intent` is the query the example stands
for, and the body is the plan that answers it.

Under the hood the library puts both into the planner's prompt, as a section of
examples. It pulls out each body, drops the `self.` prefixes so it reads like a
plan, and lists them:

```
## Example Decompositions

### Example 1
Intent: how much for 4 bananas at 2 dollars each?
Python:
cart = new_cart()
cart = add_item(cart, 'bananas', 2, 4)
total = cart_total(cart)
text = describe(cart, total)
return text

### Example 2
Intent: what do 2 apples at 3 dollars each and 1 loaf of bread at 2 dollars come to?
Python:
...
```

Take the decompositions out of `cart.py` and this section disappears: it is
there because you wrote it.

## The planner follows the pattern

Now run some orders the examples never mention, each phrased its own way:

```python
# main.py
QUERIES = [
    "ring up 5 oranges at 1 dollar each and 2 yogurts at 3 dollars each",
    "what's the damage on 3 notebooks at 4 dollars each and 2 pens at 1 dollar each?",
    "I'll take 10 eggs at 1 dollar each and 1 cake at 12 dollars",
]

for query in QUERIES:
    result = agent.run(query)
    print(result.plan)
    print(result.result)
```

```
--- intent ---
ring up 5 oranges at 1 dollar each and 2 yogurts at 3 dollars each
--- plan ---
cart = new_cart()
cart = add_item(cart, 'oranges', 1, 5)
cart = add_item(cart, 'yogurts', 3, 2)
total = cart_total(cart)
text = describe(cart, total)
result = text
--- result ---
5 oranges at 1 dollars each and 2 yogurts at 3 dollars each is 11 dollars

--- intent ---
what's the damage on 3 notebooks at 4 dollars each and 2 pens at 1 dollar each?
--- plan ---
cart = new_cart()
cart = add_item(cart, 'notebooks', 4, 3)
cart = add_item(cart, 'pens', 1, 2)
total = cart_total(cart)
text = describe(cart, total)
result = text
--- result ---
3 notebooks at 4 dollars each and 2 pens at 1 dollars each is 14 dollars

--- intent ---
I'll take 10 eggs at 1 dollar each and 1 cake at 12 dollars
--- plan ---
cart = new_cart()
cart = add_item(cart, 'eggs', 1, 10)
cart = add_item(cart, 'cake', 12, 1)
total = cart_total(cart)
text = describe(cart, total)
result = text
--- result ---
10 eggs at 1 dollars each and 1 cake at 12 dollars each is 22 dollars
```

Three different orders, three different phrasings, none of them copied from the
examples, and every plan comes out the same shape: make a cart, add each item,
total it, then describe it. The model learned the pattern from the examples,
right down to ending in a sentence, and applied it to each new order. (The
examples ended with `return text`; the planner drops the return and takes the
last assignment as the result, here aliasing it to `result` on the final line.)

## When a decomposition earns its keep

This cart is simple enough that the planner would manage without the examples. A
decomposition pays off when the right composition is not obvious: a specific
order of calls, a convention your primitives expect, a combination the model
keeps getting wrong. A worked example or two, written once, pins the pattern
down and the planner stops guessing. You teach it the way you would teach a
person: here is a question, and here is how I would answer it.
