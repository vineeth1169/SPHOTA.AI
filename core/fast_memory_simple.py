"""
Fast Memory Layer - Lightweight In-Memory Implementation (No ChromaDB)

This is a simple alternative that uses only numpy for vector search.
Use this if ChromaDB installation fails due to Python version compatibility.

Differences from chromadb version:
- In-memory only (no persistence between runs)
- Pure numpy implementation
- No external dependencies beyond numpy
- Slightly faster for small datasets (<10K memories)
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray
import pickle
from pathlib import Path


@dataclass
class MemoryCandidate:
    """
    A candidate intent retrieved from Fast Memory.
    
    Attributes:
        intent_id: The stored intent identifier
        original_text: The original user utterance
        similarity_score: Cosine similarity to current input
        metadata: Additional context stored with this memory
    """
    intent_id: str
    original_text: str
    similarity_score: float
    metadata: Dict[str, Any]


class FastMemory:
    """
    Fast Memory Layer - Simple in-memory vector store.
    
    This is a lightweight alternative to ChromaDB that uses only numpy.
    Perfect for development and when ChromaDB dependencies are incompatible.
    """
    
    def __init__(
        self,
        persist_directory: str = "./fast_memory_data",
        collection_name: str = "sphota_intents"
    ) -> None:
        """
        Initialize Fast Memory with in-memory storage.
        
        Args:
            persist_directory: Directory to save/load memory snapshots
            collection_name: Name identifier for this memory collection
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        
        # In-memory storage
        self.memories: List[Dict[str, Any]] = []
        self.embeddings: Optional[NDArray[np.float32]] = None
        
        # Create persist directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Try to load existing memories
        self._load_from_disk()
    
    def add_memory(
        self,
        user_input: str,
        resolved_intent_id: str,
        embedding: Optional[NDArray[np.float32]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store a user input and its resolved intent in Fast Memory.
        
        Args:
            user_input: The original user utterance
            resolved_intent_id: The intent that was ultimately resolved
            embedding: Pre-computed embedding (required for this implementation)
            metadata: Additional context to store
        """
        if embedding is None:
            raise ValueError("Embedding is required for simple Fast Memory")
        
        if metadata is None:
            metadata = {}
        
        # Generate unique ID
        import time
        memory_id = f"{resolved_intent_id}_{int(time.time() * 1000)}"
        
        # Store memory
        memory = {
            "id": memory_id,
            "document": user_input,
            "intent_id": resolved_intent_id,
            "metadata": metadata
        }
        self.memories.append(memory)
        
        # Add embedding to matrix
        embedding_vector = embedding.reshape(1, -1)
        if self.embeddings is None:
            self.embeddings = embedding_vector
        else:
            self.embeddings = np.vstack([self.embeddings, embedding_vector])
    
    def retrieve_candidates(
        self,
        user_input: str,
        embedding: Optional[NDArray[np.float32]] = None,
        top_k: int = 3
    ) -> List[MemoryCandidate]:
        """
        Retrieve Top K most similar past intents from Fast Memory.
        
        Args:
            user_input: Current user utterance
            embedding: Pre-computed embedding (required)
            top_k: Number of candidates to retrieve
            
        Returns:
            List of MemoryCandidate objects
        """
        if len(self.memories) == 0:
            return []
        
        if embedding is None:
            raise ValueError("Embedding is required for simple Fast Memory")
        
        # Normalize query embedding
        query_embedding = embedding.reshape(1, -1)
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_embedding = query_embedding / query_norm
        
        # Normalize stored embeddings
        if self.embeddings is not None:
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            normalized_embeddings = self.embeddings / norms
        else:
            return []
        
        # Compute cosine similarities
        similarities = np.dot(normalized_embeddings, query_embedding.T).flatten()
        
        # Get top K indices
        top_k = min(top_k, len(self.memories))
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Build candidates
        candidates = []
        for idx in top_indices:
            memory = self.memories[idx]
            candidate = MemoryCandidate(
                intent_id=memory["intent_id"],
                original_text=memory["document"],
                similarity_score=float(similarities[idx]),
                metadata=memory["metadata"]
            )
            candidates.append(candidate)
        
        return candidates
    
    def clear_memory(self) -> None:
        """Clear all stored memories."""
        self.memories = []
        self.embeddings = None
    
    def get_memory_count(self) -> int:
        """Get the number of stored memories."""
        return len(self.memories)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Fast Memory.
        
        Returns:
            Dictionary with memory statistics
        """
        return {
            "total_memories": len(self.memories),
            "collection_name": self.collection_name,
            "distance_metric": "cosine",
            "implementation": "numpy_in_memory"
        }
    
    def save_to_disk(self) -> None:
        """Save memories to disk for persistence."""
        save_path = self.persist_directory / f"{self.collection_name}.pkl"
        
        data = {
            "memories": self.memories,
            "embeddings": self.embeddings
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(data, f)
    
    def _load_from_disk(self) -> None:
        """Load memories from disk if available."""
        load_path = self.persist_directory / f"{self.collection_name}.pkl"
        
        if load_path.exists():
            try:
                with open(load_path, 'rb') as f:
                    data = pickle.load(f)
                
                self.memories = data.get("memories", [])
                self.embeddings = data.get("embeddings", None)
            except Exception:
                # If loading fails, start fresh
                self.memories = []
                self.embeddings = None


def boost_candidates_with_memory(
    base_scores: Dict[str, float],
    memory_candidates: List[MemoryCandidate],
    boost_weight: float = 0.2
) -> Dict[str, float]:
    """
    Boost intent scores based on Fast Memory candidates.
    
    Args:
        base_scores: Original similarity scores from SBERT
        memory_candidates: Candidates retrieved from Fast Memory
        boost_weight: Weight of the memory boost (0.0 to 1.0)
        
    Returns:
        Adjusted scores with memory boost applied
    """
    adjusted_scores = base_scores.copy()
    
    for candidate in memory_candidates:
        intent_id = candidate.intent_id
        if intent_id in adjusted_scores:
            boost = candidate.similarity_score * boost_weight
            adjusted_scores[intent_id] = min(1.0, adjusted_scores[intent_id] + boost)
    
    return adjusted_scores
