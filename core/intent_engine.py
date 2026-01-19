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

# Try to import ChromaDB version, fallback to simple version
try:
    from .fast_memory import FastMemory, MemoryCandidate, boost_candidates_with_memory  # type: ignore
except ImportError:
    # ChromaDB not available, use simple in-memory version
    from .fast_memory_simple import FastMemory, MemoryCandidate, boost_candidates_with_memory  # type: ignore


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


@dataclass
class SemanticCandidate:
    """
    Candidate intent from Stage 1 (Semantic Flash / Vector Search).
    
    Represents a potential match found through vector similarity search.
    
    Attributes:
        candidate_intent: The Intent object found by vector search
        semantic_similarity: Cosine similarity score (0 to 1)
        source: Origin of candidate ("vector_search" or "memory_boost")
    """
    candidate_intent: Intent
    semantic_similarity: float
    source: str  # "vector_search" or "memory_boost"


@dataclass
class VerifiedIntent:
    """
    Verified Intent - result of the two-stage Hybrid Architecture.
    
    Stage 1 (Semantic Flash): Vector search returns candidates
    Stage 2 (Deterministic Check): Hard Stop rules discard invalid candidates,
                                    context factors boost valid ones
    
    Attributes:
        intent: The final selected Intent
        semantic_candidates: List of candidates from Stage 1
        stage_1_passed: Whether semantic matching succeeded
        stage_2_passed: Whether deterministic validation passed
        fallback_used: Whether fallback mechanism was triggered
        confidence: Final confidence (0 to 1)
        context_adjusted_score: Score after CRM application
        active_factors: Context factors that influenced resolution
    """
    intent: Intent
    semantic_candidates: List[SemanticCandidate]
    stage_1_passed: bool
    stage_2_passed: bool
    fallback_used: bool
    confidence: float
    context_adjusted_score: float
    active_factors: List[str]


class IntentEngine:
    """
    The Intent Engine - Extracts holistic intent from user input.
    
    This engine implements Holistic Sentence View by:
    1. Computing semantic similarity (Processing layer)
    2. Querying Fast Memory for similar past intents (NEW!)
    3. Applying 12-factor contextual resolution (CRM)
    4. Revealing the flash of insight
    """
    
    def __init__(
        self,
        intents_path: str = "data/intents.json",
        model_name: str = "all-MiniLM-L6-v2",
        use_normalization: bool = True,
        use_fast_memory: bool = True,
        memory_boost_weight: float = 0.2
    ) -> None:
        """
        Initialize the Intent Engine.
        
        Args:
            intents_path: Path to intents.json corpus
            model_name: Sentence-BERT model identifier
            use_normalization: Whether to apply input normalization
            use_fast_memory: Whether to enable Fast Memory layer
            memory_boost_weight: Weight for Fast Memory boost (0.0 to 1.0)
        """
        # Initialize components
        self.model = SentenceTransformer(model_name)
        self.crm = ContextResolutionMatrix()
        self.normalization = NormalizationLayer() if use_normalization else None
        
        # Initialize Fast Memory layer (Vector DB)
        self.fast_memory: Any = None  # Type varies based on which implementation loads
        self.use_fast_memory = use_fast_memory
        self.memory_boost_weight = memory_boost_weight
        
        if use_fast_memory:
            self.fast_memory = FastMemory()
        
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
    
    def _get_semantic_candidates(
        self,
        user_input: str,
        input_embedding: NDArray[np.float32]
    ) -> List[SemanticCandidate]:
        """
        Stage 1: Semantic Flash - Retrieve candidate intents via vector search.
        
        This stage performs semantic similarity search to find the top candidates
        that might match the user's intent based on meaning similarity.
        
        Args:
            user_input: Original user input text
            input_embedding: Pre-computed semantic vector of input
            
        Returns:
            List of SemanticCandidate objects sorted by semantic_similarity (descending)
        """
        candidates: List[SemanticCandidate] = []
        
        # Get raw similarities from all intents
        raw_similarities = self._calculate_raw_similarities(input_embedding)
        
        # Query Fast Memory for memory-boosted candidates
        if self.use_fast_memory and self.fast_memory:
            memory_candidates = self.fast_memory.retrieve_candidates(
                user_input=user_input,
                embedding=input_embedding,
                top_k=5
            )
            
            # Convert memory candidates to SemanticCandidate objects
            for mem_candidate in memory_candidates:
                intent = self.get_intent_by_id(mem_candidate.intent_id)
                if intent:
                    # Use memory candidate's similarity score
                    candidate = SemanticCandidate(
                        candidate_intent=intent,
                        semantic_similarity=mem_candidate.similarity_score,
                        source="memory_boost"
                    )
                    candidates.append(candidate)
        
        # Add top 5 vector search results (not already in memory candidates)
        memory_intent_ids = {c.candidate_intent.id for c in candidates}
        
        # Sort all intents by similarity
        sorted_intents = sorted(
            raw_similarities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Add top candidates that aren't already from memory
        for intent_id, similarity in sorted_intents[:5]:
            if intent_id not in memory_intent_ids:
                intent = self.get_intent_by_id(intent_id)
                if intent:
                    candidate = SemanticCandidate(
                        candidate_intent=intent,
                        semantic_similarity=similarity,
                        source="vector_search"
                    )
                    candidates.append(candidate)
        
        # Sort all candidates by similarity (highest first)
        candidates.sort(key=lambda c: c.semantic_similarity, reverse=True)
        
        return candidates
    
    def _apply_deterministic_check(
        self,
        semantic_candidates: List[SemanticCandidate],
        current_context: Union[Dict[str, Any], ContextObject, None],
        distortion_score: float
    ) -> Tuple[Optional[VerifiedIntent], bool]:
        """
        Stage 2: Deterministic Check - Validate and boost candidates via CRM.
        
        This stage applies hard constraints and context-based scoring to
        determine if semantic candidates are valid in the current context.
        
        Hard Stop Rules (discard candidate if):
        - Conflict markers contradict the intent
        - Required location context is missing/mismatched
        - User profile incompatibility
        
        Context Boost (amplify confidence for valid candidates):
        - Purpose alignment
        - Situational relevance
        - Historical patterns
        
        Args:
            semantic_candidates: Candidates from Stage 1
            current_context: Current contextual factors
            distortion_score: Input distortion/slang level
            
        Returns:
            Tuple of (VerifiedIntent or None, stage_2_passed: bool)
        """
        if not semantic_candidates:
            return None, False
        
        # Build context object
        context_obj = self._build_context_object(current_context, distortion_score)
        
        # Apply CRM to get active factors
        active_factors = self.crm.get_active_factors(context_obj)
        
        # Track which candidates pass Hard Stop rules
        validated_candidates: List[Tuple[SemanticCandidate, float]] = []
        
        for candidate in semantic_candidates:
            intent_id = candidate.candidate_intent.id
            base_score = candidate.semantic_similarity
            
            # === HARD STOP RULES ===
            discard = False
            
            # Hard Stop 1: Conflict Check - Check if context conflicts discard this intent
            if context_obj.conflict:
                for conflict_marker in context_obj.conflict:
                    # If marker indicates cancellation/stopping and intent is create/start
                    if conflict_marker.lower() in ['cancel', 'stop', 'close', 'no']:
                        if any(kw in intent_id.lower() for kw in ['create', 'start', 'begin', 'open']):
                            discard = True
                            break
            
            # Hard Stop 2: Location Mismatch - Check required context vs provided context
            if candidate.candidate_intent.required_context.get('location'):
                required_location = candidate.candidate_intent.required_context['location']
                if context_obj.location and context_obj.location.lower() != required_location.lower():
                    # Location mismatch - only discard if it's explicitly required
                    if candidate.candidate_intent.required_context.get('location_required', False):
                        discard = True
            
            # Hard Stop 3: User Profile Incompatibility
            if candidate.candidate_intent.required_context.get('user_profile'):
                required_profile = candidate.candidate_intent.required_context['user_profile']
                if context_obj.user_profile and context_obj.user_profile != required_profile:
                    discard = True
            
            # If candidate passes all Hard Stop rules, apply context boosts
            if not discard:
                boosted_score = base_score
                
                # Context Boost 1: Purpose alignment
                if context_obj.purpose:
                    if candidate.candidate_intent.required_context.get('purpose') == context_obj.purpose:
                        boosted_score += self.crm.weights.get('purpose', 0.20)
                
                # Context Boost 2: Situational relevance
                if context_obj.situation:
                    if candidate.candidate_intent.required_context.get('situation') == context_obj.situation:
                        boosted_score += self.crm.weights.get('situation', 0.15)
                
                # Context Boost 3: Location bonus (if location is helpful, not required)
                if context_obj.location:
                    if candidate.candidate_intent.required_context.get('location') == context_obj.location:
                        boosted_score += self.crm.weights.get('location', 0.18) * 0.5
                
                # Context Boost 4: History/Association bonus
                if context_obj.history and candidate.candidate_intent.required_context.get('associated_intents'):
                    associated = candidate.candidate_intent.required_context['associated_intents']
                    if any(h in associated for h in context_obj.history):
                        boosted_score += self.crm.weights.get('history', 0.15)
                
                # Ensure score stays in [0, 1] range
                boosted_score = max(0.0, min(1.0, boosted_score))
                
                validated_candidates.append((candidate, boosted_score))
        
        # If no candidates passed Hard Stop rules, return None
        if not validated_candidates:
            return None, False
        
        # Select best candidate (highest boosted score)
        best_candidate, best_score = max(validated_candidates, key=lambda x: x[1])
        
        # Create VerifiedIntent
        verified = VerifiedIntent(
            intent=best_candidate.candidate_intent,
            semantic_candidates=semantic_candidates,
            stage_1_passed=True,
            stage_2_passed=True,
            fallback_used=False,
            confidence=best_score,
            context_adjusted_score=best_score,
            active_factors=active_factors
        )
        
        return verified, True
    
    def resolve_with_hybrid_logic(
        self,
        user_input: str,
        current_context: Union[Dict[str, Any], ContextObject, None] = None
    ) -> VerifiedIntent:
        """
        Main Hybrid Architecture: Two-Stage Resolution Process.
        
        Combines semantic search (Stage 1: Flash of Insight) with
        deterministic validation (Stage 2: Context Check).
        
        Flow:
        1. Stage 1 (Semantic Flash): Vector search returns Top 5 candidates
        2. Stage 2 (Deterministic Check): Hard Stop rules discard invalid,
                                          context boosts valid candidates
        3. Fallback: If confidence < 0.6, return FallbackIntent ("uncertain")
        
        Args:
            user_input: User's voice command or text
            current_context: Dictionary or ContextObject with contextual factors
            
        Returns:
            VerifiedIntent with stage tracking and confidence score
            
        Example:
            >>> context = {"location": "Bank", "history": ["atm_search"]}
            >>> result = engine.resolve_with_hybrid_logic("I need dough", context)
            >>> # Stage 1: Finds "I need money" via vector search
            >>> # Stage 2: Validates at Bank location (location mismatch discarded)
            >>> result.intent.id  # "withdraw_money"
            >>> result.stage_1_passed  # True
            >>> result.stage_2_passed  # True
            >>> result.confidence  # 0.85
        """
        if current_context is None:
            current_context = {}
        
        # Stage 1: Encode input
        input_embedding, distortion_score = self._encode_input(user_input)
        
        # Stage 1: Get semantic candidates (Top 5 from vector search)
        semantic_candidates = self._get_semantic_candidates(user_input, input_embedding)
        
        # If no candidates found at all, return fallback
        if not semantic_candidates:
            fallback_intent = self._create_fallback_intent(
                user_input=user_input,
                reason="no_semantic_candidates",
                confidence=0.0
            )
            return fallback_intent
        
        # Stage 2: Apply deterministic check (Hard Stop rules + context boost)
        verified, stage_2_passed = self._apply_deterministic_check(
            semantic_candidates=semantic_candidates,
            current_context=current_context,
            distortion_score=distortion_score
        )
        
        # If Stage 2 validation fails, or confidence is below threshold
        if not stage_2_passed or not verified or verified.confidence < 0.6:
            fallback_intent = self._create_fallback_intent(
                user_input=user_input,
                reason="low_confidence" if verified and verified.confidence < 0.6 else "stage_2_failed",
                confidence=verified.confidence if verified else 0.0,
                stage_1_passed=True if semantic_candidates else False
            )
            return fallback_intent
        
        # Success: Return VerifiedIntent
        return verified
    
    def _create_fallback_intent(
        self,
        user_input: str,
        reason: str,
        confidence: float,
        stage_1_passed: bool = False
    ) -> VerifiedIntent:
        """
        Create a FallbackIntent when confidence is too low.
        
        Args:
            user_input: Original user input
            reason: Why fallback was triggered ("no_semantic_candidates", "low_confidence", "stage_2_failed")
            confidence: Best confidence found (before fallback)
            stage_1_passed: Whether Stage 1 found candidates
            
        Returns:
            VerifiedIntent with special fallback marker
        """
        # Create a special "uncertain" intent
        fallback_intent_obj = Intent(
            id="__fallback_uncertain__",
            pure_text="I'm not certain about your intent. Please rephrase.",
            description="Fallback response when confidence is too low",
            required_context={},
            examples=[]
        )
        
        # Return as VerifiedIntent with fallback flag
        return VerifiedIntent(
            intent=fallback_intent_obj,
            semantic_candidates=[],
            stage_1_passed=stage_1_passed,
            stage_2_passed=False,
            fallback_used=True,
            confidence=confidence,
            context_adjusted_score=confidence,
            active_factors=[reason]
        )
    
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
        return_top_k: int = 3,
        store_in_memory: bool = True
    ) -> List[ResolvedIntent]:
        """
        Resolve the Vākyasphoṭa (Total Intent) from user input.
        
        Uses the new Hybrid Architecture with two-stage resolution:
        1. Stage 1 (Semantic Flash): Vector search returns Top 5 candidates
        2. Stage 2 (Deterministic Check): Hard Stop rules + context boost
        3. Fallback: Return uncertainty intent if confidence < 0.6
        
        This maintains backward compatibility by returning List[ResolvedIntent]
        while using the new hybrid logic internally.
        
        Args:
            user_input: User's voice command or text
            current_context: Dictionary of contextual factors
            return_top_k: Number of top candidates to return
            store_in_memory: Whether to store this resolution in Fast Memory
            
        Returns:
            List of ResolvedIntent objects, sorted by confidence
            
        Example:
            >>> context = {"location": "Bank", "history": ["atm_search"]}
            >>> results = engine.resolve_intent("I need dough", context)
            >>> results[0].intent.id  # "withdraw_money" (validated via Stage 2)
        """
        if current_context is None:
            current_context = {}
        
        # Use the new Hybrid Architecture
        verified_intent = self.resolve_with_hybrid_logic(user_input, current_context)
        
        # Convert VerifiedIntent to ResolvedIntent for backward compatibility
        resolved = ResolvedIntent(
            intent=verified_intent.intent,
            raw_similarity=0.0,  # Not used in hybrid architecture
            context_adjusted_score=verified_intent.context_adjusted_score,
            active_factors=verified_intent.active_factors,
            confidence=verified_intent.confidence
        )
        
        # Store in Fast Memory if enabled and not a fallback
        if store_in_memory and not verified_intent.fallback_used and self.use_fast_memory and self.fast_memory:
            input_embedding, _ = self._encode_input(user_input)
            self.fast_memory.add_memory(
                user_input=user_input,
                resolved_intent_id=resolved.intent.id,
                embedding=input_embedding,
                metadata={
                    "confidence": resolved.confidence,
                    "context_location": current_context.get('location') if isinstance(current_context, dict) else None,
                    "hybrid_stage_1": verified_intent.stage_1_passed,
                    "hybrid_stage_2": verified_intent.stage_2_passed
                }
            )
        
        # Return as list for backward compatibility
        return [resolved]
    
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
        
        # Add normalization details if Normalization was used
        if self.normalization and distortion_score > 0:
            normalized, _ = self.normalization.normalize_to_pure_form(user_input)
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
        info = {
            "model_name": self.model.get_sentence_embedding_dimension(),
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "intent_count": len(self.intents),
            "apabhramsa_enabled": self.normalization is not None,
            "crm_factors": list(self.crm.weights.keys()),
            "fast_memory_enabled": self.use_fast_memory
        }
        
        # Add Fast Memory stats if enabled
        if self.use_fast_memory and self.fast_memory:
            info["fast_memory_stats"] = self.fast_memory.get_stats()
        
        return info
    
    def get_memory_candidates(
        self,
        user_input: str,
        top_k: int = 3
    ) -> List[MemoryCandidate]:
        """
        Query Fast Memory without performing full intent resolution.
        
        Useful for debugging and understanding what the memory layer retrieves.
        
        Args:
            user_input: User utterance
            top_k: Number of candidates to retrieve
            
        Returns:
            List of MemoryCandidate objects
        """
        if not self.use_fast_memory or not self.fast_memory:
            return []
        
        input_embedding, _ = self._encode_input(user_input)
        return self.fast_memory.retrieve_candidates(
            user_input=user_input,
            embedding=input_embedding,
            top_k=top_k
        )
    
    def clear_fast_memory(self) -> None:
        """Clear all stored memories in Fast Memory layer."""
        if self.fast_memory:
            self.fast_memory.clear_memory()
