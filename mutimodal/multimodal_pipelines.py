"""
Higher-level multimodal pipelines that combine vision + LLM.

- describe_image_and_answer(image_bytes, question) -> (caption, answer)
   Steps:
    1) caption_image
    2) build messages: system prompt includes caption, then user question
    3) call core.llm.llm_router.generate
"""

import logging
from typing import Tuple, List, Dict, Any

logger = logging.getLogger("multimodal.pipelines")

from core.llm import llm_router  # type: ignore

from multimodal.image_utils import open_image_from_bytes  # type: ignore
from multimodal.captioning import caption_image  # type: ignore

async def describe_image_and_answer(image_bytes: bytes, question: str, temperature: float = 0.2) -> Dict[str, Any]:
    """
    Returns:
      {"caption": "...", "answer": ProviderResponse-like object (text, provider_name, model)}
    """
    try:
        pil = open_image_from_bytes(image_bytes)
    except Exception as exc:
        logger.exception("Failed to open image: %s", exc)
        raise

    caption = caption_image(pil)
    system_msg = {"role": "system", "content": f"You are an assistant that can answer questions about an image. Image caption: {caption}"}
    user_msg = {"role": "user", "content": question}
    messages = [system_msg, user_msg]
    resp = await llm_router.generate(messages, temperature=temperature)
    return {"caption": caption, "answer": resp}