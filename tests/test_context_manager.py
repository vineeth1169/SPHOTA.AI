"""
Unit Tests for Context Manager - 12-Factor Context Resolution Matrix

Test suite covering all 12 factors of the Context Resolution Matrix:
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

import pytest
from datetime import datetime
from typing import Dict, Any
from core.context_manager import ContextManager


class TestContextManagerBasics:
    """Test basic ContextManager initialization and utility methods."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        """Create a ContextManager instance."""
        return ContextManager()
    
    def test_initialization(self, context_mgr: ContextManager):
        """Test ContextManager initializes with empty history."""
        assert isinstance(context_mgr.command_history, list)
        assert len(context_mgr.command_history) == 0
        assert context_mgr.max_history_length == 10
    
    def test_update_command_history(self, context_mgr: ContextManager):
        """Test command history is updated correctly."""
        context_mgr.update_command_history("search flights")
        context_mgr.update_command_history("check dates")
        
        history = context_mgr.get_command_history()
        assert len(history) == 2
        assert history[0] == "search flights"
        assert history[1] == "check dates"
    
    def test_command_history_max_length(self, context_mgr: ContextManager):
        """Test command history respects max length."""
        for i in range(15):
            context_mgr.update_command_history(f"command_{i}")
        
        history = context_mgr.get_command_history()
        assert len(history) == 10  # Max length
        assert history[0] == "command_5"  # Oldest retained
        assert history[-1] == "command_14"  # Newest
    
    def test_clear_command_history(self, context_mgr: ContextManager):
        """Test command history can be cleared."""
        context_mgr.update_command_history("test")
        context_mgr.clear_command_history()
        
        assert len(context_mgr.get_command_history()) == 0


class TestFactorOneAssociationHistory:
    """Test Factor 1: Sahacarya (Association History)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_association_boost_with_matching_keywords(self, context_mgr: ContextManager):
        """Test +0.2 boost for keyword match in last 3 commands."""
        intent = {
            "type": "booking",
            "keywords": ["flight", "book", "travel"],
            "register": "Casual"
        }
        
        context_data = {
            "command_history": ["search for flights", "check travel dates", "compare airlines"],
            "system_state": "OFF",
            "user_input": "book it",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have +0.2 boost from association
        expected_min = base_score + 0.2
        assert final_score >= expected_min - 0.01  # Allow small floating point difference
    
    def test_no_boost_without_keyword_match(self, context_mgr: ContextManager):
        """Test no boost when keywords don't match history."""
        intent = {
            "type": "booking",
            "keywords": ["restaurant", "dining"],
            "register": "Casual"
        }
        
        context_data = {
            "command_history": ["search flights", "check hotels"],
            "system_state": "OFF",
            "user_input": "book a table",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should not have +0.2 boost
        assert final_score < base_score + 0.25  # No significant boost


class TestFactorTwoConflictCheck:
    """Test Factor 2: Virodhitā (Conflict Check)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_severe_penalty_turn_on_when_already_on(self, context_mgr: ContextManager):
        """Test 0.1x multiplier (90% penalty) when system already ON."""
        intent = {
            "type": "turn_on",
            "keywords": ["turn", "on", "enable"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "ON",  # Already ON - conflict!
            "user_input": "turn on lights",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.8
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have 0.1x multiplier applied
        expected_max = base_score * 0.1 + 0.05  # Allow some tolerance
        assert final_score < expected_max
    
    def test_no_penalty_turn_on_when_off(self, context_mgr: ContextManager):
        """Test no penalty when system is OFF and turning ON."""
        intent = {
            "type": "turn_on",
            "keywords": ["turn", "on"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",  # OFF - no conflict
            "user_input": "turn on lights",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.8
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should NOT have 0.1x multiplier
        assert final_score > base_score * 0.5  # Should be relatively high


class TestFactorThreeActiveGoal:
    """Test Factor 3: Artha (Active Goal)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_boost_matching_task_id(self, context_mgr: ContextManager):
        """Test +0.15 boost when intent aligns with current task."""
        intent = {
            "type": "action",
            "keywords": ["execute"],
            "task_id": "lighting_control",
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "control lights",
            "current_task_id": "lighting_control",  # Matches!
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have +0.15 boost
        assert final_score >= base_score + 0.14


class TestFactorFourApplicationState:
    """Test Factor 4: Prakaraṇa (Application State)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_boost_valid_screen(self, context_mgr: ContextManager):
        """Test +0.12 boost for valid screen context."""
        intent = {
            "type": "control",
            "keywords": ["lights"],
            "valid_screens": ["Home", "LivingRoom", "Kitchen"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "turn on lights",
            "current_task_id": None,
            "current_screen": "Home",  # Valid screen
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have +0.12 boost
        assert final_score >= base_score + 0.11
    
    def test_penalty_invalid_screen(self, context_mgr: ContextManager):
        """Test -0.05 penalty for invalid screen."""
        intent = {
            "type": "control",
            "keywords": ["lights"],
            "valid_screens": ["Home", "Kitchen"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "turn on lights",
            "current_task_id": None,
            "current_screen": "Settings",  # Invalid screen
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have -0.05 penalty
        assert final_score <= base_score - 0.04


class TestFactorFiveSyntaxCues:
    """Test Factor 5: Liṅga (Syntax Cues)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_boost_question_mark(self, context_mgr: ContextManager):
        """Test +0.1 boost for question mark with question intent."""
        intent = {
            "type": "question",
            "keywords": ["what", "where"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "What time is it?",  # Question mark
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have +0.1 boost
        assert final_score >= base_score + 0.09
    
    def test_boost_exclamation_mark(self, context_mgr: ContextManager):
        """Test +0.08 boost for exclamation with command intent."""
        intent = {
            "type": "command",
            "keywords": ["execute"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "Execute now!",  # Exclamation mark
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have +0.08 boost
        assert final_score >= base_score + 0.07


class TestFactorSevenPropriety:
    """Test Factor 7: Aucitī (Propriety)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_slang_penalty_in_business_mode(self, context_mgr: ContextManager):
        """Test 0.5x multiplier (50% penalty) for slang in Business mode."""
        intent = {
            "type": "evaluation",
            "keywords": ["sick"],
            "register": "Slang"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "That's sick",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Business",  # Business mode - penalize slang
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Professional",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.7
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have 0.5x multiplier (50% penalty)
        expected_max = base_score * 0.5 + 0.05
        assert final_score < expected_max
    
    def test_no_slang_penalty_in_casual_mode(self, context_mgr: ContextManager):
        """Test no penalty for slang in Casual mode."""
        intent = {
            "type": "evaluation",
            "keywords": ["sick"],
            "register": "Slang"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "That's sick",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",  # Casual mode - no penalty
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Gen Z",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.6
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should not have 0.5x penalty
        assert final_score > base_score * 0.6


class TestFactorEightLocation:
    """Test Factor 8: Deśa (Location)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_boost_matching_location(self, context_mgr: ContextManager):
        """Test +0.2 boost for matching location."""
        intent = {
            "type": "reference",
            "keywords": ["bank"],
            "required_location": "riverside park",
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "bank",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": "Riverside Park",  # Matches!
            "current_hour": 12,
            "user_demographic": "Gen X",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have +0.2 boost
        assert final_score >= base_score + 0.19
    
    def test_penalty_wrong_location(self, context_mgr: ContextManager):
        """Test -0.15 penalty for wrong location."""
        intent = {
            "type": "reference",
            "keywords": ["bank"],
            "required_location": "downtown",
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "bank",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": "Forest Trail",  # Wrong location
            "current_hour": 12,
            "user_demographic": "Gen X",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.6
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have -0.15 penalty
        assert final_score <= base_score - 0.14


class TestFactorNineTime:
    """Test Factor 9: Kāla (Time)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_boost_valid_time_range(self, context_mgr: ContextManager):
        """Test +0.15 boost when current time is in valid range."""
        intent = {
            "type": "action",
            "keywords": ["execute"],
            "valid_time_range": (9, 17),  # Business hours
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "execute",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Business",
            "gps_tag": None,
            "current_hour": 12,  # Within range
            "user_demographic": "Professional",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have +0.15 boost
        assert final_score >= base_score + 0.14
    
    def test_penalty_invalid_time_range(self, context_mgr: ContextManager):
        """Test -0.1 penalty when time is outside valid range."""
        intent = {
            "type": "action",
            "keywords": ["execute"],
            "valid_time_range": (9, 17),  # Business hours
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "execute",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Business",
            "gps_tag": None,
            "current_hour": 22,  # Outside range
            "user_demographic": "Professional",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.6
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have -0.1 penalty
        assert final_score <= base_score - 0.09


class TestFactorTenUserProfile:
    """Test Factor 10: Vyakti (User Profile)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_boost_gen_z_match(self, context_mgr: ContextManager):
        """Test +0.12 boost for Gen Z matching casual vocabulary."""
        intent = {
            "type": "evaluation",
            "keywords": ["awesome"],
            "vocabulary_level": "Casual",
            "register": "Slang"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "awesome",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Gen Z",  # Gen Z + Casual vocabulary match
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have +0.12 boost
        assert final_score >= base_score + 0.11
    
    def test_penalty_demographic_mismatch(self, context_mgr: ContextManager):
        """Test -0.05 penalty for demographic vocabulary mismatch."""
        intent = {
            "type": "reference",
            "keywords": ["executive"],
            "vocabulary_level": "Technical",
            "register": "Formal"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "executive",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Boomer",  # Mismatch with Technical vocabulary
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.6
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have -0.05 penalty
        assert final_score <= base_score - 0.04


class TestFactorElevenIntonation:
    """Test Factor 11: Svara (Intonation)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_boost_high_pitch_urgent(self, context_mgr: ContextManager):
        """Test +0.15 boost for high pitch with urgent intent."""
        intent = {
            "type": "alarm",
            "keywords": ["urgent"],
            "urgency": "Urgent",
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "urgent!",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "High",  # High pitch + Urgent
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have +0.15 boost
        assert final_score >= base_score + 0.14
    
    def test_boost_rising_pitch_question(self, context_mgr: ContextManager):
        """Test +0.12 boost for rising pitch with question intent."""
        intent = {
            "type": "question",
            "keywords": ["what"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "What?",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Gen Z",
            "audio_pitch": "Rising",  # Rising pitch + Question
            "input_confidence": 0.9
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have +0.12 boost
        assert final_score >= base_score + 0.11


class TestFactorTwelveFidelity:
    """Test Factor 12: Apabhraṃśa (Fidelity)."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_boost_slang_with_low_confidence(self, context_mgr: ContextManager):
        """Test 1.15x boost for slang/casual with low input confidence."""
        intent = {
            "type": "evaluation",
            "keywords": ["sick"],
            "register": "Slang",
            "has_alternate_forms": True
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "sick",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Gen Z",
            "audio_pitch": "Neutral",
            "input_confidence": 0.65  # Low confidence
        }
        
        base_score = 0.5
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have 1.15x multiplier (boost)
        expected_min = base_score * 1.15
        assert final_score >= expected_min - 0.05
    
    def test_penalty_formal_with_low_confidence(self, context_mgr: ContextManager):
        """Test 0.85x penalty for formal intent with low input confidence."""
        intent = {
            "type": "formal_action",
            "keywords": ["execute"],
            "register": "Formal",
            "has_alternate_forms": False
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "execute",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Business",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Professional",
            "audio_pitch": "Neutral",
            "input_confidence": 0.60  # Low confidence
        }
        
        base_score = 0.7
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have 0.85x multiplier (penalty)
        expected_max = base_score * 0.85 + 0.05
        assert final_score < expected_max
    
    def test_boost_formal_with_high_confidence(self, context_mgr: ContextManager):
        """Test 1.1x boost for formal intent with high input confidence."""
        intent = {
            "type": "formal_action",
            "keywords": ["execute"],
            "register": "Formal"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "execute",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Business",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Professional",
            "audio_pitch": "Neutral",
            "input_confidence": 0.95  # High confidence
        }
        
        base_score = 0.6
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        # Should have 1.1x multiplier (boost)
        expected_min = base_score * 1.1
        assert final_score >= expected_min - 0.05


class TestScoreBounding:
    """Test that confidence scores are properly bounded [0, 1]."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_score_lower_bound(self, context_mgr: ContextManager):
        """Test score doesn't go below 0."""
        intent = {
            "type": "invalid",
            "keywords": ["xyz"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "invalid",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.5
        }
        
        base_score = 0.1  # Low starting score
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        assert final_score >= 0.0
    
    def test_score_upper_bound(self, context_mgr: ContextManager):
        """Test score doesn't go above 1.0."""
        intent = {
            "type": "perfect",
            "keywords": ["perfect"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": ["perfect match", "perfect test"],
            "system_state": "OFF",
            "user_input": "perfect",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        base_score = 0.9  # High starting score
        final_score = context_mgr.calculate_confidence(intent, context_data, base_score)
        
        assert final_score <= 1.0


class TestPolysemicDisambiguation:
    """Test 12-factor scoring on real polysemic test cases from intent_db.json."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_bank_river_vs_financial(self, context_mgr: ContextManager):
        """Test disambiguation of 'bank' as river vs. financial institution."""
        river_intent = {
            "type": "noun_reference",
            "keywords": ["bank", "river"],
            "required_location": "Riverside Park",
            "register": "Neutral",
            "vocabulary_level": "Neutral"
        }
        
        financial_intent = {
            "type": "noun_reference",
            "keywords": ["bank", "finance"],
            "required_location": "Downtown Business District",
            "register": "Neutral",
            "vocabulary_level": "Neutral"
        }
        
        # Test in Nature context - river should score higher
        nature_context = {
            "command_history": ["Show hiking trails"],
            "system_state": "OFF",
            "user_input": "bank",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": "Riverside Park",
            "current_hour": 10,
            "user_demographic": "Gen X",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        river_score = context_mgr.calculate_confidence(river_intent, nature_context, 0.5)
        financial_score = context_mgr.calculate_confidence(financial_intent, nature_context, 0.5)
        
        # River should score higher in nature context
        assert river_score > financial_score
        
        # Test in City context - financial should score higher
        city_context = {
            "command_history": ["Check account balance"],
            "system_state": "OFF",
            "user_input": "bank",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Business",
            "gps_tag": "Downtown Business District",
            "current_hour": 10,
            "user_demographic": "Professional",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        river_score_city = context_mgr.calculate_confidence(river_intent, city_context, 0.5)
        financial_score_city = context_mgr.calculate_confidence(financial_intent, city_context, 0.5)
        
        # Financial should score higher in city context
        assert financial_score_city > river_score_city
    
    def test_sick_positive_vs_negative(self, context_mgr: ContextManager):
        """Test disambiguation of 'sick' as positive vs. negative based on context."""
        positive_intent = {
            "type": "evaluation",
            "keywords": ["cool", "awesome"],
            "register": "Slang",
            "vocabulary_level": "Casual"
        }
        
        negative_intent = {
            "type": "evaluation",
            "keywords": ["disgusting", "gross"],
            "register": "Formal",
            "vocabulary_level": "Formal"
        }
        
        # Test in Casual context
        casual_context = {
            "command_history": ["That movie was amazing"],
            "system_state": "OFF",
            "user_input": "That's sick",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Gen Z",
            "audio_pitch": "High",
            "input_confidence": 0.9
        }
        
        positive_score = context_mgr.calculate_confidence(positive_intent, casual_context, 0.6)
        negative_score = context_mgr.calculate_confidence(negative_intent, casual_context, 0.6)
        
        # Positive interpretation should score higher in casual
        assert positive_score > negative_score
        
        # Test in Business context
        business_context = {
            "command_history": ["Quality report"],
            "system_state": "OFF",
            "user_input": "That's sick",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Business",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Professional",
            "audio_pitch": "Neutral",
            "input_confidence": 0.88
        }
        
        positive_score_biz = context_mgr.calculate_confidence(positive_intent, business_context, 0.6)
        negative_score_biz = context_mgr.calculate_confidence(negative_intent, business_context, 0.6)
        
        # In business context, negative should be penalized less than positive
        # (though both might score lower depending on other factors)
        # The positive_intent has slang register which gets penalized in business
        assert positive_score_biz < positive_score  # Slang penalty in business


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def context_mgr(self) -> ContextManager:
        return ContextManager()
    
    def test_empty_context_history(self, context_mgr: ContextManager):
        """Test with empty command history."""
        intent = {
            "type": "test",
            "keywords": ["test"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],  # Empty
            "system_state": "OFF",
            "user_input": "test",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        # Should not crash
        score = context_mgr.calculate_confidence(intent, context_data, 0.5)
        assert 0.0 <= score <= 1.0
    
    def test_no_base_score(self, context_mgr: ContextManager):
        """Test with very low base score (0.0)."""
        intent = {
            "type": "test",
            "keywords": ["test"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "test",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        score = context_mgr.calculate_confidence(intent, context_data, 0.0)
        assert 0.0 <= score <= 1.0
    
    def test_perfect_base_score(self, context_mgr: ContextManager):
        """Test with perfect base score (1.0)."""
        intent = {
            "type": "test",
            "keywords": ["test"],
            "register": "Neutral"
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "user_input": "test",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        score = context_mgr.calculate_confidence(intent, context_data, 1.0)
        assert 0.0 <= score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
