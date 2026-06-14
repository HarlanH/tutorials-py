"""OllamaLLM: a minimal Ollama LLM.

Works for both text and vision models. Pass image data via the `images`
keyword argument to generate():

    llm.generate("What is in this image?", images=[base64_string])

Ollama includes the extra kwargs in the request payload, so the same
class works for any model regardless of its capabilities.
"""

from __future__ import annotations

import json
import urllib.request

from opensymbolicai.llm import LLM, LLMConfig, LLMResponse, InMemoryCache, TokenUsage

OLLAMA_URL = "http://localhost:11434/api/generate"


class OllamaLLM(LLM):

    _DISPLAY_NAME = "Ollama"

    def __init__(self, model: str) -> None:
        # LLM base class requires an LLMConfig; we build it internally
        # so callers only need to pass a model name.
        # InMemoryCache avoids re-calling the model for identical prompts.
        super().__init__(LLMConfig(provider="ollama", model=model), cache=InMemoryCache())

    def _generate_impl(self, prompt: str, **kwargs) -> LLMResponse:
        payload = json.dumps({
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            **kwargs,          # e.g. images=[base64_string] for vision models
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
            provider="ollama",
            model=self.config.model,
        )
