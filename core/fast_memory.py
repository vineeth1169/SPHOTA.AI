"""
Fast Memory Layer - Real-Time Ambiguity Resolution using Vector DB

This layer sits BEFORE the SQL-based Context Resolution Matrix.
It retrieves "Top 3 Most Similar Past Intents" from a Vector Database
(ChromaDB) and passes them as "Candidates" to the SQL Engine.

Example:
    User says: "I need dough" (Slang)
    Fast Memory finds: "I need money" (Past intent)
    SQL Engine then checks: Is user at a Bank? → Validates intent
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from numpy.typing import NDArray

# Lazy import chromadb to handle Python 3.14 compatibility
try:
    import chromadb as chromadb  # noqa: F401
    from chromadb.config import Settings as Settings  # noqa: F401
    CHROMADB_AVAILABLE = True
except (ImportError, RuntimeError, Exception):
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None


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
    Fast Memory Layer - Vector-based similarity search for real-time ambiguity.
    
    This layer uses ChromaDB to store and retrieve semantically similar
    past intents, helping resolve ambiguous inputs (like slang) before
    the deterministic SQL engine validates the final intent.
    """
    
    def __init__(
        self,
        persist_directory: str = "./chromadb",
        collection_name: str = "sphota_intents",
        embedding_function: Optional[Any] = None
    ) -> None:
        """
        Initialize Fast Memory with ChromaDB.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
            embedding_function: Optional custom embedding function
        """
        if not CHROMADB_AVAILABLE:
            raise RuntimeError(
                "ChromaDB is not available. Please install it with: "
                "pip install chromadb"
            )
        
        # Create persist directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(  # type: ignore
            path=persist_directory,
            settings=Settings(  # type: ignore
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.embedding_function = embedding_function
    
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
            embedding: Pre-computed embedding (optional)
            metadata: Additional context to store
        """
        if metadata is None:
            metadata = {}
        
        # Generate unique ID based on input and timestamp
        import time
        memory_id = f"{resolved_intent_id}_{int(time.time() * 1000)}"
        
        # Add to ChromaDB
        if embedding is not None:
            # Convert numpy array to list for ChromaDB
            embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding_list],
                documents=[user_input],
                metadatas=[{
                    "intent_id": resolved_intent_id,
                    **metadata
                }]
            )
        else:
            # ChromaDB will use its default embedding function
            self.collection.add(
                ids=[memory_id],
                documents=[user_input],
                metadatas=[{
                    "intent_id": resolved_intent_id,
                    **metadata
                }]
            )
    
    def retrieve_candidates(
        self,
        user_input: str,
        embedding: Optional[NDArray[np.float32]] = None,
        top_k: int = 3
    ) -> List[MemoryCandidate]:
        """
        Retrieve Top K most similar past intents from Fast Memory.
        
        This is the core method called BEFORE SQL validation.
        
        Args:
            user_input: Current user utterance
            embedding: Pre-computed embedding (optional)
            top_k: Number of candidates to retrieve
            
        Returns:
            List of MemoryCandidate objects
        """
        if self.collection.count() == 0:
            # No memories stored yet
            return []
        
        # Query ChromaDB
        if embedding is not None:
            # Use pre-computed embedding
            embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            results = self.collection.query(
                query_embeddings=[embedding_list],
                n_results=min(top_k, self.collection.count())
            )
        else:
            # Let ChromaDB compute embedding
            results = self.collection.query(
                query_texts=[user_input],
                n_results=min(top_k, self.collection.count())
            )
        
        # Convert results to MemoryCandidate objects
        candidates = []
        
        if results and results.get('ids') and len(results['ids']) > 0:
            for i, memory_id in enumerate(results['ids'][0]):
                documents = results.get('documents', [[]])
                metadatas = results.get('metadatas', [[]])
                distances = results.get('distances', [[]])
                
                document = documents[0][i] if documents and len(documents[0]) > i else ""
                metadata = metadatas[0][i] if metadatas and len(metadatas[0]) > i else {}
                distance = distances[0][i] if distances and len(distances[0]) > i else 0.0
                
                # Convert distance to similarity (cosine distance -> similarity)
                similarity = 1.0 - distance if isinstance(distance, (int, float)) else 0.0
                
                # Ensure metadata values are properly typed
                intent_id = str(metadata.get('intent_id', 'unknown')) if metadata else 'unknown'
                metadata_dict = dict(metadata) if metadata else {}
                
                candidate = MemoryCandidate(
                    intent_id=intent_id,
                    original_text=str(document),
                    similarity_score=float(similarity),
                    metadata=metadata_dict
                )
                candidates.append(candidate)
        
        return candidates
    
    def clear_memory(self) -> None:
        """Clear all stored memories (use with caution!)."""
        # Delete and recreate collection
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_memory_count(self) -> int:
        """Get the number of stored memories."""
        return self.collection.count()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Fast Memory.
        
        Returns:
            Dictionary with memory statistics
        """
        return {
            "total_memories": self.collection.count(),
            "collection_name": self.collection.name,
            "distance_metric": "cosine"
        }


def boost_candidates_with_memory(
    base_scores: Dict[str, float],
    memory_candidates: List[MemoryCandidate],
    boost_weight: float = 0.2
) -> Dict[str, float]:
    """
    Boost intent scores based on Fast Memory candidates.
    
    This applies a weighted boost to intents that match past memories,
    helping the SQL engine prioritize previously seen patterns.
    
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
            # Apply boost proportional to similarity
            boost = candidate.similarity_score * boost_weight
            adjusted_scores[intent_id] = min(1.0, adjusted_scores[intent_id] + boost)
    
    return adjusted_scores
