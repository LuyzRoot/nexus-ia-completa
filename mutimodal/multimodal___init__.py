"""
Multimodal helpers for NEXUS.

Exports:
- image utilities (load, resize, base64)
- OCR (pytesseract)
- captioning (transformers/blip or fallback)
- image generation (diffusers / openai / fallback)
- audio (ASR + TTS)
- pipelines (combine caption + LLM)
"""
from .image_utils import load_image_from_path, open_image_from_bytes, image_to_base64, resize_image  # noqa: F401
from .ocr import ocr_from_image  # noqa: F401
from .captioning import caption_image  # noqa: F401
from .image_generation import generate_image  # noqa: F401
from .audio import transcribe_audio, synthesize_speech  # noqa: F401
from .pipelines import describe_image_and_answer  # noqa: F401

__all__ = [
    "load_image_from_path", "open_image_from_bytes", "image_to_base64", "resize_image",
    "ocr_from_image", "caption_image", "generate_image", "transcribe_audio", "synthesize_speech",
    "describe_image_and_answer",
]