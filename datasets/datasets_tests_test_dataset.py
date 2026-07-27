import os
from datasets.loader import load_jsonl, load_csv
from datasets.validate import validate_jsonl, validate_csv
from datasets.preprocess import prepare_document, chunk_text_by_chars

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "sample")


def test_load_jsonl():
    p = os.path.join(SAMPLE_DIR, "sample.jsonl")
    items = list(load_jsonl(p))
    assert len(items) >= 2
    assert any("text" in it for it in items)


def test_load_csv():
    p = os.path.join(SAMPLE_DIR, "sample.csv")
    items = list(load_csv(p))
    assert len(items) >= 2
    assert "text" in items[0]


def test_prepare_and_chunk():
    raw = {"id": "x1", "text": "a"*2500}
    doc = prepare_document(raw)
    chunks = chunk_text_by_chars(doc["text"], chunk_size=1000, overlap=100)
    assert len(chunks) >= 2