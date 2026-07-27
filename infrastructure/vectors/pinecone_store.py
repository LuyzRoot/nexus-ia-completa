"""Pinecone Vector Database Provider"""
import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone

from infrastructure.vectors.base import VectorStoreProvider, EmbeddingProvider
from config.settings import settings

logger = logging.getLogger(__name__)


class PineconeVectorStore(VectorStoreProvider):
    """Pinecone Vector Database Implementation"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.PINECONE_API_KEY
        self.environment = settings.PINECONE_ENVIRONMENT
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = settings.PINECONE_DIMENSION
        self.name = "pinecone"
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(self.index_name)

    async def upsert(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: List[Dict[str, Any]],
    ) -> None:
        """Store vectors in Pinecone"""
        try:
            vectors_to_upsert = [
                (id_, vector, meta)
                for id_, vector, meta in zip(ids, vectors, metadata)
            ]
            self.index.upsert(vectors=vectors_to_upsert)
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
        except Exception as e:
            logger.error(f"Pinecone upsert error: {e}")
            raise

    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Query similar vectors from Pinecone"""
        try:
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter=filter,
                include_metadata=True,
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata,
                }
                for match in results.matches
            ]
        except Exception as e:
            logger.error(f"Pinecone query error: {e}")
            raise

    async def delete(self, ids: List[str]) -> None:
        """Delete vectors from Pinecone"""
        try:
            self.index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} vectors from Pinecone")
        except Exception as e:
            logger.error(f"Pinecone delete error: {e}")
            raise


class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI Embeddings Provider"""

    def __init__(self, api_key: Optional[str] = None):
        from openai import AsyncOpenAI
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.name = "openai_embeddings"

    async def embed(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI batch embedding error: {e}")
            raise
