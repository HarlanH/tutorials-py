# Track 34: Symbolic calculus with SymPy

SymPy differentiates, integrates, and simplifies expressions symbolically,
returning exact answers rather than numeric approximations.

The task:

> What is the derivative of x cubed plus 2x squared minus 5?

The LLM picks the right operation. SymPy returns the exact answer.

## 1. Install

```bash
uv add opensymbolicai-core sympy
```

## 2. The agent

Three primitives: differentiate, integrate, simplify.

```python
# calculus.py
import sympy
from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class CalculusAgent(PlanExecute):

    @primitive(read_only=True)
    def differentiate(self, expr: str, variable: str) -> str:
        """Differentiate expr with respect to variable and return the result as a string.

        Example: differentiate("x**3 + 2*x**2 - 5", "x") -> "3*x**2 + 4*x"
        """
        x = sympy.Symbol(variable)
        return str(sympy.diff(sympy.sympify(expr), x))

    @primitive(read_only=True)
    def integrate(self, expr: str, variable: str) -> str:
        """Integrate expr with respect to variable and return the result as a string.

        Example: integrate("3*x**2 + 4*x", "x") -> "x**3 + 2*x**2"
        """
        x = sympy.Symbol(variable)
        return str(sympy.integrate(sympy.sympify(expr), x))

    @primitive(read_only=True)
    def simplify(self, expr: str) -> str:
        """Simplify expr and return the result as a string.

        Example: simplify("sin(x)**2 + cos(x)**2") -> "1"
        """
        return str(sympy.simplify(sympy.sympify(expr)))
```

## 3. Run it

```python
# main.py
from calculus import CalculusAgent
from opensymbolicai.llm import LLMConfig

llm = LLMConfig(provider="ollama", model="qwen2.5-coder:7b")
agent = CalculusAgent(llm=llm)

result = agent.run("what is the derivative of x cubed plus 2 x squared minus 5")
print(result.result)  # 3*x**2 + 4*x
```

```bash
uv run main.py
```

The plan the LLM writes looks roughly like this:

```python
result = differentiate("x**3 + 2*x**2 - 5", "x")
```

## What just happened

The LLM read "x cubed plus 2x squared minus 5" and turned it into SymPy's
expression syntax. SymPy applied the power rule symbolically and returned
`3*x**2 + 4*x`. The answer is exact, not a floating-point approximation.

Try asking for an integral instead:

```python
result = agent.run("integrate 3 x squared plus 4 x with respect to x")
print(result.result)  # x**3 + 2*x**2
```

Or a simplification:

```python
result = agent.run("simplify sin squared x plus cos squared x")
print(result.result)  # 1
```

The same three primitives handle all three, because the LLM picks which one fits.

## Takeaway

SymPy returns exact symbolic answers: derivatives, integrals, simplifications.
The LLM picks which operation fits the question; SymPy does the math.
