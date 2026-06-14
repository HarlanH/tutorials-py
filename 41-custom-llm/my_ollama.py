"""Custom Ollama LLM with an in-memory cache.

Two classes:

  InMemoryCache  — stores LLM responses in a plain dict.
                   Tracks hits and misses so you can see the cache working.

  MyOllamaLLM   — subclasses LLM and wires the cache in.
                   The base class checks the cache before calling _generate_impl,
                   so _generate_impl only runs on a cache miss.
"""

from __future__ import annotations

import json
import urllib.request

from opensymbolicai.llm import (
    CacheEntry,
    LLM,
    LLMCache,
    LLMConfig,
    LLMResponse,
    TokenUsage,
)

OLLAMA_URL = "http://localhost:11434/api/generate"


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

class InMemoryCache(LLMCache):
    """Stores LLM responses in memory for the lifetime of the process."""

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    def reset(self) -> None:
        """Reset hit and miss counters without clearing cached responses."""
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


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

class MyOllamaLLM(LLM):
    """Connects to a local Ollama server.

    Pass a cache to avoid repeating identical LLM calls:

        cache = InMemoryCache()
        llm   = MyOllamaLLM(model="qwen2.5-coder:7b", cache=cache)
    """

    _DISPLAY_NAME = "MyOllama"

    def __init__(self, model: str, cache: LLMCache | None = None) -> None:
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
            OLLAMA_URL,
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
