"""
Context Resolution Matrix (CRM)

Implements the 12-Factor Weighted Scoring Engine based on Bhartṛhari's
linguistic determinants for resolving ambiguity and extracting pure intent.

This is the core of the Madhyamā layer - where context transforms raw input
into resolved meaning (Vākyasphoṭa).
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class ContextObject:
    """
    Container for the 12 contextual factors used in intent resolution.
    
    Each field corresponds to one of Bhartṛhari's linguistic determinants.
    """
    # Historical/Associative factors
    sahacarya: Optional[List[str]] = None  # Association/User history
    virodhita: Optional[List[str]] = None  # Opposition/Contrast markers
    
    # Semantic/Pragmatic factors
    artha: Optional[str] = None  # Purpose/Goal of utterance
    prakarana: Optional[str] = None  # Overall context/situation
    linga: Optional[str] = None  # Grammatical/semantic signs
    shabda_samarthya: Optional[float] = None  # Word capacity/strength
    auciti: Optional[float] = None  # Propriety/fitness score
    
    # Spatiotemporal factors
    desa: Optional[str] = None  # Place/Location (e.g., GPS, room)
    kala: Optional[datetime] = None  # Time/Timestamp
    
    # Individual factors
    vyakti: Optional[str] = None  # User profile/individualization
    svara: Optional[str] = None  # Accent/intonation pattern
    apabhramsa: Optional[float] = None  # Distortion/slang score


class ContextResolutionMatrix:
    """
    The 12-Factor Weighted Scoring Engine.
    
    Resolves ambiguity by applying weighted contextual factors to intent scores.
    This implements Bhartṛhari's Akhaṇḍapakṣa principle where meaning emerges
    from the totality of context, not sequential word processing.
    """
    
    def __init__(self) -> None:
        """
        Initialize the CRM with default weights for the 12 factors.
        
        Weights are based on linguistic salience and empirical tuning.
        Sum need not equal 1.0 as factors can reinforce each other.
        """
        # The 12 Sanskrit Factors with their weights
        self.weights: Dict[str, float] = {
            # === Historical/Associative Factors ===
            "sahacarya": 0.15,        # Association/Co-occurrence history
            "virodhita": 0.10,        # Opposition/Contrast detection
            
            # === Semantic/Pragmatic Factors ===
            "artha": 0.20,            # Purpose/Goal (highest weight)
            "prakarana": 0.15,        # Context/Situation
            "linga": 0.08,            # Sign/Grammar
            "shabda_samarthya": 0.12, # Word capacity/strength
            "auciti": 0.10,           # Propriety/fitness
            
            # === Spatiotemporal Factors ===
            "desa": 0.18,             # Place/Location (high salience)
            "kala": 0.15,             # Time/temporal context
            
            # === Individual Factors ===
            "vyakti": 0.12,           # User profile/personalization
            "svara": 0.08,            # Accent/intonation
            "apabhramsa": 0.07        # Distortion handling
        }
        
        # Intent keyword mappings for each factor
        self._initialize_factor_mappings()
    
    def _initialize_factor_mappings(self) -> None:
        """
        Initialize mappings between contextual factors and intent keywords.
        These define which intents are boosted by which contextual signals.
        """
        # Sahacarya (Association): Co-occurring intent patterns
        self.sahacarya_map: Dict[str, List[str]] = {
            "cooking": ["timer", "recipe", "ingredients", "temperature"],
            "music": ["volume", "playlist", "song", "play"],
            "navigation": ["traffic", "route", "directions", "arrive"],
            "work": ["meeting", "schedule", "email", "calendar"],
            "exercise": ["timer", "workout", "fitness", "heart_rate"]
        }
        
        # Virodhitā (Opposition): Conflicting/contrasting intents
        self.virodhita_map: Dict[str, List[str]] = {
            "cancel": ["create", "start", "begin"],
            "stop": ["play", "start", "continue"],
            "close": ["open", "launch", "start"],
            "decrease": ["increase", "raise", "boost"],
            "no": ["yes", "confirm", "accept"]
        }
        
        # Artha (Purpose): Goal-oriented intent groups
        self.artha_map: Dict[str, List[str]] = {
            "productivity": ["work", "schedule", "reminder", "meeting", "email"],
            "entertainment": ["music", "video", "game", "play"],
            "information": ["search", "query", "weather", "news"],
            "communication": ["call", "message", "text", "email"],
            "automation": ["timer", "alarm", "reminder", "schedule"]
        }
        
        # Prakaraṇa (Context/Situation): Situational intent relevance
        self.prakarana_map: Dict[str, List[str]] = {
            "morning_routine": ["alarm", "weather", "news", "coffee", "breakfast"],
            "cooking": ["recipe", "timer", "ingredients", "temperature"],
            "travel": ["navigation", "traffic", "weather", "booking"],
            "work_session": ["focus", "timer", "schedule", "productivity"],
            "evening_relaxation": ["music", "entertainment", "dim_lights"]
        }
        
        # Deśa (Place): Location-based intent relevance
        self.desa_map: Dict[str, List[str]] = {
            "kitchen": ["cooking", "recipe", "timer", "food", "meal"],
            "bedroom": ["sleep", "alarm", "wake", "rest", "lights"],
            "office": ["work", "meeting", "productivity", "focus"],
            "car": ["navigation", "traffic", "music", "call", "hands_free"],
            "gym": ["workout", "exercise", "timer", "fitness", "music"],
            "home": ["lights", "temperature", "security", "entertainment"]
        }
        
        # Kāla (Time): Time-based intent relevance
        self.kala_map: Dict[str, List[str]] = {
            "early_morning": ["alarm", "wake", "weather", "news"],
            "morning": ["breakfast", "coffee", "schedule", "commute"],
            "afternoon": ["lunch", "work", "meeting", "productivity"],
            "evening": ["dinner", "relaxation", "entertainment", "music"],
            "night": ["sleep", "alarm", "bedtime", "lights_off", "quiet"],
            "late_night": ["sleep", "rest", "quiet", "dim"]
        }
        
        # Vyakti (User Profile): Personalized preferences
        self.vyakti_preferences: Dict[str, List[str]] = {
            "frequent_intents": [],  # Populated dynamically
            "preferred_style": []     # User's communication style
        }
    
    def resolve_intent(
        self,
        base_scores: Dict[str, float],
        context: ContextObject
    ) -> Dict[str, float]:
        """
        Apply the 12-factor resolution to base intent scores.
        
        This is the core CRM operation that transforms ambiguous input into
        resolved meaning by applying contextual boosts and penalties.
        
        Args:
            base_scores: Dictionary of intent_id -> similarity_score from SBERT
            context: ContextObject containing the 12 contextual factors
            
        Returns:
            Resolved scores after applying contextual weights
            
        Example:
            >>> base_scores = {"cooking_timer": 0.65, "alarm": 0.62}
            >>> context = ContextObject(desa="kitchen", kala=datetime.now())
            >>> crm.resolve_intent(base_scores, context)
            {"cooking_timer": 0.83, "alarm": 0.62}  # cooking boosted in kitchen
        """
        resolved_scores = base_scores.copy()
        
        # Factor 1: Sahacarya (Association/History)
        if context.sahacarya:
            resolved_scores = self._apply_sahacarya(resolved_scores, context.sahacarya)
        
        # Factor 2: Virodhitā (Opposition/Contrast)
        if context.virodhita:
            resolved_scores = self._apply_virodhita(resolved_scores, context.virodhita)
        
        # Factor 3: Artha (Purpose/Goal)
        if context.artha:
            resolved_scores = self._apply_artha(resolved_scores, context.artha)
        
        # Factor 4: Prakaraṇa (Context/Situation)
        if context.prakarana:
            resolved_scores = self._apply_prakarana(resolved_scores, context.prakarana)
        
        # Factor 5: Liṅga (Sign/Grammar) - placeholder for grammatical analysis
        if context.linga:
            resolved_scores = self._apply_linga(resolved_scores, context.linga)
        
        # Factor 6: Śabda-sāmarthya (Word Capacity)
        if context.shabda_samarthya is not None:
            resolved_scores = self._apply_shabda_samarthya(
                resolved_scores, context.shabda_samarthya
            )
        
        # Factor 7: Aucitī (Propriety/Fitness)
        if context.auciti is not None:
            resolved_scores = self._apply_auciti(resolved_scores, context.auciti)
        
        # Factor 8: Deśa (Place/Location)
        if context.desa:
            resolved_scores = self._apply_desa(resolved_scores, context.desa)
        
        # Factor 9: Kāla (Time)
        if context.kala:
            resolved_scores = self._apply_kala(resolved_scores, context.kala)
        
        # Factor 10: Vyakti (User Profile)
        if context.vyakti:
            resolved_scores = self._apply_vyakti(resolved_scores, context.vyakti)
        
        # Factor 11: Svara (Accent/Intonation) - placeholder for prosody
        if context.svara:
            resolved_scores = self._apply_svara(resolved_scores, context.svara)
        
        # Factor 12: Apabhraṃśa (Distortion/Slang)
        if context.apabhramsa is not None:
            resolved_scores = self._apply_apabhramsa(
                resolved_scores, context.apabhramsa
            )
        
        # Normalize scores to [0, 1] range
        for intent_id in resolved_scores:
            resolved_scores[intent_id] = max(0.0, min(1.0, resolved_scores[intent_id]))
        
        return resolved_scores
    
    # === Individual Factor Application Methods ===
    
    def _apply_sahacarya(
        self,
        scores: Dict[str, float],
        history: List[str]
    ) -> Dict[str, float]:
        """Factor 1: Boost intents associated with recent history."""
        boosted = scores.copy()
        weight = self.weights["sahacarya"]
        
        for recent_intent in history:
            recent_lower = recent_intent.lower()
            for base_intent, associated in self.sahacarya_map.items():
                if base_intent in recent_lower:
                    for intent_id in scores:
                        if any(keyword in intent_id.lower() for keyword in associated):
                            boosted[intent_id] += weight
        
        return boosted
    
    def _apply_virodhita(
        self,
        scores: Dict[str, float],
        contrast_markers: List[str]
    ) -> Dict[str, float]:
        """Factor 2: Penalize intents that oppose detected contrast markers."""
        adjusted = scores.copy()
        weight = self.weights["virodhita"]
        
        for marker in contrast_markers:
            marker_lower = marker.lower()
            if marker_lower in self.virodhita_map:
                opposing_keywords = self.virodhita_map[marker_lower]
                for intent_id in scores:
                    if any(keyword in intent_id.lower() for keyword in opposing_keywords):
                        adjusted[intent_id] -= weight
        
        return adjusted
    
    def _apply_artha(
        self,
        scores: Dict[str, float],
        purpose: str
    ) -> Dict[str, float]:
        """Factor 3: Boost intents aligned with stated purpose/goal."""
        boosted = scores.copy()
        weight = self.weights["artha"]
        
        purpose_lower = purpose.lower()
        if purpose_lower in self.artha_map:
            relevant_keywords = self.artha_map[purpose_lower]
            for intent_id in scores:
                if any(keyword in intent_id.lower() for keyword in relevant_keywords):
                    boosted[intent_id] += weight
        
        return boosted
    
    def _apply_prakarana(
        self,
        scores: Dict[str, float],
        situation: str
    ) -> Dict[str, float]:
        """Factor 4: Boost intents relevant to current situation/context."""
        boosted = scores.copy()
        weight = self.weights["prakarana"]
        
        situation_lower = situation.lower()
        if situation_lower in self.prakarana_map:
            relevant_keywords = self.prakarana_map[situation_lower]
            for intent_id in scores:
                if any(keyword in intent_id.lower() for keyword in relevant_keywords):
                    boosted[intent_id] += weight
        
        return boosted
    
    def _apply_linga(
        self,
        scores: Dict[str, float],
        grammatical_sign: str
    ) -> Dict[str, float]:
        """Factor 5: Apply grammatical/semantic sign boosting."""
        # Placeholder for grammatical analysis
        # In full implementation, would analyze verb tense, mood, aspect
        return scores.copy()
    
    def _apply_shabda_samarthya(
        self,
        scores: Dict[str, float],
        word_capacity: float
    ) -> Dict[str, float]:
        """Factor 6: Scale scores by word capacity/strength metric."""
        adjusted = scores.copy()
        weight = self.weights["shabda_samarthya"]
        
        # word_capacity is a measure of semantic richness [0, 1]
        # Higher capacity = more confidence in semantic matching
        capacity_multiplier = 1.0 + (weight * word_capacity)
        
        for intent_id in scores:
            adjusted[intent_id] *= capacity_multiplier
        
        return adjusted
    
    def _apply_auciti(
        self,
        scores: Dict[str, float],
        propriety_score: float
    ) -> Dict[str, float]:
        """Factor 7: Apply propriety/fitness adjustment."""
        adjusted = scores.copy()
        weight = self.weights["auciti"]
        
        # propriety_score measures contextual appropriateness [-1, 1]
        # Positive = boost, Negative = penalize
        adjustment = weight * propriety_score
        
        for intent_id in scores:
            adjusted[intent_id] += adjustment
        
        return adjusted
    
    def _apply_desa(
        self,
        scores: Dict[str, float],
        location: str
    ) -> Dict[str, float]:
        """Factor 8: Boost intents relevant to current location."""
        boosted = scores.copy()
        weight = self.weights["desa"]
        
        location_lower = location.lower()
        if location_lower in self.desa_map:
            relevant_keywords = self.desa_map[location_lower]
            for intent_id in scores:
                if any(keyword in intent_id.lower() for keyword in relevant_keywords):
                    boosted[intent_id] += weight
        
        return boosted
    
    def _apply_kala(
        self,
        scores: Dict[str, float],
        timestamp: datetime
    ) -> Dict[str, float]:
        """Factor 9: Boost intents relevant to current time."""
        boosted = scores.copy()
        weight = self.weights["kala"]
        
        # Determine time period
        hour = timestamp.hour
        if 4 <= hour < 6:
            time_period = "early_morning"
        elif 6 <= hour < 12:
            time_period = "morning"
        elif 12 <= hour < 17:
            time_period = "afternoon"
        elif 17 <= hour < 21:
            time_period = "evening"
        elif 21 <= hour < 23:
            time_period = "night"
        else:
            time_period = "late_night"
        
        if time_period in self.kala_map:
            relevant_keywords = self.kala_map[time_period]
            for intent_id in scores:
                if any(keyword in intent_id.lower() for keyword in relevant_keywords):
                    boosted[intent_id] += weight
        
        return boosted
    
    def _apply_vyakti(
        self,
        scores: Dict[str, float],
        user_profile: str
    ) -> Dict[str, float]:
        """Factor 10: Apply user personalization."""
        boosted = scores.copy()
        weight = self.weights["vyakti"]
        
        # In full implementation, would load user preference model
        # For now, simple keyword matching
        if user_profile in self.vyakti_preferences:
            preferred_intents = self.vyakti_preferences[user_profile]
            for intent_id in scores:
                if any(pref in intent_id.lower() for pref in preferred_intents):
                    boosted[intent_id] += weight
        
        return boosted
    
    def _apply_svara(
        self,
        scores: Dict[str, float],
        intonation: str
    ) -> Dict[str, float]:
        """Factor 11: Apply accent/intonation pattern boosting."""
        # Placeholder for prosodic analysis
        # In full implementation, would analyze pitch, stress, rhythm
        # Example: rising intonation -> boost question intents
        return scores.copy()
    
    def _apply_apabhramsa(
        self,
        scores: Dict[str, float],
        distortion_score: float
    ) -> Dict[str, float]:
        """Factor 12: Adjust for slang/distortion level."""
        adjusted = scores.copy()
        weight = self.weights["apabhramsa"]
        
        # distortion_score measures how much normalization was needed [0, 1]
        # Higher distortion = less confidence penalty
        confidence_penalty = weight * distortion_score
        
        for intent_id in scores:
            adjusted[intent_id] -= confidence_penalty
        
        return adjusted
    
    # === Utility Methods ===
    
    def set_weight(self, factor: str, weight: float) -> None:
        """
        Update weight for a specific factor.
        
        Args:
            factor: Sanskrit factor name (e.g., "sahacarya", "desa")
            weight: New weight value
        """
        if factor in self.weights:
            self.weights[factor] = weight
        else:
            raise ValueError(f"Unknown factor: {factor}")
    
    def get_active_factors(self, context: ContextObject) -> List[str]:
        """
        Get list of factors that are active (have values) in the context.
        
        Args:
            context: ContextObject to analyze
            
        Returns:
            List of active factor names
        """
        active = []
        if context.sahacarya:
            active.append("sahacarya")
        if context.virodhita:
            active.append("virodhita")
        if context.artha:
            active.append("artha")
        if context.prakarana:
            active.append("prakarana")
        if context.linga:
            active.append("linga")
        if context.shabda_samarthya is not None:
            active.append("shabda_samarthya")
        if context.auciti is not None:
            active.append("auciti")
        if context.desa:
            active.append("desa")
        if context.kala:
            active.append("kala")
        if context.vyakti:
            active.append("vyakti")
        if context.svara:
            active.append("svara")
        if context.apabhramsa is not None:
            active.append("apabhramsa")
        
        return active
    
    def explain_resolution(
        self,
        base_scores: Dict[str, float],
        resolved_scores: Dict[str, float],
        context: ContextObject
    ) -> Dict[str, Any]:
        """
        Generate explanation of how context affected scores.
        
        Args:
            base_scores: Original scores before resolution
            resolved_scores: Scores after context resolution
            context: ContextObject used for resolution
            
        Returns:
            Dictionary with explanation details
        """
        explanation = {
            "active_factors": self.get_active_factors(context),
            "score_changes": {},
            "top_boosts": [],
            "top_penalties": []
        }
        
        # Calculate changes
        for intent_id in base_scores:
            change = resolved_scores[intent_id] - base_scores[intent_id]
            explanation["score_changes"][intent_id] = {
                "base": base_scores[intent_id],
                "resolved": resolved_scores[intent_id],
                "change": change
            }
        
        # Find top changes
        changes = [(iid, data["change"]) for iid, data in explanation["score_changes"].items()]
        changes.sort(key=lambda x: x[1], reverse=True)
        
        explanation["top_boosts"] = [(iid, chg) for iid, chg in changes if chg > 0][:3]
        explanation["top_penalties"] = [(iid, abs(chg)) for iid, chg in changes if chg < 0][:3]
        
        return explanation
