"""
RAG index abstraction: add documents (auto-chunk), index via vector store, search by similarity.
Uses core.embeddings.embed_text (async) for vectorization and memory/vector_store.get_default_vector_store as backend.
Optionally persists metadata to DB if `persist_metadata=True` and app.database is available.
"""
import asyncio
import logging
from typing import List, Dict, Optional, Tuple

from core.embeddings import embed_text
from memory.vector_store import get_default_vector_store, BaseVectorStore
from rag.chunker import chunk_document
from rag.loader import load_documents_from_paths

logger = logging.getLogger("rag.index")

# Optional DB persistence for metadata
try:
    from app.database import Base, engine  # type: ignore
    from sqlalchemy import Column, String, JSON, Text
    from sqlalchemy.orm import sessionmaker
    _HAS_DB = True
except Exception:
    Base = None
    engine = None
    sessionmaker = None
    _HAS_DB = False

if _HAS_DB and Base is not None:
    try:
        class RAGDocument(Base):  # type: ignore
            __tablename__ = "rag_documents"
            id = Column(String(100), primary_key=True)
            source_id = Column(String(100), index=True)
            metadata = Column(JSON)
            text = Column(Text)

        # ensure table exists at runtime (for dev only; production should use alembic)
        try:
            Base.metadata.create_all(bind=engine, tables=[RAGDocument.__table__])
        except Exception:
            pass
    except Exception:
        RAGDocument = None
else:
    RAGDocument = None

class RAGIndex:
    def __init__(self, vector_store: Optional[BaseVectorStore] = None, persist_metadata: bool = False):
        self.store = vector_store or get_default_vector_store()
        self.persist_metadata = persist_metadata and (RAGDocument is not None)
        # DB session factory if DB available
        self._Session = sessionmaker(bind=engine) if _HAS_DB and sessionmaker else None

    async def add_documents(self, docs: List[Dict], chunk_size: int = 1000, overlap: int = 200):
        """
        Adds documents (list of {"id","text","metadata"}). Auto-chunks each document and stores vectors.
        """
        tasks = []
        for doc in docs:
            chunks = chunk_document(doc, chunk_size=chunk_size, overlap=overlap)
            for chunk in chunks:
                tasks.append(self._add_chunk(chunk))
        # execute sequentially (embedding calls can be heavy); you may parallelize with asyncio.gather but be careful with rate limits
        for t in tasks:
            await t

    async def _add_chunk(self, chunk: Dict):
        # chunk: {"id","text","metadata"}
        await self.store.add_document(chunk["id"], chunk["text"], metadata=chunk.get("metadata"))
        if self.persist_metadata and self._Session:
            session = self._Session()
            try:
                row = RAGDocument(id=chunk["id"], source_id=chunk["metadata"].get("source_id"), metadata=chunk["metadata"], text=chunk["text"])
                session.merge(row)
                session.commit()
            except Exception as exc:
                logger.exception("Failed to persist rag document metadata: %s", exc)
                session.rollback()
            finally:
                session.close()

    async def add_from_paths(self, paths: List[str], namespace: Optional[str] = None, chunk_size: int = 1000, overlap: int = 200):
        docs = load_documents_from_paths(paths, namespace=namespace)
        await self.add_documents(docs, chunk_size=chunk_size, overlap=overlap)

    async def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """
        Returns list of (doc_id, score, metadata) from vector_store.search
        """
        return await self.store.search(query, top_k=top_k)

    async def get_document_text(self, doc_id: str) -> Optional[str]:
        """
        If persisted to DB, returns the stored text; otherwise metadata not guaranteed.
        """
        if self.persist_metadata and self._Session:
            session = self._Session()
            try:
                r = session.query(RAGDocument).filter(RAGDocument.id == doc_id).first()
                return r.text if r else None
            finally:
                session.close()
        return None