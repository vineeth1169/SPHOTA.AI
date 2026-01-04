"""
Context Manager for Sphota Engine
Implements the 12-Factor Context Resolution Matrix for dynamic intent scoring.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class ContextManager:
    """
    Manages contextual scoring for intent resolution using 12 classical factors.
    
    The 12 Factors:
    1. Sahacarya (Association History)
    2. Virodhitā (Conflict Check)
    3. Artha (Active Goal)
    4. Prakaraṇa (Application State)
    5. Liṅga (Syntax Cues)
    6. Śabda-sāmarthya (Word Capacity)
    7. Aucitī (Propriety)
    8. Deśa (Location)
    9. Kāla (Time)
    10. Vyakti (User Profile)
    11. Svara (Intonation)
    12. Apabhraṃśa (Fidelity)
    """
    
    def __init__(self) -> None:
        """Initialize the Context Manager."""
        self.command_history: List[str] = []
        self.max_history_length: int = 10
    
    def calculate_confidence(
        self,
        intent: Dict[str, Any],
        context_data: Dict[str, Any],
        base_score: float = 0.5
    ) -> float:
        """
        Calculate confidence score for an intent using 12-factor context resolution.
        
        Args:
            intent: Dictionary containing intent information with keys like:
                - 'type': Intent type/category
                - 'keywords': List of keywords
                - 'required_location': Location requirement
                - 'valid_time_range': Valid time range tuple
                - 'vocabulary_level': Vocabulary complexity
                - 'urgency': Urgency level
            context_data: Dictionary containing contextual information with keys like:
                - 'command_history': List of recent commands
                - 'system_state': Current system state
                - 'current_task_id': Active task identifier
                - 'current_screen': Currently active screen/menu
                - 'social_mode': Social context mode
                - 'gps_tag': Current location tag
                - 'current_hour': Current hour of day
                - 'user_demographic': User demographic info
                - 'audio_pitch': Audio pitch analysis
                - 'input_confidence': Input quality confidence
            base_score: Initial similarity score from SBERT (default: 0.5)
        
        Returns:
            Final confidence score after applying all 12 factors
        """
        final_score: float = base_score
        
        # Factor 6: Śabda-sāmarthya (Word Capacity) - Baseline
        # This is the base_score from SBERT, already applied
        word_capacity: float = base_score
        
        # Factor 1: Sahacarya (Association History)
        # Check last 3 commands for keyword matches
        association_history: float = 0.0
        command_history: List[str] = context_data.get('command_history', [])
        intent_keywords: List[str] = intent.get('keywords', [])
        
        if command_history and intent_keywords:
            recent_commands: List[str] = command_history[-3:]
            for command in recent_commands:
                command_lower: str = command.lower()
                for keyword in intent_keywords:
                    if keyword.lower() in command_lower:
                        association_history = 0.2
                        final_score += association_history
                        break
                if association_history > 0:
                    break
        
        # Factor 2: Virodhitā (Conflict Check)
        # Detect contradictions with system state
        conflict_check: float = 1.0
        intent_type: str = intent.get('type', '')
        system_state: str = context_data.get('system_state', '')
        
        if intent_type and system_state:
            # Check for contradictions
            if (intent_type.lower() in ['turn_on', 'enable', 'start'] and 
                system_state.upper() in ['ON', 'ENABLED', 'RUNNING']):
                conflict_check = 0.1  # Severe penalty
                final_score *= conflict_check
            elif (intent_type.lower() in ['turn_off', 'disable', 'stop'] and 
                  system_state.upper() in ['OFF', 'DISABLED', 'STOPPED']):
                conflict_check = 0.1  # Severe penalty
                final_score *= conflict_check
        
        # Factor 3: Artha (Active Goal)
        # Boost if intent aligns with current task
        active_goal: float = 0.0
        current_task_id: Optional[str] = context_data.get('current_task_id')
        intent_task_id: Optional[str] = intent.get('task_id')
        
        if current_task_id and intent_task_id:
            if current_task_id == intent_task_id:
                active_goal = 0.15
                final_score += active_goal
            else:
                # Check for related tasks
                if str(current_task_id) in str(intent_task_id) or str(intent_task_id) in str(current_task_id):
                    active_goal = 0.08
                    final_score += active_goal
        
        # Factor 4: Prakaraṇa (Application State)
        # Boost if intent is valid for current screen/menu
        app_state: float = 0.0
        current_screen: Optional[str] = context_data.get('current_screen')
        valid_screens: List[str] = intent.get('valid_screens', [])
        
        if current_screen and valid_screens:
            if current_screen in valid_screens:
                app_state = 0.12
                final_score += app_state
            else:
                # Slight penalty for wrong screen
                app_state = -0.05
                final_score += app_state
        
        # Factor 5: Liṅga (Syntax Cues)
        # Boost based on grammatical markers
        syntax_cues: float = 0.0
        user_input: str = context_data.get('user_input', '')
        
        if user_input:
            # Question detection
            if '?' in user_input and intent_type.lower() in ['question', 'query', 'ask']:
                syntax_cues = 0.1
                final_score += syntax_cues
            # Imperative detection
            elif user_input.strip().endswith('!') and intent_type.lower() in ['command', 'action']:
                syntax_cues = 0.08
                final_score += syntax_cues
            # Polite form detection
            elif any(word in user_input.lower() for word in ['please', 'could', 'would', 'kindly']):
                if intent.get('politeness', '') == 'formal':
                    syntax_cues = 0.06
                    final_score += syntax_cues
        
        # Factor 7: Aucitī (Propriety)
        # Adjust based on social context
        propriety: float = 1.0
        social_mode: str = context_data.get('social_mode', '')
        intent_register: str = intent.get('register', '')
        
        if social_mode == 'Business' and intent_register == 'Slang':
            propriety = 0.5  # 50% penalty
            final_score *= propriety
        elif social_mode == 'Casual' and intent_register == 'Formal':
            propriety = 0.8  # Slight penalty
            final_score *= propriety
        elif social_mode == social_mode and intent_register in ['Neutral', social_mode]:
            propriety = 1.1  # Slight boost
            final_score *= propriety
        
        # Factor 8: Deśa (Location)
        # Boost if location matches
        location: float = 0.0
        gps_tag: Optional[str] = context_data.get('gps_tag')
        required_location: Optional[str] = intent.get('required_location')
        
        if required_location:
            if gps_tag and gps_tag.lower() == required_location.lower():
                location = 0.2
                final_score += location
            elif not gps_tag:
                # No location data, apply neutral penalty
                location = -0.05
                final_score += location
            else:
                # Wrong location
                location = -0.15
                final_score += location
        
        # Factor 9: Kāla (Time)
        # Boost if time matches valid range
        time: float = 0.0
        current_hour: Optional[int] = context_data.get('current_hour')
        valid_time_range: Optional[tuple] = intent.get('valid_time_range')
        
        if current_hour is None:
            current_hour = datetime.now().hour
        
        if valid_time_range:
            start_hour, end_hour = valid_time_range
            if start_hour <= current_hour <= end_hour:
                time = 0.15
                final_score += time
            else:
                # Time mismatch penalty
                time = -0.1
                final_score += time
        
        # Factor 10: Vyakti (User Profile)
        # Boost if vocabulary matches user demographic
        user_profile: float = 0.0
        user_demographic: str = context_data.get('user_demographic', '')
        vocabulary_level: str = intent.get('vocabulary_level', '')
        
        if user_demographic and vocabulary_level:
            # Gen Z preferences
            if user_demographic == 'Gen Z' and vocabulary_level in ['Casual', 'Slang', 'Tech']:
                user_profile = 0.12
                final_score += user_profile
            # Millennial preferences
            elif user_demographic == 'Millennial' and vocabulary_level in ['Neutral', 'Tech', 'Professional']:
                user_profile = 0.12
                final_score += user_profile
            # Boomer preferences
            elif user_demographic in ['Boomer', 'Gen X'] and vocabulary_level in ['Formal', 'Traditional']:
                user_profile = 0.12
                final_score += user_profile
            else:
                # Mismatch
                user_profile = -0.05
                final_score += user_profile
        
        # Factor 11: Svara (Intonation)
        # Boost based on audio pitch analysis
        intonation: float = 0.0
        audio_pitch: str = context_data.get('audio_pitch', '')
        intent_urgency: str = intent.get('urgency', '')
        
        if audio_pitch:
            if audio_pitch in ['High', 'Rising'] and intent_urgency in ['Urgent', 'High']:
                intonation = 0.15
                final_score += intonation
            elif audio_pitch in ['High', 'Rising'] and intent_type.lower() in ['question', 'query']:
                intonation = 0.12
                final_score += intonation
            elif audio_pitch == 'Low' and intent_type.lower() in ['statement', 'command']:
                intonation = 0.08
                final_score += intonation
            elif audio_pitch in ['High', 'Rising'] and intent_urgency == 'Low':
                # Pitch-urgency mismatch
                intonation = -0.05
                final_score += intonation
        
        # Factor 12: Apabhraṃśa (Fidelity)
        # Widen search threshold for low-confidence input
        fidelity: float = 1.0
        input_confidence: float = context_data.get('input_confidence', 1.0)
        
        if input_confidence < 0.7:
            # Low input quality - check if intent has slang/alternate forms
            if intent_register in ['Slang', 'Casual'] or intent.get('has_alternate_forms', False):
                fidelity = 1.15  # Boost slang/flexible intents
                final_score *= fidelity
            else:
                # Strict intents get penalty with low input quality
                fidelity = 0.85
                final_score *= fidelity
        elif input_confidence >= 0.9:
            # High quality input - boost formal/precise intents
            if intent_register in ['Formal', 'Technical']:
                fidelity = 1.1
                final_score *= fidelity
        
        # Ensure score stays within valid bounds [0, 1]
        final_score = max(0.0, min(1.0, final_score))
        
        return final_score
    
    def update_command_history(self, command: str) -> None:
        """
        Update the command history buffer.
        
        Args:
            command: New command to add to history
        """
        self.command_history.append(command)
        
        # Maintain max history length
        if len(self.command_history) > self.max_history_length:
            self.command_history.pop(0)
    
    def get_command_history(self) -> List[str]:
        """
        Get the current command history.
        
        Returns:
            List of recent commands
        """
        return self.command_history.copy()
    
    def clear_command_history(self) -> None:
        """Clear the command history buffer."""
        self.command_history.clear()
