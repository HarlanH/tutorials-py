# Track 42: Two models, one agent

Use a vision model and a text model together in a single agent. Each model
does what it is good at: the VLM sees the image, the text model reasons
about what it saw.

A built-in `InMemoryCache` is attached to each model so identical prompts
are never sent twice.

## The scenario

Three questions about an image, answered by a two-step pipeline:

1. `describe_image` sends the image to `gemma4:e2b` (VLM) and gets a description
2. `answer` sends the description and the question to `qwen2.5-coder:7b` and gets a reply

> "What is in this image?"
> "What colors are most prominent?"
> "Is there any water visible?"

## 1. Install

```bash
uv add opensymbolicai-core
```

```bash
ollama pull qwen2.5-coder:7b
ollama pull gemma4:e2b
```

## 2. Two models, one class

`OllamaLLM` works for both text and vision models. Pass image data via
the `images` keyword argument and Ollama routes it to the right model.

```python
from opensymbolicai.llm import LLM, LLMConfig, LLMResponse, InMemoryCache

class OllamaLLM(LLM):

    def __init__(self, model: str) -> None:
        super().__init__(
            LLMConfig(provider="ollama", model=model),
            cache=InMemoryCache(),
        )

    def _generate_impl(self, prompt: str, **kwargs) -> LLMResponse:
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            **kwargs,          # images=[base64_string] passes through here
        }
        ...
```

## 3. The agent

`ImageAgent` takes two LLM instances: one for planning and text reasoning,
one for vision. Each primitive calls whichever model fits the task.

```python
class ImageAgent(PlanExecute):

    def __init__(self, llm: LLM, vision_llm: LLM) -> None:
        super().__init__(llm=llm)
        self._vision_llm = vision_llm

    @primitive(read_only=True)
    def describe_image(self, path: str) -> str:
        """Use the vision model to describe the contents of an image file."""
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return self._vision_llm.generate(
            "Describe everything you see in this image in detail.",
            images=[b64],
        ).text.strip()

    @primitive(read_only=True)
    def answer(self, question: str, description: str) -> str:
        """Use the text model to answer a question given an image description."""
        prompt = f"Image description: {description}\n\nQuestion: {question}"
        return self._llm.generate(prompt).text.strip()
```

## 4. Run it

```bash
uv run main.py
```

The sample image is downloaded automatically on first run.

## Sample output

```
Text model  : qwen2.5-coder:7b
Vision model: gemma4:e2b
Image       : sample.jpg
==================================================

Q: What is in this image?
   Plan  : description = describe_image('sample.jpg')
           result = answer('What is in this image?', description)
           return respond(result)
   Answer: A panoramic view of a rugged, mountainous landscape with a deep
           valley, dense forestation, and clear bright lighting.

Q: What colors are most prominent?
   Plan  : description = describe_image('sample.jpg')
           colors = answer('What colors are most prominent?', description)
           return respond(colors)
   Answer: Dark green for the lush vegetation, gray for the rock formations,
           blue for the sky, and white for the wispy clouds.

Q: Is there any water visible?
   Plan  : description = describe_image('sample.jpg')
           water_visible = 'water' in description.lower()
           result = answer('Is there any water visible?', ...)
           return respond(result)
   Answer: Yes, there is a calm body of water running through the bottom
           of the valley.
```

## What just happened

The text model (`qwen2.5-coder:7b`) never sees the image. It writes a plan,
calls `describe_image`, receives a text description back, and calls `answer`
to extract a focused reply. The VLM (`gemma4:e2b`) never sees the question;
it only describes what it sees.

The cache means `describe_image` is only called once per unique image path.
On a second run with the same questions, both models return from cache
instantly (28s to 0s in testing).

## Takeaway

Inject additional models as constructor arguments alongside `llm`. The agent's
planning model stays unchanged; it just calls primitives. Each primitive
decides which model to use internally.

```python
text_llm   = OllamaLLM(model="qwen2.5-coder:7b")
vision_llm = OllamaLLM(model="gemma4:e2b")

agent = ImageAgent(llm=text_llm, vision_llm=vision_llm)
```

The same pattern works for any combination: a code model, an embedding
model, a reasoning model, each used only where it fits.
