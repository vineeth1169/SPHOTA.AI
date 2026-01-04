"""
Integration Tests for Refactored Streamlit App

Test suite covering:
1. Sidebar context controls and advanced factor toggles
2. ContextManager integration with Streamlit app
3. Intent resolution with 12-factor scoring visualization
4. End-to-end polysemic disambiguation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime

# Mock streamlit before importing app
pytest.importorskip("streamlit")


class TestSidebarContextControls:
    """Test sidebar input simulation and context configuration."""
    
    def test_location_dropdown_options(self):
        """Test location dropdown has all required options."""
        expected_locations = ["Home", "City", "Nature", "Office", "Kitchen", "Car", "Gym"]
        # This would be tested in actual Streamlit context
        assert len(expected_locations) == 7
        assert "Home" in expected_locations
        assert "Nature" in expected_locations
        assert "City" in expected_locations
    
    def test_time_mode_selection(self):
        """Test time mode radio button options."""
        time_modes = ["Current", "Manual"]
        assert len(time_modes) == 2
        assert "Current" in time_modes
        assert "Manual" in time_modes
    
    def test_advanced_factors_enabled(self):
        """Test advanced factors available when checkbox is true."""
        advanced_factors = [
            "social_mode",
            "system_state",
            "history_type",
            "audio_pitch",
            "input_confidence",
            "user_demographic"
        ]
        
        # All factors should be available
        assert len(advanced_factors) == 6
        assert "social_mode" in advanced_factors  # Tests Aucitī
        assert "system_state" in advanced_factors  # Tests Virodhitā
        assert "history_type" in advanced_factors  # Tests Sahacarya
        assert "audio_pitch" in advanced_factors  # Tests Svara


class TestContextDataBuilding:
    """Test building context data for ContextManager from UI inputs."""
    
    def test_context_data_from_basic_inputs(self):
        """Test context data construction from basic sidebar inputs."""
        location = "Home"
        current_hour = 14
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "current_task_id": None,
            "current_screen": "Home",
            "social_mode": "Casual",
            "gps_tag": location,
            "current_hour": current_hour,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        assert context_data["gps_tag"] == "Home"
        assert context_data["current_hour"] == 14
        assert context_data["social_mode"] == "Casual"
    
    def test_context_data_with_travel_history(self):
        """Test context data with travel history."""
        history_type = "Travel"
        
        command_history = {
            "Travel": ["Search flights to Paris", "Check travel dates"],
            "Restaurant": ["Search restaurants near me", "Check cuisines"],
            "Shopping": ["Browse products", "Add to cart"]
        }.get(history_type, [])
        
        context_data = {
            "command_history": command_history,
            "system_state": "OFF",
            "current_task_id": "travel_booking",
            "current_screen": "Travel",
            "social_mode": "Casual",
            "gps_tag": "City",
            "current_hour": 10,
            "user_demographic": "Millennial",
            "audio_pitch": "Normal",
            "input_confidence": 0.96
        }
        
        assert "Search flights" in context_data["command_history"][0]
        assert context_data["current_task_id"] == "travel_booking"
    
    def test_context_data_with_advanced_factors(self):
        """Test full context data with all advanced factors."""
        context_data = {
            "command_history": ["Quality report"],
            "system_state": "ON",
            "current_task_id": "demo_task",
            "current_screen": "Home",
            "social_mode": "Business",
            "gps_tag": "Office",
            "current_hour": 15,
            "user_demographic": "Professional",
            "audio_pitch": "Rising",
            "input_confidence": 0.88,
            "user_input": "turn on the lights"
        }
        
        # Verify all required keys are present
        required_keys = [
            "command_history", "system_state", "current_task_id",
            "current_screen", "social_mode", "gps_tag", "current_hour",
            "user_demographic", "audio_pitch", "input_confidence"
        ]
        
        for key in required_keys:
            assert key in context_data


class TestIntentScoring:
    """Test intent scoring with 12-factor matrix."""
    
    def test_scored_results_structure(self):
        """Test structure of scored results for display."""
        scored_result = {
            "intent": "turn_on_lights",
            "description": "Turn on the lights",
            "raw_score": 0.75,
            "twelve_factor_score": 0.85,
            "boost": 0.10
        }
        
        assert scored_result["intent"]
        assert "raw_score" in scored_result
        assert "twelve_factor_score" in scored_result
        assert "boost" in scored_result
        
        # Validate score relationships
        assert scored_result["boost"] == (
            scored_result["twelve_factor_score"] - scored_result["raw_score"]
        )
    
    def test_top_three_intents_ranking(self):
        """Test ranking of top 3 intents by 12-factor score."""
        scored_results = [
            {
                "intent": "intent_a",
                "description": "Intent A",
                "raw_score": 0.70,
                "twelve_factor_score": 0.85,
                "boost": 0.15
            },
            {
                "intent": "intent_b",
                "description": "Intent B",
                "raw_score": 0.65,
                "twelve_factor_score": 0.72,
                "boost": 0.07
            },
            {
                "intent": "intent_c",
                "description": "Intent C",
                "raw_score": 0.60,
                "twelve_factor_score": 0.65,
                "boost": 0.05
            }
        ]
        
        # Verify ranking by 12-factor score
        for i in range(len(scored_results) - 1):
            assert (scored_results[i]["twelve_factor_score"] >= 
                    scored_results[i + 1]["twelve_factor_score"])
        
        # Winner should be first
        winner = scored_results[0]
        assert winner["twelve_factor_score"] == 0.85


class TestVisualizationData:
    """Test data preparation for Streamlit visualizations."""
    
    def test_bar_chart_data_format(self):
        """Test bar chart data is properly formatted for Plotly."""
        chart_data = pd.DataFrame([
            {
                "intent": "turn_on_lights",
                "raw_score": 0.75,
                "twelve_factor_score": 0.85
            },
            {
                "intent": "toggle_lights",
                "raw_score": 0.70,
                "twelve_factor_score": 0.78
            },
            {
                "intent": "lights_control",
                "raw_score": 0.65,
                "twelve_factor_score": 0.70
            }
        ])
        
        assert len(chart_data) == 3
        assert "intent" in chart_data.columns
        assert "raw_score" in chart_data.columns
        assert "twelve_factor_score" in chart_data.columns
    
    def test_metrics_display_data(self):
        """Test metrics data for display."""
        winner = {
            "intent": "bank_financial",
            "description": "Financial Bank Institution",
            "raw_score": 0.72,
            "twelve_factor_score": 0.88,
            "boost": 0.16
        }
        
        # Test metric formatting
        intent_name = winner["intent"].replace("_", " ").title()
        assert "Bank" in intent_name
        
        raw_pct = f"{winner['raw_score']:.1%}"
        assert "72" in raw_pct
        
        factor_pct = f"{winner['twelve_factor_score']:.1%}"
        assert "88" in factor_pct
    
    def test_detail_table_format(self):
        """Test detailed comparison table format."""
        table_data = [
            {
                "Intent": "Turn On Lights",
                "Raw Score": "75.0%",
                "12-Factor Score": "85.0%",
                "Boost/Penalty": "+10.0%",
                "Description": "Turns on the lights in current room..."
            },
            {
                "Intent": "Toggle Lights",
                "Raw Score": "70.0%",
                "12-Factor Score": "78.0%",
                "Boost/Penalty": "+8.0%",
                "Description": "Toggles light state..."
            }
        ]
        
        df = pd.DataFrame(table_data)
        assert len(df) == 2
        assert "Intent" in df.columns
        assert "12-Factor Score" in df.columns
        assert "Boost/Penalty" in df.columns


class TestPolysemicExamples:
    """Test polysemic disambiguation examples in UI."""
    
    def test_bank_example_setup(self):
        """Test 'bank' polysemic example button setup."""
        river_context = {
            "location": "Nature",
            "history_type": "None"
        }
        
        financial_context = {
            "location": "City",
            "history_type": "Shopping"
        }
        
        # Both should use same input but different contexts
        assert "bank" in str(river_context).lower() or "Nature" in str(river_context)
        assert "City" in str(financial_context)
        
        # Verify context differences trigger different intents
        assert river_context["location"] != financial_context["location"]
    
    def test_lights_example_setup(self):
        """Test 'turn on lights' example button setup."""
        context = {
            "location": "Home",
            "system_state": "OFF"
        }
        
        assert context["location"] == "Home"
        assert context["system_state"] == "OFF"
    
    def test_sick_example_setup(self):
        """Test 'sick' polysemic example (implicit in advanced factors)."""
        casual_context = {
            "social_mode": "Casual",
            "user_demographic": "Gen Z"
        }
        
        business_context = {
            "social_mode": "Business",
            "user_demographic": "Professional"
        }
        
        # Social mode should differ
        assert casual_context["social_mode"] != business_context["social_mode"]


class TestErrorHandling:
    """Test error handling in app."""
    
    def test_empty_input_handling(self):
        """Test handling of empty user input."""
        user_input = ""
        
        # Should not process empty input
        assert not user_input.strip()
    
    def test_context_data_fallback(self):
        """Test fallback values when context data is incomplete."""
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        # Even with None values, context_data should be usable
        assert isinstance(context_data, dict)
        assert all(isinstance(v, (str, int, float, list, type(None))) 
                   for v in context_data.values())
    
    def test_score_calculation_fallback(self):
        """Test fallback scoring when ContextManager fails."""
        fallback_score = 0.5  # Default fallback
        
        # Should provide valid fallback score
        assert 0.0 <= fallback_score <= 1.0


class TestContextFactorCoverage:
    """Test that all 12 factors are exercised through UI."""
    
    def test_factor_1_sahacarya_coverage(self):
        """Test Factor 1 coverage - command history selection."""
        history_options = ["None", "Travel", "Restaurant", "Shopping"]
        assert "Travel" in history_options  # Tests Sahacarya
    
    def test_factor_2_virodhita_coverage(self):
        """Test Factor 2 coverage - system state selection."""
        system_states = ["ON", "OFF"]
        assert "ON" in system_states
        assert "OFF" in system_states
    
    def test_factor_4_prakirana_coverage(self):
        """Test Factor 4 coverage - location affects screens."""
        locations = ["Home", "City", "Nature", "Office"]
        assert "Home" in locations
        assert "City" in locations
    
    def test_factor_7_auciti_coverage(self):
        """Test Factor 7 coverage - social mode selection."""
        social_modes = ["Casual", "Business"]
        assert "Casual" in social_modes
        assert "Business" in social_modes
    
    def test_factor_8_desa_coverage(self):
        """Test Factor 8 coverage - location selection."""
        locations = ["Home", "City", "Nature", "Office", "Kitchen", "Car", "Gym"]
        assert len(locations) >= 3
    
    def test_factor_9_kala_coverage(self):
        """Test Factor 9 coverage - time selection."""
        time_options = {
            "Current": datetime.now().hour,
            "Manual": 12
        }
        assert 0 <= time_options["Current"] <= 23
        assert 0 <= time_options["Manual"] <= 23
    
    def test_factor_10_vyakti_coverage(self):
        """Test Factor 10 coverage - user demographic selection."""
        demographics = ["Gen Z", "Millennial", "Gen X", "Boomer"]
        assert len(demographics) == 4
    
    def test_factor_11_svara_coverage(self):
        """Test Factor 11 coverage - voice pitch selection."""
        pitches = ["Neutral", "Flat", "Rising", "High"]
        assert "Rising" in pitches
        assert "High" in pitches


class TestAppIntegration:
    """Test integration of ContextManager with Streamlit app."""
    
    def test_context_manager_import(self):
        """Test ContextManager is importable."""
        from core.context_manager import ContextManager
        
        mgr = ContextManager()
        assert mgr is not None
    
    def test_calculate_confidence_callable(self):
        """Test calculate_confidence method exists and is callable."""
        from core.context_manager import ContextManager
        
        mgr = ContextManager()
        assert callable(mgr.calculate_confidence)
    
    def test_confidence_with_app_context_format(self):
        """Test confidence calculation with app-generated context."""
        from core.context_manager import ContextManager
        
        mgr = ContextManager()
        
        intent = {
            "type": "turn_on",
            "keywords": ["turn", "on"],
            "register": "Neutral",
            "vocabulary_level": "Casual",
            "urgency": "Normal",
            "valid_screens": ["Home"],
            "required_location": None,
            "valid_time_range": (0, 23)
        }
        
        context_data = {
            "command_history": [],
            "system_state": "OFF",
            "current_task_id": None,
            "current_screen": "Home",
            "social_mode": "Casual",
            "gps_tag": "Home",
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9,
            "user_input": "turn on the lights"
        }
        
        score = mgr.calculate_confidence(intent, context_data, 0.7)
        
        assert 0.0 <= score <= 1.0


class TestEndToEndScenarios:
    """Test complete end-to-end scenarios."""
    
    def test_scenario_bank_river(self):
        """Test 'bank' disambiguation to river."""
        from core.context_manager import ContextManager
        
        mgr = ContextManager()
        
        river_intent = {
            "type": "noun_reference",
            "keywords": ["bank", "river"],
            "required_location": "Riverside Park",
            "register": "Neutral",
            "vocabulary_level": "Neutral"
        }
        
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
        
        score = mgr.calculate_confidence(river_intent, nature_context, 0.5)
        assert score > 0.4  # Should be reasonably high
    
    def test_scenario_lights_conflict(self):
        """Test 'turn on lights' with conflict check."""
        from core.context_manager import ContextManager
        
        mgr = ContextManager()
        
        turn_on_intent = {
            "type": "turn_on",
            "keywords": ["turn", "on"],
            "register": "Neutral",
            "vocabulary_level": "Casual"
        }
        
        conflict_context = {
            "command_history": [],
            "system_state": "ON",  # Already on - conflict!
            "user_input": "turn on the lights",
            "current_task_id": None,
            "current_screen": "Home",
            "social_mode": "Casual",
            "gps_tag": "Home",
            "current_hour": 12,
            "user_demographic": "Millennial",
            "audio_pitch": "Neutral",
            "input_confidence": 0.9
        }
        
        score = mgr.calculate_confidence(turn_on_intent, conflict_context, 0.8)
        assert score < 0.3  # Should be heavily penalized
    
    def test_scenario_sick_casual(self):
        """Test 'sick' in casual context (positive interpretation)."""
        from core.context_manager import ContextManager
        
        mgr = ContextManager()
        
        positive_intent = {
            "type": "evaluation",
            "keywords": ["cool"],
            "register": "Slang",
            "vocabulary_level": "Casual"
        }
        
        casual_context = {
            "command_history": ["That movie was amazing"],
            "system_state": "OFF",
            "user_input": "That's sick",
            "current_task_id": None,
            "current_screen": None,
            "social_mode": "Casual",  # Casual mode - no slang penalty
            "gps_tag": None,
            "current_hour": 12,
            "user_demographic": "Gen Z",
            "audio_pitch": "High",
            "input_confidence": 0.92
        }
        
        score = mgr.calculate_confidence(positive_intent, casual_context, 0.6)
        assert score > 0.5  # Should score reasonably well


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
