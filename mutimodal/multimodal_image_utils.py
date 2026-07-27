"""
Image utilities: loading, resizing, encoding to base64, safe operations.
"""
from typing import Tuple, Optional
import io
import base64
import logging

logger = logging.getLogger("multimodal.image_utils")

try:
    from PIL import Image, ImageOps, ImageDraw, ImageFont  # type: ignore
    _HAS_PIL = True
except Exception:
    Image = None
    _HAS_PIL = False


def load_image_from_path(path: str):
    if not _HAS_PIL:
        raise RuntimeError("Pillow is not installed. Install pillow to use image utilities.")
    return Image.open(path).convert("RGB")


def open_image_from_bytes(data: bytes):
    if not _HAS_PIL:
        raise RuntimeError("Pillow is not installed. Install pillow to use image utilities.")
    return Image.open(io.BytesIO(data)).convert("RGB")


def resize_image(img, size: Tuple[int, int], fit: bool = True):
    """
    Resize image to size=(w,h). If fit=True, maintain aspect ratio and pad with white.
    """
    if not _HAS_PIL:
        raise RuntimeError("Pillow is not installed.")
    if fit:
        return ImageOps.contain(img, size)
    return img.resize(size)


def image_to_base64(img, fmt: str = "JPEG", quality: int = 85) -> str:
    """
    Encode PIL.Image to base64 data URI (jpeg by default).
    """
    if not _HAS_PIL:
        raise RuntimeError("Pillow is not installed.")
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=quality)
    b = buf.getvalue()
    return "data:image/{};base64,".format(fmt.lower()) + base64.b64encode(b).decode("utf-8")


def placeholder_image_with_text(text: str, size: Tuple[int, int] = (512, 512)):
    """
    Return a simple placeholder image with text (Pillow).
    """
    if not _HAS_PIL:
        raise RuntimeError("Pillow is not installed.")
    img = Image.new("RGB", size, color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    w, h = draw.textsize(text, font=font)
    draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, fill=(10, 10, 10), font=font)
    return img