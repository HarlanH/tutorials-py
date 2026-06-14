"""ImageAgent: answers questions about an image using two models.

  vision_llm  — a VLM (gemma4:e2b) that sees the image and produces
                a detailed description.

  llm         — a text model (qwen2.5-coder:7b) that writes the plan
                and distils a focused answer from the description.

The agent wires them together: describe_image calls the VLM, answer
calls the text model. Neither model knows about the other.
"""

from __future__ import annotations

import base64

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive
from opensymbolicai.llm import LLM


class ImageAgent(PlanExecute):

    def __init__(self, llm: LLM, vision_llm: LLM) -> None:
        super().__init__(llm=llm)
        self._vision_llm = vision_llm

    # ------------------------------------------------------------------
    # Primitives
    # ------------------------------------------------------------------

    @primitive(read_only=True)
    def describe_image(self, path: str) -> str:
        """Use the vision model to describe the contents of an image file.

        Example: describe_image("photo.jpg")
                 -> "A landscape with mountains and a river..."
        """
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return self._vision_llm.generate(
            "Describe everything you see in this image in detail.",
            images=[b64],
        ).text.strip()

    @primitive(read_only=True)
    def answer(self, question: str, description: str) -> str:
        """Use the text model to answer a specific question from a description.

        Example: answer("What colors are dominant?", "A mountain scene with...")
                 -> "Green and grey are the dominant colors."
        """
        prompt = (
            f"Image description: {description}\n\n"
            f"Question: {question}\n"
            f"Answer in one or two sentences."
        )
        return self._llm.generate(prompt).text.strip()

    @primitive(read_only=True)
    def respond(self, message: str) -> str:
        """Return the message as the final answer."""
        return message

    # ------------------------------------------------------------------
    # Decompositions
    # ------------------------------------------------------------------

    @decomposition(
        intent="Look at photo.jpg. What is in this image?",
        expanded_intent=(
            "Call describe_image with the image path to get the visual content. "
            "Call answer with the original question and the description. "
            "Return the respond call with the answer."
        ),
    )
    def _example(self):
        description = self.describe_image("photo.jpg")
        result = self.answer("What is in this image?", description)
        return self.respond(result)
