import pytest
import asyncio

def test_predictor_generate(monkeypatch_llm, monkeypatch_embeddings, setup_test_db):
    pred_mod = pytest.importorskip("inference.predictor")
    async def run():
        p = pred_mod.Predictor()
        messages = [{"role":"user","content":"hello"}]
        resp = await p.generate(messages, temperature=0.1)
        # resp should be a ProviderResponse-like object with .text
        assert hasattr(resp, "text")
        assert "echo" in resp.text
    asyncio.run(run())

def test_generate_with_retrieval(monkeypatch_llm, monkeypatch_embeddings, setup_test_db):
    pred_mod = pytest.importorskip("inference.predictor")
    rag_mod = pytest.importorskip("rag.index")
    async def run():
        p = pred_mod.Predictor()
        # If retriever exists, call generate_with_retrieval. If not, it should still return a resp.
        items, resp = await p.generate_with_retrieval("test query", top_k=2, rerank=False)
        assert hasattr(resp, "text")
    asyncio.run(run())