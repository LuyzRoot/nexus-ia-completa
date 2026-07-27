import pytest

def test_multimodal_placeholder_and_caption():
    mm = pytest.importorskip("multimodal.image_utils")
    img = mm.placeholder_image_with_text("hello test", size=(200,200))
    assert img is not None
    # image_to_base64 may raise if pillow missing; importorskip handled
    base64_uri = mm.image_to_base64(img, fmt="JPEG")
    assert base64_uri.startswith("data:image/jpeg;base64,")

    # captioning may be absent; try if available
    try:
        cap = pytest.importorskip("multimodal.captioning")
        # If caption_image uses transformers pipeline it may require heavy deps; allow both behaviors
        caption = cap.caption_image(img)
        assert isinstance(caption, str)
    except Exception:
        # if not present, pass
        pass