"""
Context Weighter - 12-Factor Intent Scoring

Implements a comprehensive 12-factor weighting system for intent resolution.
Each factor independently adjusts the confidence score based on contextual information.

The 12 factors (in English):
1. Association (user history)
2. Opposition (conflict detection)
3. Purpose (active goal alignment)
4. Situation (current screen state)
5. Indicator (syntax cues)
6. Word Capacity (base semantic score)
7. Propriety (social mode appropriateness)
8. Place (location context)
9. Time (temporal context)
10. Individual (user profile matching)
11. Intonation (audio feature analysis)
12. Distortion (input fidelity normalization)
"""

from typing import Dict, Any, List, Optional


class ContextWeighter:
    """
    Applies comprehensive 12-factor weighting to intent confidence scores.
    
    Each factor can boost, penalize, or block an intent based on contextual information.
    Final score is always bounded to [0.0, 1.0].
    """
    
    def __init__(self) -> None:
        """Initialize the context weighter with default factor weights."""
        self.factor_weights: Dict[str, float] = {
            'association': 0.15,        # Factor 1: User history
            'opposition': 0.10,         # Factor 2: Conflict detection
            'purpose': 0.20,            # Factor 3: Goal alignment
            'situation': 0.15,          # Factor 4: Screen state
            'indicator': 0.08,          # Factor 5: Syntax cues
            'word_capacity': 0.12,      # Factor 6: Base semantic score
            'propriety': 0.10,          # Factor 7: Social mode
            'place': 0.18,              # Factor 8: Location
            'time': 0.15,               # Factor 9: Time/Temporal
            'individual': 0.12,         # Factor 10: User profile
            'intonation': 0.08,         # Factor 11: Audio features
            'distortion': 0.07          # Factor 12: Input fidelity
        }
    
    def apply_weights(
        self, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Apply 12-factor weighting to the intent confidence score.
        
        Sequentially applies all 12 factors, each modifying the score based on
        contextual information. Final score is bounded to [0.0, 1.0].
        
        Args:
            intent: Dictionary containing intent metadata with keys like:
                - 'action': Intent action type (e.g., 'turn_on', 'turn_off')
                - 'type': Intent type (e.g., 'query', 'command', 'action')
                - 'tags': List of associated tags for history matching
                - 'goal_alignment': Goal category the intent supports
                - 'valid_screens': List of screens where intent is actionable
                - 'formality': Formality level ('formal', 'casual', 'neutral')
                - 'contains_slang': Boolean indicating vulgar/slang content
                - 'required_location': Specific location requirement
                - 'time_specific': Required time of day
                - 'vocabulary_level': Vocabulary complexity level
                
            context: Dictionary containing contextual information with keys like:
                - 'base_score': Raw semantic similarity (0.0-1.0)
                - 'user_history': List of recent commands/tags
                - 'system_state': Current system state ('ON', 'OFF', etc)
                - 'active_goal': Currently active user goal
                - 'current_screen': Current UI screen/location
                - 'syntax_flags': List of detected syntax patterns
                - 'social_mode': Communication mode ('business', 'casual')
                - 'location': Current user location
                - 'time_of_day': Current time period
                - 'user_profile': User demographic profile
                - 'audio_features': Dict with audio analysis (pitch, tone, etc)
                - 'input_fidelity': Input quality score (0.0-1.0)
        
        Returns:
            float: Final confidence score bounded to [0.0, 1.0]
        """
        base_score: float = context.get('base_score', 0.5)
        final_score: float = base_score
        
        # ===== APPLY ALL 12 FACTORS =====
        
        # Factor 1: Association (User History)
        final_score = self._apply_association(final_score, intent, context)
        
        # Factor 2: Opposition (Conflict Detection)
        final_score = self._apply_opposition(final_score, intent, context)
        
        # Factor 3: Purpose (Goal Alignment)
        final_score = self._apply_purpose(final_score, intent, context)
        
        # Factor 4: Situation (Screen State)
        final_score = self._apply_situation(final_score, intent, context)
        
        # Factor 5: Indicator (Syntax Cues)
        final_score = self._apply_indicator(final_score, intent, context)
        
        # Factor 6: Word Capacity (Base Score)
        # Already incorporated in base_score
        
        # Factor 7: Propriety (Social Mode)
        final_score = self._apply_propriety(final_score, intent, context)
        
        # Factor 8: Place (Location Context)
        final_score = self._apply_place(final_score, intent, context)
        
        # Factor 9: Time (Temporal Context)
        final_score = self._apply_time(final_score, intent, context)
        
        # Factor 10: Individual (User Profile)
        final_score = self._apply_individual(final_score, intent, context)
        
        # Factor 11: Intonation (Audio Features)
        final_score = self._apply_intonation(final_score, intent, context)
        
        # Factor 12: Distortion (Input Fidelity)
        final_score = self._apply_distortion(final_score, intent, context)
        
        # ===== FINALIZE SCORE =====
        # Ensure score is within valid bounds [0.0, 1.0]
        final_score = max(0.0, min(1.0, final_score))
        
        return final_score
    
    def _apply_association(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 1: Association (User History)
        
        Logic: Check user_history (last 3 commands). If the intent tag matches
        a tag in history, boost score by +0.15.
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        user_history: List[str] = context.get('user_history', [])
        intent_tags: List[str] = intent.get('tags', [])
        
        if user_history and intent_tags:
            recent_history: List[str] = user_history[-3:]
            
            for tag in intent_tags:
                tag_lower: str = tag.lower()
                for history_item in recent_history:
                    if tag_lower in history_item.lower():
                        score += 0.15
                        return score
        
        return score
    
    def _apply_opposition(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 2: Opposition (Conflict Detection)
        
        Logic: Check system_state. If the intent contradicts the state
        (e.g., "Turn On" when state="ON"), multiply score by 0.1 (severe penalty).
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        system_state: str = context.get('system_state', '')
        intent_action: str = intent.get('action', '')
        
        if not intent_action or not system_state:
            return score
        
        intent_action_lower: str = intent_action.lower()
        system_state_upper: str = system_state.upper()
        
        # Check for contradictions
        if intent_action_lower in ['turn_on', 'enable', 'start', 'activate']:
            if system_state_upper in ['ON', 'ENABLED', 'RUNNING', 'ACTIVE']:
                score *= 0.1  # Severe penalty
                return score
        
        if intent_action_lower in ['turn_off', 'disable', 'stop', 'deactivate']:
            if system_state_upper in ['OFF', 'DISABLED', 'STOPPED', 'INACTIVE']:
                score *= 0.1  # Severe penalty
                return score
        
        return score
    
    def _apply_purpose(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 3: Purpose (Goal Alignment)
        
        Logic: Check active_goal. If intent aligns with the current goal
        (e.g., goal="booking_flight"), boost by +0.20.
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        active_goal: str = context.get('active_goal', '')
        intent_goal_alignment: str = intent.get('goal_alignment', '')
        
        if not active_goal or not intent_goal_alignment:
            return score
        
        active_goal_lower: str = active_goal.lower()
        intent_goal_lower: str = intent_goal_alignment.lower()
        
        # Exact match
        if active_goal_lower == intent_goal_lower:
            score += 0.20
        # Partial match
        elif intent_goal_lower in active_goal_lower or active_goal_lower in intent_goal_lower:
            score += 0.10
        
        return score
    
    def _apply_situation(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 4: Situation (Screen State)
        
        Logic: Check current_screen. If the intent is actionable on the
        current screen, boost by +0.15.
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        current_screen: str = context.get('current_screen', '')
        valid_screens: List[str] = intent.get('valid_screens', [])
        
        if current_screen and valid_screens:
            if current_screen in valid_screens:
                score += 0.15
            else:
                score -= 0.05  # Slight penalty if intent not valid on screen
        
        return score
    
    def _apply_indicator(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 5: Indicator (Syntax Cues)
        
        Logic: Check syntax_flags. If input has "Question" syntax and
        intent is "Query", boost by +0.08.
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        syntax_flags: List[str] = context.get('syntax_flags', [])
        intent_type: str = intent.get('type', '')
        
        if not syntax_flags or not intent_type:
            return score
        
        syntax_flags_lower: List[str] = [s.lower() for s in syntax_flags]
        intent_type_lower: str = intent_type.lower()
        
        # Question syntax matches query intent
        if 'question' in syntax_flags_lower and intent_type_lower in ['query', 'ask', 'question']:
            score += 0.08
        
        # Exclamation syntax matches command intent
        elif 'exclamation' in syntax_flags_lower and intent_type_lower in ['command', 'action', 'imperative']:
            score += 0.08
        
        # Statement syntax matches informational intent
        elif 'statement' in syntax_flags_lower and intent_type_lower in ['statement', 'information']:
            score += 0.08
        
        return score
    
    def _apply_propriety(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 7: Propriety (Social Mode)
        
        Logic: Check social_mode. If "Business" and intent contains
        "Slang/Vulgar", multiply score by 0.0 (block it).
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        social_mode: str = context.get('social_mode', '')
        intent_formality: str = intent.get('formality', 'neutral')
        contains_slang: bool = intent.get('contains_slang', False)
        
        if not social_mode:
            return score
        
        social_mode_lower: str = social_mode.lower()
        
        # Block vulgar/slang content in business mode
        if social_mode_lower == 'business' and contains_slang:
            score *= 0.0
        
        # Penalize formal intent in casual mode
        elif social_mode_lower == 'casual' and intent_formality == 'formal':
            score *= 0.8
        
        # Boost matching formality levels
        elif social_mode_lower == intent_formality.lower() or intent_formality == 'neutral':
            score *= 1.1
        
        return score
    
    def _apply_place(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 8: Place (Location Context)
        
        Logic: Check location. If intent requires a specific location
        (e.g., "Kitchen") and we are there, boost by +0.18.
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        current_location: str = context.get('location', '')
        required_location: str = intent.get('required_location', '')
        
        if not required_location:
            return score
        
        required_location_lower: str = required_location.lower()
        
        # Location matches
        if current_location:
            if current_location.lower() == required_location_lower:
                score += 0.18
            else:
                score -= 0.15  # Wrong location penalty
        else:
            # No location data available
            score -= 0.05
        
        return score
    
    def _apply_time(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 9: Time (Temporal Context)
        
        Logic: Check time_of_day. If intent is time-specific
        (e.g., "Good Morning"), boost by +0.15 only if time matches.
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        time_of_day: str = context.get('time_of_day', '')
        required_time: str = intent.get('time_specific', '')
        
        if not required_time:
            return score
        
        required_time_lower: str = required_time.lower()
        
        # Time matches
        if time_of_day:
            if time_of_day.lower() == required_time_lower:
                score += 0.15
            elif required_time_lower not in time_of_day.lower():
                score -= 0.05  # Wrong time penalty
        else:
            # No time data available
            score -= 0.05
        
        return score
    
    def _apply_individual(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 10: Individual (User Profile)
        
        Logic: Check user_profile. If intent vocabulary matches user
        demographic (e.g., "Gen Z"), boost by +0.12.
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        user_profile: str = context.get('user_profile', '')
        intent_vocab_level: str = intent.get('vocabulary_level', 'neutral')
        
        if not user_profile or not intent_vocab_level:
            return score
        
        user_profile_lower: str = user_profile.lower()
        intent_vocab_lower: str = intent_vocab_level.lower()
        
        # Exact match
        if user_profile_lower == intent_vocab_lower:
            score += 0.12
        
        # Partial match
        elif user_profile_lower in intent_vocab_lower or intent_vocab_lower in user_profile_lower:
            score += 0.06
        
        # Neutral vocabulary works for all profiles
        elif intent_vocab_lower == 'neutral':
            score += 0.06
        
        return score
    
    def _apply_intonation(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 11: Intonation (Audio Features)
        
        Logic: Check audio_features. If pitch is "Rising" (Question)
        vs "Flat" (Statement), boost corresponding intent types by +0.08.
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        audio_features: Dict[str, str] = context.get('audio_features', {})
        pitch: str = audio_features.get('pitch', '')
        intent_type: str = intent.get('type', '')
        
        if not pitch or not intent_type:
            return score
        
        pitch_lower: str = pitch.lower()
        intent_type_lower: str = intent_type.lower()
        
        # Rising pitch (question intonation) matches query intents
        if pitch_lower == 'rising' and intent_type_lower in ['question', 'query', 'ask']:
            score += 0.08
        
        # Flat pitch (statement intonation) matches command/statement intents
        elif pitch_lower == 'flat' and intent_type_lower in ['statement', 'command', 'action']:
            score += 0.08
        
        return score
    
    def _apply_distortion(
        self, 
        score: float, 
        intent: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Factor 12: Distortion (Input Fidelity)
        
        Logic: Check input_fidelity. If fidelity < 0.5 (noisy),
        trigger the normalization layer to map slang to pure intent before scoring.
        
        Args:
            score: Current confidence score
            intent: Intent metadata
            context: Context information
            
        Returns:
            Modified confidence score
        """
        input_fidelity: float = context.get('input_fidelity', 1.0)
        
        # If input quality is poor (< 0.5), apply normalization
        if input_fidelity < 0.5:
            try:
                # Import normalization layer for handling distorted input
                from core.apabhramsa_layer import ApabhramsaLayer
                
                normalizer: ApabhramsaLayer = ApabhramsaLayer()
                # Apply normalization to map slang/distorted forms to pure intent
                # Reduce score confidence based on input quality
                score *= (0.5 + input_fidelity)
                
            except ImportError:
                # Fallback if normalization layer not available
                score *= (0.5 + input_fidelity)
        
        return score
    
    def calculate_final_score(
        self,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate final confidence score using all 12 factors.
        
        Convenience method that calls apply_weights.
        
        Args:
            intent: Intent metadata dictionary
            context: Context information dictionary
            
        Returns:
            float: Final confidence score between 0.0 and 1.0
        """
        return self.apply_weights(intent, context)


# Example usage and documentation
if __name__ == "__main__":
    # Example: Create weighter and apply to an intent
    weighter = ContextWeighter()
    
    # Define a sample intent
    sample_intent = {
        'id': 'lights_on',
        'action': 'turn_on',
        'type': 'command',
        'tags': ['lights', 'home', 'automation'],
        'goal_alignment': 'home_control',
        'valid_screens': ['home', 'settings'],
        'formality': 'casual',
        'contains_slang': False,
        'required_location': 'home',
        'time_specific': 'evening',
        'vocabulary_level': 'neutral'
    }
    
    # Define sample context
    sample_context = {
        'base_score': 0.75,
        'user_history': ['lights', 'brightness', 'home'],
        'system_state': 'OFF',
        'active_goal': 'home_control',
        'current_screen': 'home',
        'syntax_flags': ['statement', 'imperative'],
        'social_mode': 'casual',
        'location': 'home',
        'time_of_day': 'evening',
        'user_profile': 'general_user',
        'audio_features': {'pitch': 'flat', 'tone': 'normal'},
        'input_fidelity': 0.95
    }
    
    # Calculate final score
    final_score = weighter.apply_weights(sample_intent, sample_context)
    print(f"Final confidence score: {final_score:.2f}")
