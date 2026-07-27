import os
import pytest
from multimodal.image_utils import placeholder_image_with_text, image_to_base64
from multimodal.captioning import caption_image

def test_placeholder_image_and_base64():
    img = placeholder_image_with_text("hello test", size=(200,200))
    data_uri = image_to_base64(img, fmt="JPEG")
    assert data_uri.startswith("data:image/jpeg;base64,")
    # quick length check
    assert len(data_uri) > 100

@pytest.mark.skipif(True, reason="captioning backend may be absent in CI")
def test_captioning_on_placeholder():
    img = placeholder_image_with_text("a cat on a mat", size=(256,256))
    caption = caption_image(img)
    assert isinstance(caption, str)