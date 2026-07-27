import pytest
import asyncio

def test_rag_index_add_search(monkeypatch, monkeypatch_embeddings, setup_test_db):
    rag = pytest.importorskip("rag.index")
    # use RAGIndex and add a small document, then search
    async def run():
        idx = rag.RAGIndex()
        docs = [{"id":"d1","text":"hello world from nexus","metadata":{"title":"doc1"}}]
        await idx.add_documents(docs)
        res = await idx.search("hello")
        assert isinstance(res, list)
        # Each result is (doc_id, score, metadata) when using default InMemoryVectorStore
        assert any(r[0].startswith("d1") for r in res)
    asyncio.run(run())