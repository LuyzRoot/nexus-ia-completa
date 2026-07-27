"""
OCR functionality using pytesseract when available.
Provides:
- ocr_from_image(pil_image) -> str
"""
import logging

logger = logging.getLogger("multimodal.ocr")

try:
    import pytesseract  # type: ignore
    _HAS_PYTESSERACT = True
except Exception:
    pytesseract = None
    _HAS_PYTESSERACT = False

try:
    from PIL import Image  # type: ignore
except Exception:
    Image = None

def ocr_from_image(pil_image) -> str:
    """
    Extract text from a PIL image using pytesseract. Raises helpful error if lib missing.
    """
    if not _HAS_PYTESSERACT:
        raise RuntimeError("pytesseract is not installed. Install pytesseract and Tesseract-OCR binary to enable OCR.")
    # pillow image expected
    try:
        text = pytesseract.image_to_string(pil_image)
        return text.strip()
    except Exception as exc:
        logger.exception("OCR failed: %s", exc)
        raise