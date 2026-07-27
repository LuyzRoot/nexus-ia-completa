"""
Image captioning abstraction:

Tries several backends in order:
- transformers pipeline("image-to-text") (e.g., Salesforce/blip-* models)
- minimal local heuristic fallback (placeholder)
"""

import logging
from typing import Optional

logger = logging.getLogger("multimodal.captioning")

# try huggingface transformers pipeline
try:
    from transformers import pipeline  # type: ignore
    _HAS_TRANSFORMERS = True
except Exception:
    pipeline = None
    _HAS_TRANSFORMERS = False

_captioner = None

def _init_captioner():
    global _captioner
    if _captioner is not None:
        return _captioner
    if _HAS_TRANSFORMERS:
        try:
            # image-to-text pipeline will select a default model if none provided
            _captioner = pipeline("image-to-text")
            logger.info("Initialized transformers image-to-text pipeline")
            return _captioner
        except Exception as exc:
            logger.warning("Transformers image-to-text pipeline unavailable: %s", exc)
            _captioner = None
    return None

def caption_image(pil_image, max_length: int = 64) -> str:
    """
    Return a caption for the provided PIL image.
    """
    captioner = _init_captioner()
    if captioner:
        try:
            # pipeline returns list of dicts with 'generated_text'
            out = captioner(pil_image, max_length=max_length)
            if isinstance(out, (list, tuple)) and out:
                text = out[0].get("generated_text") or out[0].get("caption") or str(out[0])
                return text.strip()
            return str(out)
        except Exception as exc:
            logger.exception("Captioning failed: %s", exc)
    # fallback heuristic: placeholder
    try:
        from multimodal.image_utils import placeholder_image_with_text  # avoid circular heavy imports
    except Exception:
        return "an image"
    return "An image (captioning not available in this environment)."