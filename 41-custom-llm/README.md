# Track 41: Custom LLM with a response cache

Subclass `LLM` to connect to any LLM service. Add a cache so repeated
prompts are served from memory instead of making another network call.

No special integration needed. Any agent that accepts an `LLMConfig`
also accepts a custom `LLM` instance — pass one in and the agent uses it.

## The scenario

Three calculator questions are asked twice. The first run calls Ollama.
The second run returns the same answers from cache without any LLM calls.

## 1. Install

```bash
uv add opensymbolicai-core
```

```bash
ollama pull qwen2.5-coder:7b
```

## 2. The custom LLM

Subclass `LLM` and implement one method: `_generate_impl`. The base class
handles retries and cache lookups automatically — `_generate_impl` only
runs when there is a cache miss.

```python
from opensymbolicai.llm import LLM, LLMConfig, LLMResponse, TokenUsage

class MyOllamaLLM(LLM):

    def __init__(self, model: str, cache=None) -> None:
        # LLM base class requires an LLMConfig; we build it internally
        # so callers only need to pass a model name.
        super().__init__(LLMConfig(provider="ollama", model=model), cache=cache)

    def _generate_impl(self, prompt: str, **kwargs) -> LLMResponse:
        payload = json.dumps({
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            **kwargs,
        }).encode()

        request = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request) as resp:
            data = json.loads(resp.read())

        return LLMResponse(
            text=data["response"],
            usage=TokenUsage(
                input_tokens=data.get("prompt_eval_count", 0),
                output_tokens=data.get("eval_count", 0),
            ),
            provider="my-ollama",
            model=self.config.model,
        )
```

## 3. The cache

Subclass `LLMCache` and implement `get`, `set`, `delete`, `clear`.
`InMemoryCache` uses a plain dict and counts hits and misses.

```python
from opensymbolicai.llm import CacheEntry, LLMCache

class InMemoryCache(LLMCache):

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> CacheEntry | None:
        entry = self._store.get(key)
        if entry is not None:
            self._hits += 1
        else:
            self._misses += 1
        return entry

    def set(self, key: str, entry: CacheEntry) -> None:
        self._store[key] = entry

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def clear(self) -> None:
        self._store.clear()
```

Wire the two together and pass the result to any agent:

```python
cache = InMemoryCache()
llm   = MyOllamaLLM(model="qwen2.5-coder:7b", cache=cache)
agent = CalculatorAgent(llm=llm)
```

## 4. Run it

```bash
uv run main.py
```

## Sample output

```
Run 1 (cold cache)
----------------------------------------
Q: What is 12 multiplied by 8?
   Plan   : result = multiply(12, 8)
            return result
   Answer : 96
Q: What is 144 divided by 12?
   Plan   : result = divide(144, 12)
            return result
   Answer : 12.0
Q: What is 50 plus 37?
   Plan   : result = add(50, 37)
            return result
   Answer : 87

Cache — hits: 0  misses: 3

Run 2 (warm cache)
----------------------------------------
Q: What is 12 multiplied by 8?
   Plan   : result = multiply(12, 8)
            return result
   Answer : 96
Q: What is 144 divided by 12?
   Plan   : result = divide(144, 12)
            return result
   Answer : 12.0
Q: What is 50 plus 37?
   Plan   : result = add(50, 37)
            return result
   Answer : 87

Cache — hits: 3  misses: 0
```

## What just happened

Run 1 misses the cache three times — each question goes to Ollama and the
response is stored. Run 2 hits the cache three times — `_generate_impl` is
never called and the answers come back instantly.

The cache key is a SHA-256 hash of the model config and the prompt, so
identical questions always resolve to the same key.

## Takeaway

Two methods define the integration surface:

| What to implement | What you get for free |
|---|---|
| `_generate_impl` | retries, cache lookup/store |
| `LLMCache.get/set/delete/clear` | used automatically by every `LLM` |

Swap `InMemoryCache` for a Redis or SQLite-backed implementation and the
rest of the code stays unchanged.
