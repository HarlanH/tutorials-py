# Track 45: Coding agent

An agent that reads a Python file, rewrites it according to an instruction,
saves it in place, and runs it to confirm the output is unchanged.

Three recursive programs are converted to iterative: Fibonacci, factorial,
and binary search.

## The scenario

Each program in `programs/` is a working recursive implementation. The agent:

1. Reads the source
2. Asks the LLM to produce an iterative version
3. Writes the new version back to the same file
4. Runs it and returns stdout

`main.py` captures the file before and after, computes a unified diff, and
prints it alongside the run output.

## 1. Install

```bash
uv add opensymbolicai-core
```

```bash
ollama pull qwen2.5-coder:7b
```

## 2. The agent

Four primitives: read, rewrite, write, run.

```python
class CodingAgent(PlanExecute):

    @primitive(read_only=True)
    def read_file(self, path: str) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()

    @primitive(read_only=True)
    def rewrite(self, source: str, instruction: str) -> str:
        prompt = f"{instruction}\n\nReturn ONLY the new Python source code.\n\n{source}"
        return self._llm.generate(prompt).text.strip()

    @primitive(read_only=False)
    def write_file(self, path: str, content: str) -> str:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"wrote {path}"

    @primitive(read_only=True)
    def run_code(self, path: str) -> str:
        result = subprocess.run([sys.executable, path], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else f"ERROR:\n{result.stderr}"
```

The generated plan is the same shape for every task:

```python
source     = read_file("programs/fib.py")
updated    = rewrite(source, "Convert the recursive function to iterative...")
write_result = write_file("programs/fib.py", updated)
output     = run_code("programs/fib.py")
return respond(output)
```

## 3. Run it

```bash
uv run main.py
```

## Sample output

```
Model: qwen2.5-coder:7b
============================================================

programs/fib.py
----------------------------------------
Diff:
--- a/programs/fib.py
+++ b/programs/fib.py
@@ -1,5 +1,8 @@
 def fib(n):
     if n <= 1:
         return n
-    return fib(n - 1) + fib(n - 2)
+    a, b = 0, 1
+    for _ in range(2, n + 1):
+        a, b = b, a + b
+    return b

Output (8.8s):
  0 1 1 2 3 5 8 13 21 34

programs/factorial.py
----------------------------------------
Diff:
--- a/programs/factorial.py
+++ b/programs/factorial.py
@@ -1,5 +1,5 @@
 def factorial(n):
-    if n == 0:
-        return 1
-    return n * factorial(n - 1)
+    result = 1
+    for i in range(2, n + 1):
+        result *= i
+    return result

Output (3.9s):
  0! = 1
  1! = 1
  2! = 2
  3! = 6
  4! = 24
  5! = 120
  6! = 720
  7! = 5040

programs/binary_search.py
----------------------------------------
Diff:
--- a/programs/binary_search.py
+++ b/programs/binary_search.py
@@ -1,13 +1,13 @@
-def binary_search(arr, target, low=0, high=None):
-    if high is None:
-        high = len(arr) - 1
-    if low > high:
-        return -1
-    mid = (low + high) // 2
-    if arr[mid] == target:
-        return mid
-    elif arr[mid] < target:
-        return binary_search(arr, target, mid + 1, high)
-    else:
-        return binary_search(arr, target, low, mid - 1)
+def binary_search(arr, target):
+    low, high = 0, len(arr) - 1
+    while low <= high:
+        mid = (low + high) // 2
+        if arr[mid] == target:
+            return mid
+        elif arr[mid] < target:
+            low = mid + 1
+        else:
+            high = mid - 1
+    return -1

Output (6.0s):
  Array: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
  Search 6: index 3
  Search 7: index -1
  Search 14: index 7
```

## What just happened

The LLM rewrites each function without seeing the diff format. `main.py`
reads the file before and after the agent runs, then calls
`difflib.unified_diff` to produce the display. The diff is a record of
what changed, not the mechanism of change.

`run_code` executes the rewritten file with the same Python interpreter
running `main.py`, so the validation uses no mocks or test harness. If
the output matches what the original program printed, the conversion worked.

## Takeaway

`read_only=False` on `write_file` marks it as a mutating primitive. The
agent reads, transforms, and writes in a single plan. Running the result
closes the loop: the agent sees its own output and the plan can use it as
the final response.

The same four primitives work for any source-level transformation: add
type hints, rename a function, convert a class to dataclass, or translate
between languages.
