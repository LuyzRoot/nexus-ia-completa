"""Memory management with short-term and long-term storage"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from infrastructure.vectors.pinecone_store import PineconeVectorStore, OpenAIEmbedding

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Memory entry with metadata"""
    id: str
    content: str
    category: str  # "conversation", "fact", "preference", "skill"
    timestamp: datetime
    user_id: str
    metadata: Dict[str, Any] = None
    vector: Optional[List[float]] = None


class MemoryManager:
    """Unified memory management system"""

    def __init__(self):
        self.vector_store = PineconeVectorStore()
        self.embeddings = OpenAIEmbedding()
        self.short_term_memory: Dict[str, List[MemoryEntry]] = {}  # User ID -> memories

    async def save_memory(
        self,
        user_id: str,
        content: str,
        category: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryEntry:
        """Save memory to both short-term and long-term storage"""
        try:
            # Create embedding
            vector = await self.embeddings.embed(content)
            
            # Create memory entry
            memory_id = f"{user_id}_{datetime.utcnow().timestamp()}"
            entry = MemoryEntry(
                id=memory_id,
                content=content,
                category=category,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                metadata=metadata or {},
                vector=vector,
            )
            
            # Save to short-term memory (RAM)
            if user_id not in self.short_term_memory:
                self.short_term_memory[user_id] = []
            self.short_term_memory[user_id].append(entry)
            
            # Save to long-term memory (Pinecone)
            await self.vector_store.upsert(
                vectors=[vector],
                ids=[memory_id],
                metadata=[
                    {
                        "user_id": user_id,
                        "content": content,
                        "category": category,
                        "timestamp": entry.timestamp.isoformat(),
                        **(metadata or {}),
                    }
                ],
            )
            
            logger.info(f"Memory saved: {memory_id}")
            return entry
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            raise

    async def retrieve_memories(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        filter_category: Optional[str] = None,
    ) -> List[MemoryEntry]:
        """Retrieve relevant memories using semantic search"""
        try:
            # Get query embedding
            query_vector = await self.embeddings.embed(query)
            
            # Search in vector store
            filter_dict = None
            if filter_category:
                filter_dict = {"category": filter_category, "user_id": user_id}
            
            results = await self.vector_store.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter_dict,
            )
            
            memories = []
            for result in results:
                memory_id = result["id"]
                metadata = result["metadata"]
                
                entry = MemoryEntry(
                    id=memory_id,
                    content=metadata.get("content", ""),
                    category=metadata.get("category", "conversation"),
                    timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.utcnow().isoformat())),
                    user_id=user_id,
                    metadata=metadata,
                )
                memories.append(entry)
            
            return memories
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            raise

    def get_short_term_memories(self, user_id: str, limit: int = 10) -> List[MemoryEntry]:
        """Get recent short-term memories from RAM"""
        if user_id not in self.short_term_memory:
            return []
        
        return self.short_term_memory[user_id][-limit:]

    async def clear_short_term_memory(self, user_id: str) -> None:
        """Clear short-term memory for a user"""
        if user_id in self.short_term_memory:
            self.short_term_memory[user_id] = []
            logger.info(f"Short-term memory cleared for user: {user_id}")
