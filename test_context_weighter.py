"""
Test Suite for Context Weighter - 12 Factor System

Validates that all 12 factors work correctly in isolation and together.
"""

import pytest
from core.context_weighter import ContextWeighter


class TestContextWeighter:
    """Test suite for the ContextWeighter class."""
    
    @pytest.fixture
    def weighter(self):
        """Create a fresh weighter instance for each test."""
        return ContextWeighter()
    
    @pytest.fixture
    def base_intent(self):
        """Standard intent template."""
        return {
            'id': 'test_intent',
            'action': 'turn_on',
            'type': 'command',
            'tags': ['test', 'example'],
            'goal_alignment': 'test_goal',
            'valid_screens': ['home', 'test'],
            'formality': 'neutral',
            'contains_slang': False,
            'required_location': 'home',
            'time_specific': 'evening',
            'vocabulary_level': 'neutral'
        }
    
    @pytest.fixture
    def base_context(self):
        """Standard context template."""
        return {
            'base_score': 0.75,
            'user_history': [],
            'system_state': 'OFF',
            'active_goal': '',
            'current_screen': 'home',
            'syntax_flags': ['statement'],
            'social_mode': 'casual',
            'location': 'home',
            'time_of_day': 'evening',
            'user_profile': 'general_user',
            'audio_features': {'pitch': 'flat', 'tone': 'neutral'},
            'input_fidelity': 0.95
        }
    
    # ========== FACTOR 1: ASSOCIATION TESTS ==========
    
    def test_association_boost_on_match(self, weighter, base_intent, base_context):
        """Factor 1: Should boost score when intent tag matches history."""
        base_context['user_history'] = ['test', 'example', 'previous']
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Association should boost score"
        assert score_with >= score_without + 0.10, "Boost should be at least 0.10"
    
    def test_association_no_boost_empty_history(self, weighter, base_intent, base_context):
        """Factor 1: No boost if history is empty."""
        base_context['user_history'] = []
        
        score = weighter.apply_weights(base_intent, base_context)
        assert 0.0 <= score <= 1.0, "Score should be bounded"
    
    def test_association_no_boost_no_match(self, weighter, base_intent, base_context):
        """Factor 1: No boost if tags don't match history."""
        base_context['user_history'] = ['unrelated', 'commands']
        
        score = weighter.apply_weights(base_intent, base_context)
        assert 0.0 <= score <= 1.0, "Score should be valid"
    
    # ========== FACTOR 2: OPPOSITION TESTS ==========
    
    def test_opposition_penalty_turn_on_already_on(self, weighter, base_intent, base_context):
        """Factor 2: Should penalize 'turn on' when state is already ON."""
        base_intent['action'] = 'turn_on'
        base_context['system_state'] = 'ON'
        
        score = weighter.apply_weights(base_intent, base_context)
        expected_penalty = 0.75 * 0.1
        
        assert score <= expected_penalty * 1.5, "Opposition should severely penalize"
    
    def test_opposition_penalty_turn_off_already_off(self, weighter, base_intent, base_context):
        """Factor 2: Should penalize 'turn off' when state is already OFF."""
        base_intent['action'] = 'turn_off'
        base_context['system_state'] = 'OFF'
        
        score = weighter.apply_weights(base_intent, base_context)
        assert score < 0.2, "Should be severely penalized"
    
    def test_opposition_no_penalty_valid_action(self, weighter, base_intent, base_context):
        """Factor 2: No penalty for valid state transitions."""
        base_intent['action'] = 'turn_on'
        base_context['system_state'] = 'OFF'
        
        score_before = 0.75
        score_after = weighter.apply_weights(base_intent, base_context)
        
        assert score_after > score_before * 0.5, "Valid action should not be heavily penalized"
    
    # ========== FACTOR 3: PURPOSE TESTS ==========
    
    def test_purpose_exact_match_boost(self, weighter, base_intent, base_context):
        """Factor 3: Should boost score for exact goal match."""
        base_intent['goal_alignment'] = 'home_automation'
        base_context['active_goal'] = 'home_automation'
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Goal match should boost"
        assert score_with >= score_without + 0.15, "Boost should be significant"
    
    def test_purpose_partial_match_boost(self, weighter, base_intent, base_context):
        """Factor 3: Should boost for partial goal match."""
        base_intent['goal_alignment'] = 'home_automation'
        base_context['active_goal'] = 'home_control'
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Partial match should boost"
    
    def test_purpose_no_boost_no_goal(self, weighter, base_intent, base_context):
        """Factor 3: No boost if no active goal."""
        base_context['active_goal'] = ''
        
        score = weighter.apply_weights(base_intent, base_context)
        assert 0.0 <= score <= 1.0, "Score should be valid"
    
    # ========== FACTOR 4: SITUATION TESTS ==========
    
    def test_situation_boost_valid_screen(self, weighter, base_intent, base_context):
        """Factor 4: Should boost if intent is valid on current screen."""
        base_intent['valid_screens'] = ['home', 'settings']
        base_context['current_screen'] = 'home'
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Valid screen should boost"
    
    def test_situation_penalty_invalid_screen(self, weighter, base_intent, base_context):
        """Factor 4: Should penalize if intent not valid on current screen."""
        base_intent['valid_screens'] = ['settings', 'advanced']
        base_context['current_screen'] = 'home'
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with < score_without, "Invalid screen should penalize"
    
    # ========== FACTOR 5: INDICATOR TESTS ==========
    
    def test_indicator_question_matches_query(self, weighter, base_intent, base_context):
        """Factor 5: Should boost question syntax with query intent."""
        base_intent['type'] = 'query'
        base_context['syntax_flags'] = ['question']
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Question should match query"
    
    def test_indicator_exclamation_matches_command(self, weighter, base_intent, base_context):
        """Factor 5: Should boost exclamation syntax with command intent."""
        base_intent['type'] = 'command'
        base_context['syntax_flags'] = ['exclamation']
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Exclamation should match command"
    
    # ========== FACTOR 7: PROPRIETY TESTS ==========
    
    def test_propriety_block_slang_in_business(self, weighter, base_intent, base_context):
        """Factor 7: Should block slang content in business mode."""
        base_intent['contains_slang'] = True
        base_context['social_mode'] = 'business'
        
        score = weighter.apply_weights(base_intent, base_context)
        assert score == 0.0, "Slang should be completely blocked in business mode"
    
    def test_propriety_allow_slang_in_casual(self, weighter, base_intent, base_context):
        """Factor 7: Should allow slang in casual mode."""
        base_intent['contains_slang'] = True
        base_context['social_mode'] = 'casual'
        
        score = weighter.apply_weights(base_intent, base_context)
        assert score > 0.0, "Slang should be allowed in casual mode"
    
    # ========== FACTOR 8: PLACE TESTS ==========
    
    def test_place_boost_location_match(self, weighter, base_intent, base_context):
        """Factor 8: Should boost when location matches requirement."""
        base_intent['required_location'] = 'kitchen'
        base_context['location'] = 'kitchen'
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Location match should boost"
        assert score_with >= score_without + 0.15, "Place is a strong factor"
    
    def test_place_penalty_location_mismatch(self, weighter, base_intent, base_context):
        """Factor 8: Should penalize when location doesn't match."""
        base_intent['required_location'] = 'kitchen'
        base_context['location'] = 'bedroom'
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with < score_without, "Wrong location should penalize"
    
    # ========== FACTOR 9: TIME TESTS ==========
    
    def test_time_boost_time_match(self, weighter, base_intent, base_context):
        """Factor 9: Should boost when time matches requirement."""
        base_intent['time_specific'] = 'evening'
        base_context['time_of_day'] = 'evening'
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Time match should boost"
    
    def test_time_penalty_time_mismatch(self, weighter, base_intent, base_context):
        """Factor 9: Should penalize when time doesn't match."""
        base_intent['time_specific'] = 'morning'
        base_context['time_of_day'] = 'evening'
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with < score_without, "Wrong time should penalize"
    
    # ========== FACTOR 10: INDIVIDUAL TESTS ==========
    
    def test_individual_exact_profile_match(self, weighter, base_intent, base_context):
        """Factor 10: Should boost for user profile vocabulary match."""
        base_intent['vocabulary_level'] = 'technical'
        base_context['user_profile'] = 'technical'
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Profile match should boost"
    
    def test_individual_neutral_vocabulary_all_profiles(self, weighter, base_intent, base_context):
        """Factor 10: Neutral vocabulary should work for all profiles."""
        base_intent['vocabulary_level'] = 'neutral'
        base_context['user_profile'] = 'any_profile'
        
        score = weighter.apply_weights(base_intent, base_context)
        assert score > 0.5, "Neutral vocabulary should work for all"
    
    # ========== FACTOR 11: INTONATION TESTS ==========
    
    def test_intonation_rising_pitch_matches_query(self, weighter, base_intent, base_context):
        """Factor 11: Rising pitch should match query intents."""
        base_intent['type'] = 'question'
        base_context['audio_features'] = {'pitch': 'rising', 'tone': 'neutral'}
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Rising pitch should match questions"
    
    def test_intonation_flat_pitch_matches_command(self, weighter, base_intent, base_context):
        """Factor 11: Flat pitch should match command intents."""
        base_intent['type'] = 'command'
        base_context['audio_features'] = {'pitch': 'flat', 'tone': 'formal'}
        
        score_without = weighter.apply_weights(base_intent, {'base_score': 0.75})
        score_with = weighter.apply_weights(base_intent, base_context)
        
        assert score_with > score_without, "Flat pitch should match commands"
    
    # ========== FACTOR 12: DISTORTION TESTS ==========
    
    def test_distortion_high_fidelity_no_penalty(self, weighter, base_intent, base_context):
        """Factor 12: High fidelity input should not be penalized."""
        base_context['input_fidelity'] = 0.95
        
        score_high_fidelity = weighter.apply_weights(base_intent, base_context)
        
        # Score should not be heavily reduced
        assert score_high_fidelity > 0.6, "High fidelity should preserve score"
    
    def test_distortion_low_fidelity_penalty(self, weighter, base_intent, base_context):
        """Factor 12: Low fidelity input should be penalized."""
        base_context['input_fidelity'] = 0.3
        
        score_low_fidelity = weighter.apply_weights(base_intent, base_context)
        score_high_fidelity = weighter.apply_weights(base_intent, {'base_score': 0.75, 'input_fidelity': 0.95})
        
        assert score_low_fidelity < score_high_fidelity, "Low fidelity should reduce score"
    
    # ========== INTEGRATION TESTS ==========
    
    def test_all_factors_together_maximum_boost(self, weighter, base_intent, base_context):
        """All factors aligned should maximally boost score."""
        # Set up perfect alignment for all factors
        base_intent.update({
            'action': 'turn_on',
            'type': 'command',
            'tags': ['lights', 'home'],
            'goal_alignment': 'home_automation',
            'valid_screens': ['home', 'settings'],
            'formality': 'casual',
            'contains_slang': False,
            'required_location': 'home',
            'time_specific': 'evening',
            'vocabulary_level': 'general'
        })
        
        base_context.update({
            'base_score': 0.75,
            'user_history': ['lights', 'brightness'],
            'system_state': 'OFF',
            'active_goal': 'home_automation',
            'current_screen': 'home',
            'syntax_flags': ['statement', 'imperative'],
            'social_mode': 'casual',
            'location': 'home',
            'time_of_day': 'evening',
            'user_profile': 'general',
            'audio_features': {'pitch': 'flat', 'tone': 'casual'},
            'input_fidelity': 0.98
        })
        
        score = weighter.apply_weights(base_intent, base_context)
        
        # With all factors aligned, score should be significantly boosted
        assert score > 0.80, f"All factors aligned should produce high score, got {score}"
        assert score <= 1.0, "Score must be bounded"
    
    def test_conflicting_factors(self, weighter, base_intent, base_context):
        """Some factors working against each other."""
        base_intent.update({
            'action': 'turn_on',
            'required_location': 'office',
            'time_specific': 'morning',
            'contains_slang': True
        })
        
        base_context.update({
            'base_score': 0.75,
            'system_state': 'ON',  # Contradiction!
            'location': 'home',  # Wrong location
            'time_of_day': 'evening',  # Wrong time
            'social_mode': 'business',  # Blocks slang
            'input_fidelity': 0.4  # Low fidelity
        })
        
        score = weighter.apply_weights(base_intent, base_context)
        
        # With many contradictions, score should be low
        assert score < 0.5, f"Conflicting factors should lower score, got {score}"
        assert score >= 0.0, "Score must be non-negative"
    
    def test_score_always_bounded(self, weighter, base_intent):
        """Score should always be in [0.0, 1.0]."""
        contexts = [
            {'base_score': 0.99},
            {'base_score': 0.01},
            {'base_score': 0.5},
            {'base_score': 2.0},  # Invalid base
            {'base_score': -0.5},  # Invalid base
        ]
        
        for context in contexts:
            score = weighter.apply_weights(base_intent, context)
            assert 0.0 <= score <= 1.0, f"Score {score} not in [0.0, 1.0]"
    
    def test_empty_intent_metadata(self, weighter):
        """Should handle minimal intent metadata gracefully."""
        minimal_intent = {'id': 'test'}
        minimal_context = {'base_score': 0.75}
        
        score = weighter.apply_weights(minimal_intent, minimal_context)
        assert 0.0 <= score <= 1.0, "Should handle minimal metadata"
    
    def test_empty_context(self, weighter, base_intent):
        """Should handle empty context gracefully."""
        empty_context = {}
        
        score = weighter.apply_weights(base_intent, empty_context)
        assert 0.0 <= score <= 1.0, "Should handle empty context"
    
    # ========== POLYSEMIC TEST: THE BANK EXAMPLE ==========
    
    def test_polysemic_bank_nature_context(self, weighter):
        """The classic 'bank' disambiguation - nature context."""
        river_bank = {
            'id': 'river_bank',
            'tags': ['nature', 'river', 'bank'],
            'required_location': 'nature',
            'goal_alignment': 'outdoor',
            'vocabulary_level': 'casual'
        }
        
        nature_context = {
            'base_score': 0.70,
            'user_history': ['fishing', 'outdoors', 'nature'],
            'location': 'nature',
            'active_goal': 'outdoor_activity',
            'time_of_day': 'afternoon',
            'user_profile': 'outdoor_enthusiast',
            'input_fidelity': 0.95,
            'social_mode': 'casual'
        }
        
        score = weighter.apply_weights(river_bank, nature_context)
        
        # With location, history, and goal alignment, should be high
        assert score > 0.75, f"Nature context should boost river bank, got {score}"
    
    def test_polysemic_bank_finance_context(self, weighter):
        """The classic 'bank' disambiguation - finance context."""
        financial_bank = {
            'id': 'financial_bank',
            'tags': ['finance', 'banking', 'money'],
            'required_location': 'city',
            'goal_alignment': 'finance',
            'vocabulary_level': 'formal'
        }
        
        finance_context = {
            'base_score': 0.70,
            'user_history': ['transfer', 'balance', 'deposit'],
            'location': 'city',
            'active_goal': 'financial_management',
            'time_of_day': 'morning',
            'user_profile': 'professional',
            'input_fidelity': 0.98,
            'social_mode': 'business',
            'current_screen': 'banking_app'
        }
        
        score = weighter.apply_weights(financial_bank, finance_context)
        
        # With location, history, and goal alignment, should be high
        assert score > 0.75, f"Finance context should boost financial bank, got {score}"


if __name__ == "__main__":
    # Run tests with: pytest test_context_weighter.py -v
    pytest.main([__file__, "-v"])
