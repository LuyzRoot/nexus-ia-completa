"""
Image generation helpers.

Backends attempted:
- diffusers (Stable Diffusion) when installed and CUDA available
- OpenAI Images API (if openai installed & key configured)
- Fallback: generate a simple placeholder image with prompt text (Pillow)
"""

import logging
from typing import Optional
import io

logger = logging.getLogger("multimodal.image_generation")

# Try diffusers
try:
    from diffusers import StableDiffusionPipeline  # type: ignore
    import torch  # type: ignore
    _HAS_DIFFUSERS = True
except Exception:
    StableDiffusionPipeline = None
    torch = None
    _HAS_DIFFUSERS = False

# Try OpenAI images (openai python package)
try:
    import openai  # type: ignore
    _HAS_OPENAI = True
except Exception:
    openai = None
    _HAS_OPENAI = False

from multimodal.image_utils import placeholder_image_with_text, image_to_base64  # type: ignore


async def generate_image(prompt: str, width: int = 512, height: int = 512, steps: int = 20, provider: Optional[str] = None) -> bytes:
    """
    Generate an image from prompt and return raw image bytes (JPEG).
    provider can be "diffusers", "openai" or None to auto-select.
    """
    # prefer explicit provider if requested
    if provider == "diffusers" and _HAS_DIFFUSERS:
        return _generate_with_diffusers(prompt, width, height, steps)
    if provider == "openai" and _HAS_OPENAI:
        return await _generate_with_openai(prompt, width, height)

    # auto selection: diffusers -> openai -> fallback
    if _HAS_DIFFUSERS:
        try:
            return _generate_with_diffusers(prompt, width, height, steps)
        except Exception as exc:
            logger.warning("Diffusers generation failed: %s", exc)
    if _HAS_OPENAI:
        try:
            return await _generate_with_openai(prompt, width, height)
        except Exception as exc:
            logger.warning("OpenAI image generation failed: %s", exc)

    # fallback: placeholder image with text
    img = placeholder_image_with_text(prompt[:120], size=(width, height))
    data_uri = image_to_base64(img, fmt="JPEG")
    # return raw bytes (decoded) for consistency
    header, b64 = data_uri.split(",", 1)
    return io.BytesIO(base64_decode(b64)).getvalue()


def _generate_with_diffusers(prompt: str, width: int, height: int, steps: int) -> bytes:
    if not _HAS_DIFFUSERS:
        raise RuntimeError("diffusers not available")
    # Note: model selection and device placement may require config in production
    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = pipe.to(device)
    image = pipe(prompt, height=height, width=width, num_inference_steps=steps).images[0]
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


async def _generate_with_openai(prompt: str, width: int, height: int) -> bytes:
    if not _HAS_OPENAI:
        raise RuntimeError("openai package not available")
    # this requires OPENAI_API_KEY configured in environment; adapt as needed
    resp = openai.Image.create(prompt=prompt, size=f"{width}x{height}")
    # resp.data[0].b64_json contains base64
    import base64
    b64 = resp["data"][0]["b64_json"]
    return base64.b64decode(b64)


def base64_decode(s: str) -> bytes:
    import base64
    return base64.b64decode(s)