"""OllamaLLM: a minimal Ollama LLM.

Works for both text and vision models. Pass image data via the `images`
keyword argument to generate():

    llm.generate("What is in this image?", images=[base64_string])

Vision models require the /api/chat endpoint with images in the message,
while text models use the simpler /api/generate endpoint.
"""

from __future__ import annotations

import json
import urllib.request

from opensymbolicai.llm import LLM, LLMConfig, LLMResponse, InMemoryCache, TokenUsage

OLLAMA_BASE = "http://localhost:11434"


class OllamaLLM(LLM):

    _DISPLAY_NAME = "Ollama"

    def __init__(self, model: str) -> None:
        # LLM base class requires an LLMConfig; we build it internally
        # so callers only need to pass a model name.
        # InMemoryCache avoids re-calling the model for identical prompts.
        super().__init__(LLMConfig(provider="ollama", model=model), cache=InMemoryCache())

    def _generate_impl(self, prompt: str, **kwargs) -> LLMResponse:
        images = kwargs.pop("images", None)

        if images:
            # Vision models require /api/chat with images in the message
            payload = json.dumps({
                "model": self.config.model,
                "messages": [{
                    "role": "user",
                    "content": prompt,
                    "images": images,
                }],
                "stream": False,
            }).encode()
            url = f"{OLLAMA_BASE}/api/chat"
        else:
            # Text-only requests use the simpler /api/generate
            payload = json.dumps({
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                **kwargs,
            }).encode()
            url = f"{OLLAMA_BASE}/api/generate"

        request = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request) as resp:
            data = json.loads(resp.read())

        # /api/chat returns message.content, /api/generate returns response
        if images:
            text = data["message"]["content"]
        else:
            text = data["response"]

        return LLMResponse(
            text=text,
            usage=TokenUsage(
                input_tokens=data.get("prompt_eval_count", 0),
                output_tokens=data.get("eval_count", 0),
            ),
            provider="ollama",
            model=self.config.model,
        )
