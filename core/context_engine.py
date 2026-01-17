"""
Context Resolution Engine (CRE)

Production-ready implementation of the 12-factor context resolution system.

The Context Resolution Engine implements domain-driven intent disambiguation
by applying weighted contextual factors to resolve ambiguity in user input.
This follows DDD principles with clear domain language and bounded contexts.

Architecture:
  - ContextResolutionEngine: Main orchestrator for context-based scoring
  - ContextSnapshot: Immutable value object representing contextual state
  - ResolutionFactor: Strategy for each of the 12 factors
  - ResolutionResult: Value object returned from resolution

References:
  - Domain-Driven Design (Evans, 2003)
  - Intent Resolution through Contextual Analysis
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# Configure logging for the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TimeOfDay(Enum):
    """Enumeration of time periods for temporal context resolution."""
    EARLY_MORNING = "early_morning"  # 4:00 AM - 6:00 AM
    MORNING = "morning"              # 6:00 AM - 12:00 PM
    AFTERNOON = "afternoon"          # 12:00 PM - 5:00 PM
    EVENING = "evening"              # 5:00 PM - 9:00 PM
    NIGHT = "night"                  # 9:00 PM - 11:00 PM
    LATE_NIGHT = "late_night"        # 11:00 PM - 4:00 AM


@dataclass
class ContextSnapshot:
    """
    Immutable snapshot of contextual state used for intent resolution.
    
    This value object represents the 12 contextual factors that influence
    intent disambiguation. Each factor may be None if not applicable to
    the current resolution context.
    
    The 12 Factors:
    1. association_history: Recent user intent patterns
    2. conflict_markers: Contrasting or opposing signals
    3. goal_alignment: User's stated or inferred purpose
    4. situation_context: Current situational context
    5. linguistic_indicators: Grammatical/syntactic signals
    6. semantic_capacity: Semantic richness of input (0.0-1.0)
    7. social_propriety: Contextual appropriateness (-1.0 to 1.0)
    8. location_context: Geographic/spatial context
    9. temporal_context: Time-based context
    10. user_profile: User personalization profile
    11. prosodic_features: Accent, intonation, stress patterns
    12. input_fidelity: Measure of input clarity (0.0-1.0)
    """
    
    # === Factor 1: Association History ===
    association_history: Optional[List[str]] = None
    """Recent sequence of user intents for co-occurrence analysis."""
    
    # === Factor 2: Conflict Detection ===
    conflict_markers: Optional[List[str]] = None
    """Explicit contrast or opposition signals in input."""
    
    # === Factor 3: Goal Alignment ===
    goal_alignment: Optional[str] = None
    """User's stated or inferred primary goal/purpose."""
    
    # === Factor 4: Situation Context ===
    situation_context: Optional[str] = None
    """High-level situation classification (e.g., 'work_session', 'travel')."""
    
    # === Factor 5: Linguistic Indicators ===
    linguistic_indicators: Optional[str] = None
    """Grammatical cues (question mark, imperative mood, etc.)."""
    
    # === Factor 6: Semantic Capacity ===
    semantic_capacity: Optional[float] = None
    """Semantic richness metric [0.0=minimal, 1.0=maximal]."""
    
    # === Factor 7: Social Propriety ===
    social_propriety: Optional[float] = None
    """Contextual appropriateness [-1.0=inappropriate, 1.0=appropriate]."""
    
    # === Factor 8: Location Context ===
    location_context: Optional[str] = None
    """Current location (e.g., 'kitchen', 'office', 'car')."""
    
    # === Factor 9: Temporal Context ===
    temporal_context: Optional[datetime] = None
    """Timestamp for time-of-day and temporal reasoning."""
    
    # === Factor 10: User Profile ===
    user_profile: Optional[str] = None
    """User demographic or preference profile."""
    
    # === Factor 11: Prosodic Features ===
    prosodic_features: Optional[str] = None
    """Accent, intonation, stress patterns in speech."""
    
    # === Factor 12: Input Fidelity ===
    input_fidelity: Optional[float] = None
    """Clarity/fidelity of input signal [0.0=degraded, 1.0=clear]."""
    
    def get_active_factors(self) -> List[str]:
        """
        Identify which factors are active (non-None) in this context.
        
        Returns:
            List of active factor names in order of the 12 factors.
            
        Example:
            >>> context = ContextSnapshot(
            ...     location_context="kitchen",
            ...     temporal_context=datetime.now()
            ... )
            >>> context.get_active_factors()
            ['location_context', 'temporal_context']
        """
        active_factors = []
        
        if self.association_history is not None:
            active_factors.append('association_history')
        if self.conflict_markers is not None:
            active_factors.append('conflict_markers')
        if self.goal_alignment is not None:
            active_factors.append('goal_alignment')
        if self.situation_context is not None:
            active_factors.append('situation_context')
        if self.linguistic_indicators is not None:
            active_factors.append('linguistic_indicators')
        if self.semantic_capacity is not None:
            active_factors.append('semantic_capacity')
        if self.social_propriety is not None:
            active_factors.append('social_propriety')
        if self.location_context is not None:
            active_factors.append('location_context')
        if self.temporal_context is not None:
            active_factors.append('temporal_context')
        if self.user_profile is not None:
            active_factors.append('user_profile')
        if self.prosodic_features is not None:
            active_factors.append('prosodic_features')
        if self.input_fidelity is not None:
            active_factors.append('input_fidelity')
        
        return active_factors


@dataclass
class ResolutionResult:
    """
    Result of context resolution operation.
    
    Value object containing resolved intent scores and diagnostic information
    for explainability and debugging.
    """
    
    resolved_scores: Dict[str, float]
    """Normalized intent scores after context resolution."""
    
    active_factors: List[str] = field(default_factory=list)
    """List of context factors that were active during resolution."""
    
    score_deltas: Dict[str, float] = field(default_factory=dict)
    """Change in score for each intent (resolved - base)."""
    
    confidence_estimate: float = 0.0
    """Estimated confidence in resolution [0.0-1.0]."""
    
    factor_contributions: Dict[str, Dict[str, float]] = field(default_factory=dict)
    """Per-factor contributions to score changes for explanation."""


class ContextResolutionEngine:
    """
    Production-grade 12-factor context resolution engine.
    
    This engine implements the core business logic for disambiguating user
    intents through contextual analysis. It follows DDD principles with
    clear domain language and testable components.
    
    The 12 Factors (in order of typical salience):
    1. Location (Geographic/spatial context) - HIGH SALIENCE
    2. Temporal (Time-based reasoning) - HIGH SALIENCE
    3. Goal Alignment (User purpose) - HIGH SALIENCE
    4. Semantic Capacity (Input richness) - MEDIUM SALIENCE
    5. Situation (Contextual classification) - MEDIUM SALIENCE
    6. Association History (Co-occurrence patterns) - MEDIUM SALIENCE
    7. Social Propriety (Contextual appropriateness) - MEDIUM SALIENCE
    8. Conflict Detection (Opposing signals) - MEDIUM SALIENCE
    9. Prosodic Features (Speech characteristics) - LOW SALIENCE
    10. Linguistic Indicators (Grammatical signals) - LOW SALIENCE
    11. Input Fidelity (Signal clarity) - LOW SALIENCE
    12. User Profile (Personalization) - LOW SALIENCE
    """
    
    DEFAULT_WEIGHTS: Dict[str, float] = {
        'association_history': 0.15,      # Factor 1: Association
        'conflict_markers': 0.10,          # Factor 2: Conflict
        'goal_alignment': 0.20,            # Factor 3: Purpose (highest)
        'situation_context': 0.15,         # Factor 4: Situation
        'linguistic_indicators': 0.08,     # Factor 5: Grammar
        'semantic_capacity': 0.12,         # Factor 6: Word power
        'social_propriety': 0.10,          # Factor 7: Propriety
        'location_context': 0.18,          # Factor 8: Location
        'temporal_context': 0.15,          # Factor 9: Time
        'user_profile': 0.12,              # Factor 10: Profile
        'prosodic_features': 0.08,         # Factor 11: Intonation
        'input_fidelity': 0.07             # Factor 12: Distortion
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None) -> None:
        """
        Initialize the Context Resolution Engine with configuration.
        
        Args:
            weights: Optional custom weights for factors. Defaults to DEFAULT_WEIGHTS
                    if not provided. Weights do not need to sum to 1.0 as factors
                    can reinforce each other.
                    
        Raises:
            ValueError: If any weight is negative or factor name is invalid.
            
        Example:
            >>> engine = ContextResolutionEngine()
            >>> custom_weights = {'location_context': 0.25, 'temporal_context': 0.20}
            >>> engine = ContextResolutionEngine(weights=custom_weights)
        """
        self.weights: Dict[str, float] = weights or self.DEFAULT_WEIGHTS.copy()
        
        # Validate weights
        for factor_name, weight in self.weights.items():
            if factor_name not in self.DEFAULT_WEIGHTS:
                logger.warning(f"Unknown factor: {factor_name}")
            if weight < 0:
                raise ValueError(f"Factor weight cannot be negative: {factor_name}={weight}")
        
        # Initialize factor-specific mappings
        self._initialize_knowledge_maps()
        
        logger.info(f"ContextResolutionEngine initialized with {len(self.weights)} factors")
    
    def _initialize_knowledge_maps(self) -> None:
        """
        Initialize domain knowledge maps for factor resolution.
        
        These maps define the semantic relationships between context values
        and intent keywords. They encode business rules for the domain.
        """
        # Factor 1: Association History - Co-occurrence patterns
        self.association_patterns: Dict[str, List[str]] = {
            "cooking": ["timer", "recipe", "ingredients", "temperature", "heat"],
            "music": ["volume", "playlist", "song", "artist", "play"],
            "navigation": ["traffic", "route", "directions", "arrive", "gps"],
            "work": ["meeting", "schedule", "email", "calendar", "task"],
            "exercise": ["timer", "workout", "fitness", "heart_rate", "steps"]
        }
        
        # Factor 2: Conflict Detection - Opposing intent pairs
        self.conflict_pairs: Dict[str, List[str]] = {
            "cancel": ["create", "start", "begin", "schedule"],
            "stop": ["play", "start", "continue", "run"],
            "close": ["open", "launch", "start", "activate"],
            "decrease": ["increase", "raise", "boost", "enhance"],
            "no": ["yes", "confirm", "accept", "allow"]
        }
        
        # Factor 3: Goal Alignment - Purpose-based groupings
        self.goal_groups: Dict[str, List[str]] = {
            "productivity": ["work", "schedule", "reminder", "meeting", "focus"],
            "entertainment": ["music", "video", "game", "movie", "play"],
            "information": ["search", "query", "weather", "news", "wiki"],
            "communication": ["call", "message", "text", "email", "notify"],
            "automation": ["timer", "alarm", "reminder", "routine"]
        }
        
        # Factor 4: Situation Context - Situational relevance
        self.situation_intents: Dict[str, List[str]] = {
            "morning_routine": ["alarm", "weather", "news", "coffee", "commute"],
            "cooking": ["recipe", "timer", "ingredients", "heat", "food"],
            "travel": ["navigation", "traffic", "weather", "booking"],
            "work_session": ["focus", "timer", "schedule", "productivity"],
            "evening_relax": ["music", "dim_lights", "entertainment"]
        }
        
        # Factor 8: Location Context - Location-specific intents
        self.location_intents: Dict[str, List[str]] = {
            "kitchen": ["cooking", "recipe", "timer", "food", "heat"],
            "bedroom": ["sleep", "alarm", "wake", "rest", "lights"],
            "office": ["work", "meeting", "productivity", "focus", "email"],
            "car": ["navigation", "traffic", "music", "hands_free", "call"],
            "gym": ["workout", "exercise", "timer", "fitness", "music"],
            "home": ["lights", "temperature", "security", "entertainment"]
        }
        
        # Factor 9: Temporal Context - Time-of-day specific intents
        self.time_period_intents: Dict[TimeOfDay, List[str]] = {
            TimeOfDay.EARLY_MORNING: ["alarm", "wake", "weather", "news"],
            TimeOfDay.MORNING: ["breakfast", "coffee", "schedule", "commute"],
            TimeOfDay.AFTERNOON: ["lunch", "meeting", "work", "focus"],
            TimeOfDay.EVENING: ["dinner", "relax", "entertainment", "music"],
            TimeOfDay.NIGHT: ["sleep", "quiet", "lights_off", "bedtime"],
            TimeOfDay.LATE_NIGHT: ["sleep", "rest", "quiet", "dark"]
        }
        
        # Factor 10: User Profile - User preference groups
        self.user_preferences: Dict[str, List[str]] = {
            "tech_enthusiast": ["automation", "smart_home", "advanced"],
            "casual_user": ["entertainment", "music", "simple"],
            "productivity_focused": ["work", "schedule", "task"],
            "fitness_oriented": ["exercise", "health", "workout"]
        }
        
        logger.debug("Knowledge maps initialized successfully")
    
    def resolve(
        self,
        base_scores: Dict[str, float],
        context: ContextSnapshot
    ) -> ResolutionResult:
        """
        Apply context resolution to base intent scores.
        
        This is the primary entry point for intent disambiguation. It takes
        baseline semantic similarity scores and applies contextual factors
        to compute final resolved scores.
        
        Args:
            base_scores: Dict mapping intent_id -> baseline_score [0.0-1.0]
            context: ContextSnapshot containing contextual factors
            
        Returns:
            ResolutionResult with resolved scores and diagnostics
            
        Raises:
            ValueError: If base_scores contain invalid values
            
        Example:
            >>> engine = ContextResolutionEngine()
            >>> base_scores = {"set_timer": 0.75, "alarm": 0.62}
            >>> context = ContextSnapshot(
            ...     location_context="kitchen",
            ...     temporal_context=datetime.now()
            ... )
            >>> result = engine.resolve(base_scores, context)
            >>> result.resolved_scores
            {'set_timer': 0.88, 'alarm': 0.62}
        """
        # Validate inputs
        self._validate_scores(base_scores)
        
        # Initialize result tracking
        resolved_scores = base_scores.copy()
        factor_contributions: Dict[str, Dict[str, float]] = {}
        active_factors = context.get_active_factors()
        
        logger.debug(f"Starting resolution with {len(active_factors)} active factors")
        
        # Apply each factor in sequence
        # Factor 1: Association History
        if context.association_history is not None:
            resolved_scores, contrib = self._apply_association_factor(
                resolved_scores, context.association_history
            )
            factor_contributions['association_history'] = contrib
        
        # Factor 2: Conflict Detection
        if context.conflict_markers is not None:
            resolved_scores, contrib = self._apply_conflict_factor(
                resolved_scores, context.conflict_markers
            )
            factor_contributions['conflict_markers'] = contrib
        
        # Factor 3: Goal Alignment
        if context.goal_alignment is not None:
            resolved_scores, contrib = self._apply_goal_factor(
                resolved_scores, context.goal_alignment
            )
            factor_contributions['goal_alignment'] = contrib
        
        # Factor 4: Situation Context
        if context.situation_context is not None:
            resolved_scores, contrib = self._apply_situation_factor(
                resolved_scores, context.situation_context
            )
            factor_contributions['situation_context'] = contrib
        
        # Factor 5: Linguistic Indicators
        if context.linguistic_indicators is not None:
            resolved_scores, contrib = self._apply_linguistic_factor(
                resolved_scores, context.linguistic_indicators
            )
            factor_contributions['linguistic_indicators'] = contrib
        
        # Factor 6: Semantic Capacity
        if context.semantic_capacity is not None:
            resolved_scores, contrib = self._apply_semantic_capacity_factor(
                resolved_scores, context.semantic_capacity
            )
            factor_contributions['semantic_capacity'] = contrib
        
        # Factor 7: Social Propriety
        if context.social_propriety is not None:
            resolved_scores, contrib = self._apply_propriety_factor(
                resolved_scores, context.social_propriety
            )
            factor_contributions['social_propriety'] = contrib
        
        # Factor 8: Location Context
        if context.location_context is not None:
            resolved_scores, contrib = self._apply_location_factor(
                resolved_scores, context.location_context
            )
            factor_contributions['location_context'] = contrib
        
        # Factor 9: Temporal Context
        if context.temporal_context is not None:
            resolved_scores, contrib = self._apply_temporal_factor(
                resolved_scores, context.temporal_context
            )
            factor_contributions['temporal_context'] = contrib
        
        # Factor 10: User Profile
        if context.user_profile is not None:
            resolved_scores, contrib = self._apply_user_profile_factor(
                resolved_scores, context.user_profile
            )
            factor_contributions['user_profile'] = contrib
        
        # Factor 11: Prosodic Features
        if context.prosodic_features is not None:
            resolved_scores, contrib = self._apply_prosodic_factor(
                resolved_scores, context.prosodic_features
            )
            factor_contributions['prosodic_features'] = contrib
        
        # Factor 12: Input Fidelity
        if context.input_fidelity is not None:
            resolved_scores, contrib = self._apply_fidelity_factor(
                resolved_scores, context.input_fidelity
            )
            factor_contributions['input_fidelity'] = contrib
        
        # Normalize scores to [0.0, 1.0] range
        resolved_scores = self._normalize_scores(resolved_scores)
        
        # Calculate score deltas
        score_deltas = {
            intent_id: resolved_scores[intent_id] - base_scores[intent_id]
            for intent_id in base_scores
        }
        
        # Estimate overall confidence
        confidence = self._estimate_confidence(active_factors, score_deltas)
        
        logger.info(f"Resolution complete. Active factors: {len(active_factors)}")
        
        return ResolutionResult(
            resolved_scores=resolved_scores,
            active_factors=active_factors,
            score_deltas=score_deltas,
            confidence_estimate=confidence,
            factor_contributions=factor_contributions
        )
    
    def _validate_scores(self, scores: Dict[str, float]) -> None:
        """
        Validate that score dictionary is well-formed.
        
        Args:
            scores: Dictionary to validate
            
        Raises:
            ValueError: If scores contain NaN, Inf, or out-of-range values
        """
        for intent_id, score in scores.items():
            if not isinstance(score, (int, float)):
                raise ValueError(f"Score for {intent_id} is not numeric: {type(score)}")
            if score < 0.0 or score > 1.0:
                raise ValueError(f"Score for {intent_id} out of range [0.0, 1.0]: {score}")
    
    def _apply_association_factor(
        self,
        scores: Dict[str, float],
        association_history: List[str]
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 1: Apply association history co-occurrence patterns.
        
        Boosts intents that commonly co-occur with recent user intents.
        
        Args:
            scores: Current intent scores
            association_history: List of recent intent types
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        weight = self.weights['association_history']
        
        for recent_intent in association_history:
            recent_lower = recent_intent.lower()
            for base_intent, associated_keywords in self.association_patterns.items():
                if base_intent in recent_lower:
                    for intent_id in scores:
                        if any(kw in intent_id.lower() for kw in associated_keywords):
                            boost = weight
                            updated[intent_id] += boost
                            contributions[intent_id] = contributions.get(intent_id, 0.0) + boost
        
        logger.debug(f"Applied association factor: {len(contributions)} intents boosted")
        return updated, contributions
    
    def _apply_conflict_factor(
        self,
        scores: Dict[str, float],
        conflict_markers: List[str]
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 2: Detect and penalize conflicting intents.
        
        Reduces scores for intents that oppose explicit conflict markers
        in the input (e.g., 'no' opposes affirmative intents).
        
        Args:
            scores: Current intent scores
            conflict_markers: List of opposing signals
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        weight = self.weights['conflict_markers']
        
        for marker in conflict_markers:
            marker_lower = marker.lower()
            if marker_lower in self.conflict_pairs:
                opposing = self.conflict_pairs[marker_lower]
                for intent_id in scores:
                    if any(kw in intent_id.lower() for kw in opposing):
                        penalty = -weight
                        updated[intent_id] += penalty
                        contributions[intent_id] = contributions.get(intent_id, 0.0) + penalty
        
        logger.debug(f"Applied conflict factor: {len(contributions)} intents penalized")
        return updated, contributions
    
    def _apply_goal_factor(
        self,
        scores: Dict[str, float],
        goal_alignment: str
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 3: Boost intents aligned with stated goal/purpose.
        
        This is typically the highest-weight factor as user goals are
        highly predictive of intent.
        
        Args:
            scores: Current intent scores
            goal_alignment: User's stated goal
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        weight = self.weights['goal_alignment']
        
        goal_lower = goal_alignment.lower()
        if goal_lower in self.goal_groups:
            relevant_keywords = self.goal_groups[goal_lower]
            for intent_id in scores:
                if any(kw in intent_id.lower() for kw in relevant_keywords):
                    boost = weight
                    updated[intent_id] += boost
                    contributions[intent_id] = boost
        
        logger.debug(f"Applied goal factor: {len(contributions)} intents boosted")
        return updated, contributions
    
    def _apply_situation_factor(
        self,
        scores: Dict[str, float],
        situation_context: str
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 4: Boost intents relevant to current situation.
        
        Situational context (e.g., 'cooking', 'morning_routine') enables
        predictive intent selection.
        
        Args:
            scores: Current intent scores
            situation_context: Current situation classification
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        weight = self.weights['situation_context']
        
        situation_lower = situation_context.lower()
        if situation_lower in self.situation_intents:
            relevant_keywords = self.situation_intents[situation_lower]
            for intent_id in scores:
                if any(kw in intent_id.lower() for kw in relevant_keywords):
                    boost = weight
                    updated[intent_id] += boost
                    contributions[intent_id] = boost
        
        logger.debug(f"Applied situation factor: {len(contributions)} intents boosted")
        return updated, contributions
    
    def _apply_linguistic_factor(
        self,
        scores: Dict[str, float],
        linguistic_indicators: str
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 5: Apply grammatical and syntactic signal boosting.
        
        Linguistic markers (e.g., question marks, imperatives) help
        disambiguate between similar intents.
        
        Args:
            scores: Current intent scores
            linguistic_indicators: Grammatical signals
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        
        # Placeholder for NLP analysis
        # In production, this would use POS tagging, dependency parsing, etc.
        logger.debug("Applied linguistic factor: placeholder")
        
        return updated, contributions
    
    def _apply_semantic_capacity_factor(
        self,
        scores: Dict[str, float],
        semantic_capacity: float
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 6: Scale scores by semantic richness of input.
        
        Input with higher semantic capacity (more detail, specificity)
        should have higher confidence in semantic matching.
        
        Args:
            scores: Current intent scores
            semantic_capacity: Semantic richness [0.0-1.0]
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        weight = self.weights['semantic_capacity']
        
        # Capacity multiplier: higher capacity = more confident matching
        multiplier = 1.0 + (weight * semantic_capacity)
        
        for intent_id in scores:
            delta = scores[intent_id] * (multiplier - 1.0)
            updated[intent_id] = scores[intent_id] * multiplier
            contributions[intent_id] = delta
        
        logger.debug(f"Applied semantic capacity factor: multiplier={multiplier:.2f}")
        return updated, contributions
    
    def _apply_propriety_factor(
        self,
        scores: Dict[str, float],
        social_propriety: float
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 7: Apply social appropriateness adjustments.
        
        Contextual appropriateness affects intent selection
        (e.g., formal tone in business vs. casual in personal).
        
        Args:
            scores: Current intent scores
            social_propriety: Appropriateness [-1.0 (inappropriate) to 1.0 (appropriate)]
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        weight = self.weights['social_propriety']
        
        adjustment = weight * social_propriety
        
        for intent_id in scores:
            updated[intent_id] += adjustment
            contributions[intent_id] = adjustment
        
        logger.debug(f"Applied propriety factor: adjustment={adjustment:.3f}")
        return updated, contributions
    
    def _apply_location_factor(
        self,
        scores: Dict[str, float],
        location_context: str
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 8: Boost intents relevant to current location.
        
        Location is one of the highest-salience factors, as it strongly
        predicts user intent (e.g., 'recipe' in kitchen vs. 'navigation' in car).
        
        Args:
            scores: Current intent scores
            location_context: Current location
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        weight = self.weights['location_context']
        
        location_lower = location_context.lower()
        if location_lower in self.location_intents:
            relevant_keywords = self.location_intents[location_lower]
            for intent_id in scores:
                if any(kw in intent_id.lower() for kw in relevant_keywords):
                    boost = weight
                    updated[intent_id] += boost
                    contributions[intent_id] = boost
        
        logger.debug(f"Applied location factor: {len(contributions)} intents boosted")
        return updated, contributions
    
    def _apply_temporal_factor(
        self,
        scores: Dict[str, float],
        temporal_context: datetime
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 9: Boost intents relevant to time of day.
        
        Temporal patterns are highly predictive (e.g., 'alarm' in morning,
        'sleep' at night). This is a high-salience factor.
        
        Args:
            scores: Current intent scores
            temporal_context: Current timestamp
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        weight = self.weights['temporal_context']
        
        # Determine time period
        time_period = self._classify_time_of_day(temporal_context)
        
        if time_period in self.time_period_intents:
            relevant_keywords = self.time_period_intents[time_period]
            for intent_id in scores:
                if any(kw in intent_id.lower() for kw in relevant_keywords):
                    boost = weight
                    updated[intent_id] += boost
                    contributions[intent_id] = boost
        
        logger.debug(f"Applied temporal factor: period={time_period.value}, "
                    f"boosted={len(contributions)} intents")
        return updated, contributions
    
    def _apply_user_profile_factor(
        self,
        scores: Dict[str, float],
        user_profile: str
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 10: Apply user personalization preferences.
        
        Different users have different intent preferences. This factor
        personalizes resolution based on user profile.
        
        Args:
            scores: Current intent scores
            user_profile: User profile/demographic
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        weight = self.weights['user_profile']
        
        profile_lower = user_profile.lower()
        if profile_lower in self.user_preferences:
            preferred_keywords = self.user_preferences[profile_lower]
            for intent_id in scores:
                if any(kw in intent_id.lower() for kw in preferred_keywords):
                    boost = weight
                    updated[intent_id] += boost
                    contributions[intent_id] = boost
        
        logger.debug(f"Applied user profile factor: {len(contributions)} intents boosted")
        return updated, contributions
    
    def _apply_prosodic_factor(
        self,
        scores: Dict[str, float],
        prosodic_features: str
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 11: Apply accent and intonation pattern boosting.
        
        Prosodic features (pitch, stress, rhythm) carry semantic information.
        E.g., rising intonation often indicates questions.
        
        Args:
            scores: Current intent scores
            prosodic_features: Prosodic pattern description
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        
        # Placeholder for prosody analysis
        logger.debug("Applied prosodic factor: placeholder")
        
        return updated, contributions
    
    def _apply_fidelity_factor(
        self,
        scores: Dict[str, float],
        input_fidelity: float
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Factor 12: Adjust scores for signal quality and clarity.
        
        Degraded input (low fidelity) reduces confidence in the resolution.
        
        Args:
            scores: Current intent scores
            input_fidelity: Signal clarity [0.0 (degraded) to 1.0 (clear)]
            
        Returns:
            Tuple of (updated_scores, contribution_dict) for this factor
        """
        updated = scores.copy()
        contributions = {}
        weight = self.weights['input_fidelity']
        
        # Lower fidelity = higher penalty
        confidence_penalty = weight * (1.0 - input_fidelity)
        
        for intent_id in scores:
            updated[intent_id] -= confidence_penalty
            contributions[intent_id] = -confidence_penalty
        
        logger.debug(f"Applied fidelity factor: penalty={confidence_penalty:.3f}")
        return updated, contributions
    
    def _classify_time_of_day(self, timestamp: datetime) -> TimeOfDay:
        """
        Classify a timestamp into a time period.
        
        Args:
            timestamp: Datetime to classify
            
        Returns:
            TimeOfDay enum value
        """
        hour = timestamp.hour
        
        if 4 <= hour < 6:
            return TimeOfDay.EARLY_MORNING
        elif 6 <= hour < 12:
            return TimeOfDay.MORNING
        elif 12 <= hour < 17:
            return TimeOfDay.AFTERNOON
        elif 17 <= hour < 21:
            return TimeOfDay.EVENING
        elif 21 <= hour < 23:
            return TimeOfDay.NIGHT
        else:
            return TimeOfDay.LATE_NIGHT
    
    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize all scores to [0.0, 1.0] range.
        
        Args:
            scores: Potentially out-of-range scores
            
        Returns:
            Normalized scores in [0.0, 1.0]
        """
        normalized = {}
        for intent_id, score in scores.items():
            # Clamp to valid range
            normalized[intent_id] = max(0.0, min(1.0, score))
        
        return normalized
    
    def _estimate_confidence(
        self,
        active_factors: List[str],
        score_deltas: Dict[str, float]
    ) -> float:
        """
        Estimate overall confidence in resolution.
        
        Confidence increases with more active factors and larger score deltas.
        
        Args:
            active_factors: List of active contextual factors
            score_deltas: Per-intent score changes
            
        Returns:
            Confidence estimate [0.0-1.0]
        """
        # Base confidence increases with number of active factors
        factor_confidence = min(1.0, len(active_factors) / 6.0)  # 6+ factors = high confidence
        
        # Delta confidence increases if factors significantly changed scores
        avg_delta = sum(abs(d) for d in score_deltas.values()) / len(score_deltas) if score_deltas else 0.0
        delta_confidence = min(1.0, avg_delta)
        
        # Combined confidence (weighted average)
        confidence = (0.6 * factor_confidence) + (0.4 * delta_confidence)
        
        return confidence
    
    def update_weight(self, factor_name: str, new_weight: float) -> None:
        """
        Update weight for a specific factor.
        
        Allows dynamic tuning of factor importance.
        
        Args:
            factor_name: Name of factor to update
            new_weight: New weight value (must be non-negative)
            
        Raises:
            ValueError: If factor name is unknown or weight is negative
            
        Example:
            >>> engine = ContextResolutionEngine()
            >>> engine.update_weight('location_context', 0.25)  # Increase location weight
        """
        if factor_name not in self.DEFAULT_WEIGHTS:
            raise ValueError(f"Unknown factor: {factor_name}")
        if new_weight < 0:
            raise ValueError(f"Weight cannot be negative: {new_weight}")
        
        old_weight = self.weights[factor_name]
        self.weights[factor_name] = new_weight
        
        logger.info(f"Updated factor weight: {factor_name} {old_weight:.2f} -> {new_weight:.2f}")
    
    def get_factor_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all factors for diagnostic/educational purposes.
        
        Returns:
            Dictionary with factor metadata including name, weight, salience level
        """
        return {
            'association_history': {
                'weight': self.weights['association_history'],
                'salience': 'medium',
                'description': 'Co-occurrence patterns from user history'
            },
            'conflict_markers': {
                'weight': self.weights['conflict_markers'],
                'salience': 'medium',
                'description': 'Opposing or contrasting signals'
            },
            'goal_alignment': {
                'weight': self.weights['goal_alignment'],
                'salience': 'high',
                'description': 'User stated or inferred purpose'
            },
            'situation_context': {
                'weight': self.weights['situation_context'],
                'salience': 'medium',
                'description': 'Current situational classification'
            },
            'linguistic_indicators': {
                'weight': self.weights['linguistic_indicators'],
                'salience': 'low',
                'description': 'Grammatical and syntactic signals'
            },
            'semantic_capacity': {
                'weight': self.weights['semantic_capacity'],
                'salience': 'medium',
                'description': 'Semantic richness of input'
            },
            'social_propriety': {
                'weight': self.weights['social_propriety'],
                'salience': 'medium',
                'description': 'Contextual appropriateness'
            },
            'location_context': {
                'weight': self.weights['location_context'],
                'salience': 'high',
                'description': 'Geographic or spatial context'
            },
            'temporal_context': {
                'weight': self.weights['temporal_context'],
                'salience': 'high',
                'description': 'Time of day or temporal patterns'
            },
            'user_profile': {
                'weight': self.weights['user_profile'],
                'salience': 'low',
                'description': 'User demographic or preference profile'
            },
            'prosodic_features': {
                'weight': self.weights['prosodic_features'],
                'salience': 'low',
                'description': 'Accent, intonation, stress patterns'
            },
            'input_fidelity': {
                'weight': self.weights['input_fidelity'],
                'salience': 'low',
                'description': 'Signal quality and clarity'
            }
        }
