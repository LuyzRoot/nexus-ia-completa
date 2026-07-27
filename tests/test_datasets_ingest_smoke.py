import pytest
import os
import json
import tempfile
import asyncio

def test_datasets_loader_and_preprocess(tmp_path, monkeypatch_embeddings):
    ds = pytest.importorskip("datasets.loader")
    prep = pytest.importorskip("datasets.preprocess")
    # create sample jsonl
    p = tmp_path / "s.jsonl"
    p.write_text(json.dumps({"id":"x1","text":"hello world"}) + "\n")
    # load
    rows = list(ds.load_jsonl(str(p)))
    assert rows and rows[0]["id"] == "x1"
    doc = prep.prepare_document(rows[0])
    assert "text" in doc and doc["id"].startswith("x1")