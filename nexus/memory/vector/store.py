from typing import List, Optional
import numpy as np
from abc import ABC, abstractmethod

class VectorStore(ABC):
    """Abstract vector store for embeddings"""
    
    @abstractmethod
    async def add(self, id: str, embedding: List[float], metadata: dict = None):
        pass
    
    @abstractmethod
    async def search(self, embedding: List[float], top_k: int = 5):
        pass
    
    @abstractmethod
    async def delete(self, id: str):
        pass

class MemoryVectorStore(VectorStore):
    """In-memory vector store (development only)"""
    
    def __init__(self):
        self.vectors = {}
        self.embeddings = {}
    
    async def add(self, id: str, embedding: List[float], metadata: dict = None):
        self.embeddings[id] = np.array(embedding)
        self.vectors[id] = metadata or {}
    
    async def search(self, embedding: List[float], top_k: int = 5):
        if not self.embeddings:
            return []
        
        query = np.array(embedding)
        scores = []
        
        for id, vec in self.embeddings.items():
            # Cosine similarity
            similarity = np.dot(query, vec) / (np.linalg.norm(query) * np.linalg.norm(vec) + 1e-10)
            scores.append((id, similarity, self.vectors[id]))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
    
    async def delete(self, id: str):
        self.embeddings.pop(id, None)
        self.vectors.pop(id, None)
