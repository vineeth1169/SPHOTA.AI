"""
Intent Engine (The Flash of Insight)

This is the core intent recognition engine that extracts the "Resolved Intent"
(Total Intent) from user input by combining semantic similarity with the
Context Resolution Matrix.

Unlike token prediction, this engine seeks the holistic meaning unit.
"""

from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

from .context_matrix import ContextResolutionMatrix, ContextObject
from .normalization_layer import NormalizationLayer


@dataclass
class Intent:
    """
    Represents a Pure Meaning from the corpus.
    
    Attributes:
        id: Unique identifier
        pure_text: The canonical representation
        description: Human-readable description
        required_context: Dictionary of contextual requirements
        examples: Example utterances
        embedding: Pre-computed semantic vector
    """
    id: str
    pure_text: str
    description: str
    required_context: Dict[str, Any]
    examples: List[str]
    embedding: Optional[NDArray[np.float32]] = None


@dataclass
class ResolvedIntent:
    """
    The Resolved Intent - the final recognized intent.
    
    Attributes:
        intent: The matched Intent object
        raw_similarity: Original cosine similarity score
        context_adjusted_score: Score after CRM adjustment
        active_factors: List of context factors that influenced the result
        confidence: Final confidence (0 to 1)
    """
    intent: Intent
    raw_similarity: float
    context_adjusted_score: float
    active_factors: List[str]
    confidence: float


class IntentEngine:
    """
    The Intent Engine - Extracts holistic intent from user input.
    
    This engine implements Holistic Sentence View by:
    1. Computing semantic similarity (Processing layer)
    2. Applying 12-factor contextual resolution (CRM)
    3. Revealing the flash of insight
    """
    
    def __init__(
        self,
        intents_path: str = "data/intents.json",
        model_name: str = "all-MiniLM-L6-v2",
        use_normalization: bool = True
    ) -> None:
        """
        Initialize the Intent Engine.
        
        Args:
            intents_path: Path to intents.json corpus
            model_name: Sentence-BERT model identifier
            use_normalization: Whether to apply input normalization
        """
        # Initialize components
        self.model = SentenceTransformer(model_name)
        self.crm = ContextResolutionMatrix()
        self.normalization = NormalizationLayer() if use_normalization else None
        
        # Load intents corpus
        self.intents: List[Intent] = []
        self.intent_embeddings: Optional[NDArray[np.float32]] = None
        self.load_intents(intents_path)
    
    def load_intents(self, path: str) -> None:
        """
        Load Pure Meanings corpus from JSON file.
        
        Args:
            path: Path to intents.json
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.intents = []
        for intent_dict in data['intents']:
            intent = Intent(
                id=intent_dict['id'],
                pure_text=intent_dict['pure_text'],
                description=intent_dict['description'],
                required_context=intent_dict.get('required_context', {}),
                examples=intent_dict.get('examples', [])
            )
            self.intents.append(intent)
        
        # Pre-compute embeddings for all pure_text entries
        self._compute_intent_embeddings()
    
    def _compute_intent_embeddings(self) -> None:
        """Pre-compute semantic vectors for all pure meanings."""
        pure_texts = [intent.pure_text for intent in self.intents]
        embeddings = self.model.encode(
            pure_texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        
        self.intent_embeddings = embeddings
        for i, intent in enumerate(self.intents):
            intent.embedding = embeddings[i]
    
    def _encode_input(self, text: str) -> Tuple[NDArray[np.float32], float]:
        """
        Encode user input to semantic vector.
        
        Applies input normalization if enabled.
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (embedding, distortion_score)
        """
        distortion_score = 0.0
        
        if self.normalization:
            # Apply input normalization
            normalized_text, distortion_score = self.normalization.normalize_to_pure_form(text)
            text_to_encode = normalized_text
        else:
            text_to_encode = text
        
        # Encode to semantic space
        embedding = self.model.encode(
            text_to_encode,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        
        return embedding, distortion_score
    
    @staticmethod
    def cosine_similarity(
        vec1: NDArray[np.float32],
        vec2: NDArray[np.float32]
    ) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0 to 1)
        """
        # Vectors are already normalized, so dot product = cosine similarity
        similarity = np.dot(vec1, vec2)
        return float(max(0.0, min(1.0, similarity)))
    
    def _calculate_raw_similarities(
        self,
        input_embedding: NDArray[np.float32]
    ) -> Dict[str, float]:
        """
        Calculate raw cosine similarities for all intents.
        
        Args:
            input_embedding: User input vector
            
        Returns:
            Dictionary mapping intent_id to similarity score
        """
        similarities = {}
        
        if self.intent_embeddings is not None:
            for i, intent in enumerate(self.intents):
                similarity = self.cosine_similarity(
                    input_embedding,
                    self.intent_embeddings[i]
                )
                similarities[intent.id] = similarity
        
        return similarities
    
    def _build_context_object(
        self,
        current_context: Union[Dict[str, Any], ContextObject, None],
        distortion_score: float
    ) -> ContextObject:
        """
        Build ContextObject from user-provided context.
        
        Args:
            current_context: Dictionary of context values or ContextObject
            distortion_score: Input distortion score
            
        Returns:
            ContextObject for CRM processing
        """
        from datetime import datetime
        
        # If already a ContextObject, update distortion and return
        if isinstance(current_context, ContextObject):
            if distortion_score > 0 and current_context.distortion is None:
                current_context.distortion = distortion_score
            return current_context
        
        # If None, create empty context
        if current_context is None:
            current_context = {}
        
        # Extract and map context values from dict (with backward compatibility for old Sanskrit keys)
        context = ContextObject(
            history=current_context.get('history') or current_context.get('sahacarya'),
            conflict=current_context.get('conflict') or current_context.get('virodhita'),
            purpose=current_context.get('purpose') or current_context.get('artha'),
            situation=current_context.get('situation') or current_context.get('prakarana'),
            indicator=current_context.get('indicator') or current_context.get('linga'),
            word_power=current_context.get('word_power') or current_context.get('shabda_samarthya'),
            propriety=current_context.get('propriety') or current_context.get('auciti'),
            location=current_context.get('location') or current_context.get('desa'),
            time=current_context.get('time') or current_context.get('kala') or datetime.now(),
            user_profile=current_context.get('user_profile') or current_context.get('vyakti'),
            intonation=current_context.get('intonation') or current_context.get('svara'),
            distortion=distortion_score if distortion_score > 0 else None
        )
        
        return context
    
    def resolve_intent(
        self,
        user_input: str,
        current_context: Union[Dict[str, Any], ContextObject, None] = None,
        return_top_k: int = 3
    ) -> List[ResolvedIntent]:
        """
        Resolve the Vākyasphoṭa (Total Intent) from user input.
        
        This is the main engine method that combines:
        1. Semantic similarity (raw AI scores)
        2. Contextual resolution (12-factor CRM)
        3. Produces the "Flash of Insight"
        
        Args:
            user_input: User's voice command or text
            current_context: Dictionary of contextual factors
            return_top_k: Number of top candidates to return
            
        Returns:
            List of ResolvedIntent objects, sorted by confidence
            
        Example:
            >>> context = {"location": "nature", "history": ["fishing"]}
            >>> results = engine.resolve_intent("take me to the bank", context)
            >>> results[0].intent.id  # "river_bank" (not "financial_bank")
        """
        if current_context is None:
            current_context = {}
        
        # Step 1: Encode input (with Distortion handling)
        input_embedding, distortion_score = self._encode_input(user_input)
        
        # Step 2: Calculate raw semantic similarities
        raw_similarities = self._calculate_raw_similarities(input_embedding)
        
        # Step 3: Build context object for CRM
        context_obj = self._build_context_object(current_context, distortion_score)
        
        # Step 4: Apply Context Resolution Matrix
        # This is where Sphota differs from standard AI!
        context_adjusted_scores = self.crm.resolve_intent(
            base_scores=raw_similarities,
            context=context_obj
        )
        
        # Step 5: Get active factors for explanation
        active_factors = self.crm.get_active_factors(context_obj)
        
        # Step 6: Create ResolvedIntent objects
        resolved_intents: List[ResolvedIntent] = []
        
        for intent in self.intents:
            intent_id = intent.id
            resolved = ResolvedIntent(
                intent=intent,
                raw_similarity=raw_similarities[intent_id],
                context_adjusted_score=context_adjusted_scores[intent_id],
                active_factors=active_factors,
                confidence=context_adjusted_scores[intent_id]
            )
            resolved_intents.append(resolved)
        
        # Step 7: Sort by confidence and return top K
        resolved_intents.sort(key=lambda x: x.confidence, reverse=True)
        
        return resolved_intents[:return_top_k]
    
    def explain_resolution(
        self,
        user_input: str,
        current_context: Union[Dict[str, Any], ContextObject, None] = None
    ) -> Dict[str, Any]:
        """
        Generate detailed explanation of intent resolution process.
        
        Useful for debugging and demonstrating the CRM's effect.
        
        Args:
            user_input: User input text
            current_context: Context dictionary or ContextObject
            
        Returns:
            Detailed explanation dictionary
        """
        # Handle different context types
        if isinstance(current_context, ContextObject):
            # Convert ContextObject to dict for explanation
            context_dict = {
                'history': current_context.history,
                'conflict': current_context.conflict,
                'purpose': current_context.purpose,
                'situation': current_context.situation,
                'indicator': current_context.indicator,
                'word_power': current_context.word_power,
                'propriety': current_context.propriety,
                'location': current_context.location,
                'time': current_context.time,
                'user_profile': current_context.user_profile,
                'intonation': current_context.intonation,
                'distortion': current_context.distortion
            }
            context_obj = current_context
        elif current_context is None:
            context_dict = {}
            context_obj = ContextObject()
        else:
            context_dict = current_context
            context_obj = None  # Will be built later
        
        # Perform resolution
        input_embedding, distortion_score = self._encode_input(user_input)
        raw_similarities = self._calculate_raw_similarities(input_embedding)
        
        if context_obj is None:
            context_obj = self._build_context_object(context_dict, distortion_score)
        
        context_adjusted = self.crm.resolve_intent(raw_similarities, context_obj)
        
        # Generate explanation using CRM
        crm_explanation = self.crm.explain_resolution(
            base_scores=raw_similarities,
            resolved_scores=context_adjusted,
            context=context_obj
        )
        
        # Add input processing details
        explanation = {
            "input": {
                "original": user_input,
                "distortion_score": distortion_score,
            },
            "context": {
                "provided": context_dict,
                "active_factors": crm_explanation["active_factors"]
            },
            "resolution": {
                "score_changes": crm_explanation["score_changes"],
                "top_boosts": crm_explanation["top_boosts"],
                "top_penalties": crm_explanation["top_penalties"]
            }
        }
        
        # Add normalization details if Distortion was used
        if self.distortion and distortion_score > 0:
            normalized, _ = self.distortion.normalize_to_pure_form(user_input)
            explanation["input"]["normalized"] = normalized
        
        return explanation
    
    def get_intent_by_id(self, intent_id: str) -> Optional[Intent]:
        """
        Retrieve an intent by its ID.
        
        Args:
            intent_id: Intent identifier
            
        Returns:
            Intent object or None
        """
        for intent in self.intents:
            if intent.id == intent_id:
                return intent
        return None
    
    def get_all_intents(self) -> List[Intent]:
        """Get all loaded intents."""
        return self.intents.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model and corpus.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            "model_name": self.model.get_sentence_embedding_dimension(),
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "intent_count": len(self.intents),
            "apabhramsa_enabled": self.distortion is not None,
            "crm_factors": list(self.crm.weights.keys())
        }
