"""Track 42: two models, one agent.

qwen2.5-coder:7b  — text model, writes plans and distils answers.
gemma4:e2b        — vision model, describes the image.

The agent receives a question about an image. The text model writes a plan
that calls describe_image (VLM) then answer (text model) to produce a reply.
"""

from __future__ import annotations

import os
import sys
import urllib.request

from image_agent import ImageAgent
from llm import OllamaLLM
from ollama import check_ollama

TEXT_MODEL   = "qwen2.5-coder:7b"
VISION_MODEL = "gemma4:e2b"

SAMPLE_IMAGE = os.path.join(os.path.dirname(__file__), "sample.jpg")
SAMPLE_IMAGE_URL = "https://www.gstatic.com/webp/gallery/1.jpg"

QUESTIONS = [
    "What is in this image?",
    "What colors are most prominent?",
    "Is there any water visible?",
]


def ensure_sample_image() -> None:
    if os.path.exists(SAMPLE_IMAGE):
        return
    print(f"Downloading sample image...")
    req = urllib.request.Request(
        SAMPLE_IMAGE_URL,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req) as resp:
        with open(SAMPLE_IMAGE, "wb") as f:
            f.write(resp.read())
    print(f"Saved to {SAMPLE_IMAGE}\n")


def main() -> None:
    if not check_ollama(TEXT_MODEL) or not check_ollama(VISION_MODEL):
        sys.exit(1)

    ensure_sample_image()

    text_llm   = OllamaLLM(model=TEXT_MODEL)
    vision_llm = OllamaLLM(model=VISION_MODEL)

    print(f"Text model  : {TEXT_MODEL}")
    print(f"Vision model: {VISION_MODEL}")
    print(f"Image       : {SAMPLE_IMAGE}")
    print("=" * 50)

    for question in QUESTIONS:
        agent = ImageAgent(llm=text_llm, vision_llm=vision_llm)
        prompt = f"Look at {SAMPLE_IMAGE}. {question}"
        result = agent.run(prompt)

        print(f"\nQ: {question}")
        print(f"   Plan  : {result.plan.strip()}")
        print(f"   Answer: {result.result}")


if __name__ == "__main__":
    main()
