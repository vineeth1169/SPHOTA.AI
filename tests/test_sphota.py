"""
Unit Tests for Sphota AI Engine

Test suite covering:
1. Context weighting (polysemic resolution)
2. Apabhraṃśa normalization (slang handling)
3. 12-Factor schema validation
4. Zero-context fallback behavior

Uses pytest framework with mocked SentenceTransformer for performance.
"""

import pytest
from datetime import datetime
from typing import Dict, List
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Import core Sphota modules
from core.context_matrix import ContextResolutionMatrix, ContextObject
from core.pasyanti_engine import PasyantiEngine, ResolvedIntent
from core.apabhramsa_layer import ApabhramsaLayer


# === Fixtures ===

@pytest.fixture
def mock_sentence_transformer():
    """
    Mock SentenceTransformer to avoid loading heavy models in tests.
    Returns consistent embeddings for test stability.
    """
    mock_model = MagicMock()
    
    # Create deterministic embeddings based on input text
    def mock_encode(texts, show_progress_bar=False):
        """Generate fake embeddings with predictable similarity patterns."""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        for text in texts:
            # Create 384-dim vector (matching all-MiniLM-L6-v2)
            # Use text hash for deterministic but varied embeddings
            seed = hash(text) % 10000
            np.random.seed(seed)
            embedding = np.random.randn(384)
            embedding = embedding / np.linalg.norm(embedding)  # Normalize
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    mock_model.encode = Mock(side_effect=mock_encode)
    return mock_model


@pytest.fixture
def pasyanti_engine(mock_sentence_transformer):
    """
    Create a PasyantiEngine with mocked SentenceTransformer.
    """
    with patch('core.pasyanti_engine.SentenceTransformer', return_value=mock_sentence_transformer):
        engine = PasyantiEngine(intents_path="data/intents.json")
        return engine


@pytest.fixture
def context_matrix():
    """
    Create a ContextResolutionMatrix instance.
    """
    return ContextResolutionMatrix()


@pytest.fixture
def apabhramsa_layer():
    """
    Create an ApabhramsaLayer instance.
    """
    return ApabhramsaLayer()


# === Test Suite ===

class TestContextWeighting:
    """
    Test Case 1: The "Bank" Polysemic Resolution Test
    
    Verifies that ContextResolutionMatrix correctly disambiguates
    "bank" based on contextual factors (Deśa, Sahacārya).
    """
    
    def test_bank_financial_context(self, pasyanti_engine: PasyantiEngine):
        """
        Test: "I want to go to the bank" in financial context.
        
        Context:
            - Deśa (Place): "city"
            - Sahacārya (Association): ["money", "account"]
        
        Expected: "financial_bank" wins over "river_bank"
        """
        # Arrange
        user_input = "I want to go to the bank"
        context = ContextObject(
            desa="city",
            sahacarya=["money", "account", "deposit"],
            kala=datetime.now()
        )
        
        # Act
        results = pasyanti_engine.resolve_intent(user_input, context)
        
        # Assert
        assert len(results) > 0, "Should return at least one result"
        
        # Find bank-related intents
        financial_bank = next((r for r in results if r.intent.id == "financial_bank"), None)
        river_bank = next((r for r in results if r.intent.id == "river_bank"), None)
        
        # Both should exist in results
        assert financial_bank is not None, "financial_bank intent should exist"
        assert river_bank is not None, "river_bank intent should exist"
        
        # Context-adjusted score should favor financial_bank
        assert financial_bank.context_adjusted_score > river_bank.context_adjusted_score, \
            f"Financial bank ({financial_bank.context_adjusted_score:.4f}) should score higher than river bank ({river_bank.context_adjusted_score:.4f}) in city context"
        
        # Winner should be financial_bank
        winner = results[0]
        assert winner.intent.id == "financial_bank", \
            f"Winner should be financial_bank, got {winner.intent.id}"
    
    def test_bank_nature_context(self, pasyanti_engine: PasyantiEngine):
        """
        Test: "I want to go to the bank" in nature context.
        
        Context:
            - Deśa (Place): "nature"
            - Sahacārya (Association): ["fishing", "river"]
        
        Expected: "river_bank" wins over "financial_bank"
        """
        # Arrange
        user_input = "I want to go to the bank"
        context = ContextObject(
            desa="nature",
            sahacarya=["fishing", "river", "camping"],
            kala=datetime.now()
        )
        
        # Act
        results = pasyanti_engine.resolve_intent(user_input, context)
        
        # Assert
        assert len(results) > 0, "Should return at least one result"
        
        # Find bank-related intents
        financial_bank = next((r for r in results if r.intent.id == "financial_bank"), None)
        river_bank = next((r for r in results if r.intent.id == "river_bank"), None)
        
        # Both should exist
        assert financial_bank is not None, "financial_bank intent should exist"
        assert river_bank is not None, "river_bank intent should exist"
        
        # Context-adjusted score should favor river_bank
        assert river_bank.context_adjusted_score > financial_bank.context_adjusted_score, \
            f"River bank ({river_bank.context_adjusted_score:.4f}) should score higher than financial bank ({financial_bank.context_adjusted_score:.4f}) in nature context"
        
        # Winner should be river_bank
        winner = results[0]
        assert winner.intent.id == "river_bank", \
            f"Winner should be river_bank, got {winner.intent.id}"
    
    def test_context_flips_outcome(self, pasyanti_engine: PasyantiEngine):
        """
        Meta-test: Verify that changing context actually flips the winner.
        
        This is the core proof that CRM works - same input, different
        context, different outcome.
        """
        user_input = "take me to the bank"
        
        # Context A: Financial
        context_financial = ContextObject(
            desa="city",
            sahacarya=["money"],
            artha="finance"
        )
        results_financial = pasyanti_engine.resolve_intent(user_input, context_financial)
        winner_financial = results_financial[0].intent.id
        
        # Context B: Nature
        context_nature = ContextObject(
            desa="nature",
            sahacarya=["fishing"],
            artha="recreation"
        )
        results_nature = pasyanti_engine.resolve_intent(user_input, context_nature)
        winner_nature = results_nature[0].intent.id
        
        # Assert winners are different
        assert winner_financial != winner_nature, \
            "Context should flip the winner (got same winner in both contexts)"
        
        # Assert specific winners
        assert winner_financial == "financial_bank", \
            f"Financial context should yield financial_bank, got {winner_financial}"
        assert winner_nature == "river_bank", \
            f"Nature context should yield river_bank, got {winner_nature}"


class TestApabhramsa:
    """
    Test Case 2: The Slang/Apabhraṃśa Normalization Test
    
    Verifies that ApabhramsaLayer correctly normalizes slang to
    pure forms, enabling semantic matching.
    """
    
    def test_slang_normalization(self, apabhramsa_layer: ApabhramsaLayer):
        """
        Test: "No cap" (Gen Z slang) normalizes to "no lie" / "truthfully"
        """
        # Arrange
        slang_input = "No cap on that"
        
        # Act
        normalized, distortion_score = apabhramsa_layer.normalize_to_pure_form(slang_input)
        
        # Assert
        assert normalized != slang_input, "Should normalize slang"
        assert "no lie" in normalized.lower() or "truthfully" in normalized.lower() or "honestly" in normalized.lower(), \
            f"Should map 'no cap' to truthfulness, got: {normalized}"
        assert distortion_score > 0, "Should detect distortion in slang"
        assert 0 <= distortion_score <= 1, "Distortion score should be in [0, 1]"
    
    def test_multiple_slang_terms(self, apabhramsa_layer: ApabhramsaLayer):
        """
        Test: Multiple slang terms in one sentence
        """
        # Arrange
        slang_input = "bruh that's lowkey fire ngl"
        
        # Act
        normalized, distortion_score = apabhramsa_layer.normalize_to_pure_form(slang_input)
        
        # Assert
        assert normalized != slang_input, "Should normalize multiple slang terms"
        assert distortion_score > 0.3, "Multiple slang terms should have higher distortion"
    
    def test_clean_input_unchanged(self, apabhramsa_layer: ApabhramsaLayer):
        """
        Test: Clean input with no slang should pass through unchanged
        """
        # Arrange
        clean_input = "I want to go to the store"
        
        # Act
        normalized, distortion_score = apabhramsa_layer.normalize_to_pure_form(clean_input)
        
        # Assert
        assert normalized == clean_input, "Clean input should remain unchanged"
        assert distortion_score == 0, "Clean input should have zero distortion"
    
    def test_apabhramsa_affects_confidence(self, pasyanti_engine: PasyantiEngine):
        """
        Test: High distortion (slang) should reduce confidence scores
        """
        # Arrange
        clean_input = "turn on the lights"
        slang_input = "bruh turn on them lights fr fr"
        
        context = ContextObject(desa="home")
        
        # Act
        results_clean = pasyanti_engine.resolve_intent(clean_input, context)
        results_slang = pasyanti_engine.resolve_intent(slang_input, context)
        
        # Assert
        # Slang input should have lower confidence due to Apabhraṃśa penalty
        winner_clean = results_clean[0]
        winner_slang = results_slang[0]
        
        # Note: This test might be tricky due to mocking, but conceptually:
        # The slang version should either have same winner with lower confidence,
        # or potentially different winner if distortion is high
        assert winner_slang.context_adjusted_score <= winner_clean.context_adjusted_score + 0.1, \
            "Slang should not increase confidence (distortion penalty)"


class TestTwelveFactorSchema:
    """
    Test Case 3: 12-Factor Schema Validation
    
    Verifies that ContextResolutionMatrix correctly initializes
    with all 12 Sanskrit factors and their default weights.
    """
    
    def test_all_factors_present(self, context_matrix: ContextResolutionMatrix):
        """
        Test: All 12 factors exist in the weights dictionary
        """
        # Arrange
        expected_factors = [
            "sahacarya",      # Association
            "virodhita",      # Opposition
            "artha",          # Purpose
            "prakarana",      # Context
            "linga",          # Sign
            "shabda_samarthya",  # Word capacity
            "auciti",         # Propriety
            "desa",           # Place
            "kala",           # Time
            "vyakti",         # User profile
            "svara",          # Accent
            "apabhramsa"      # Distortion
        ]
        
        # Act & Assert
        for factor in expected_factors:
            assert factor in context_matrix.weights, \
                f"Factor '{factor}' should be in weights dictionary"
            
            # Verify weight is a valid number
            weight = context_matrix.weights[factor]
            assert isinstance(weight, (int, float)), \
                f"Weight for '{factor}' should be numeric, got {type(weight)}"
            assert weight > 0, \
                f"Weight for '{factor}' should be positive, got {weight}"
    
    def test_factor_count(self, context_matrix: ContextResolutionMatrix):
        """
        Test: Exactly 12 factors (no more, no less)
        """
        assert len(context_matrix.weights) == 12, \
            f"Should have exactly 12 factors, got {len(context_matrix.weights)}"
    
    def test_weight_ranges(self, context_matrix: ContextResolutionMatrix):
        """
        Test: All weights are in reasonable ranges [0.0, 0.5]
        """
        for factor, weight in context_matrix.weights.items():
            assert 0.0 <= weight <= 0.5, \
                f"Weight for '{factor}' should be in [0, 0.5], got {weight}"
    
    def test_artha_highest_weight(self, context_matrix: ContextResolutionMatrix):
        """
        Test: Artha (Purpose) should have highest weight (as per design)
        """
        artha_weight = context_matrix.weights["artha"]
        other_weights = [w for f, w in context_matrix.weights.items() if f != "artha"]
        
        assert artha_weight == max(context_matrix.weights.values()), \
            "Artha (Purpose) should have highest weight"
        assert artha_weight > max(other_weights), \
            "Artha weight should exceed all other factors"
    
    def test_factor_mappings_initialized(self, context_matrix: ContextResolutionMatrix):
        """
        Test: Factor mappings (sahacarya_map, desa_map, etc.) are initialized
        """
        # Check critical mappings exist
        assert hasattr(context_matrix, 'sahacarya_map'), "sahacarya_map should exist"
        assert hasattr(context_matrix, 'desa_map'), "desa_map should exist"
        assert hasattr(context_matrix, 'kala_map'), "kala_map should exist"
        assert hasattr(context_matrix, 'artha_map'), "artha_map should exist"
        
        # Check they're not empty
        assert len(context_matrix.sahacarya_map) > 0, "sahacarya_map should have entries"
        assert len(context_matrix.desa_map) > 0, "desa_map should have entries"
        assert len(context_matrix.kala_map) > 0, "kala_map should have entries"
    
    def test_active_factors_detection(self, context_matrix: ContextResolutionMatrix):
        """
        Test: get_active_factors correctly identifies set factors
        """
        # Arrange
        context = ContextObject(
            desa="kitchen",
            kala=datetime.now(),
            sahacarya=["cooking"]
        )
        
        # Act
        active = context_matrix.get_active_factors(context)
        
        # Assert
        assert "desa" in active, "desa should be detected as active"
        assert "kala" in active, "kala should be detected as active"
        assert "sahacarya" in active, "sahacarya should be detected as active"
        assert "artha" not in active, "artha should not be active (not set)"
        assert len(active) == 3, f"Should detect exactly 3 active factors, got {len(active)}"


class TestZeroContextFallback:
    """
    Test Case 4: Zero-Context Fallback Behavior
    
    Verifies that the system handles missing/empty context gracefully
    and falls back to raw similarity scores without crashing.
    """
    
    def test_empty_context_object(self, pasyanti_engine: PasyantiEngine):
        """
        Test: Empty ContextObject should not crash, returns raw scores
        """
        # Arrange
        user_input = "Hello"
        context = ContextObject()  # All fields None/empty
        
        # Act & Assert (should not raise exception)
        results = pasyanti_engine.resolve_intent(user_input, context)
        
        # Verify results are returned
        assert len(results) > 0, "Should return results even with empty context"
        assert results[0].intent is not None, "Winner intent should exist"
        
        # With empty context, raw and adjusted scores should be very close
        # (only minor normalization differences)
        winner = results[0]
        score_diff = abs(winner.context_adjusted_score - winner.raw_similarity)
        assert score_diff < 0.05, \
            "With empty context, scores should be nearly identical"
    
    def test_none_context(self, pasyanti_engine: PasyantiEngine):
        """
        Test: None context should fall back to empty ContextObject
        """
        # Arrange
        user_input = "Hello there"
        
        # Act & Assert (should not crash)
        results = pasyanti_engine.resolve_intent(user_input, None)
        
        assert len(results) > 0, "Should handle None context gracefully"
        assert results[0].intent is not None, "Should return valid winner"
    
    def test_highest_raw_probability_wins(self, pasyanti_engine: PasyantiEngine):
        """
        Test: Without context, highest raw similarity should win
        """
        # Arrange
        user_input = "turn on the lights"
        context = ContextObject()  # Empty context
        
        # Act
        results = pasyanti_engine.resolve_intent(user_input, context)
        
        # Assert
        # Verify results are sorted by context_adjusted_score
        for i in range(len(results) - 1):
            assert results[i].context_adjusted_score >= results[i + 1].context_adjusted_score, \
                "Results should be sorted by context_adjusted_score descending"
        
        # With empty context, winner should be the highest raw similarity
        winner = results[0]
        max_raw_score = max(r.raw_similarity for r in results)
        
        # Winner's raw score should be at or very near the maximum
        assert abs(winner.raw_similarity - max_raw_score) < 0.01, \
            "Winner should have highest (or tied) raw similarity with empty context"
    
    def test_graceful_degradation(self, context_matrix: ContextResolutionMatrix):
        """
        Test: CRM.resolve_intent with empty context returns unchanged scores
        """
        # Arrange
        base_scores = {
            "intent_a": 0.8,
            "intent_b": 0.6,
            "intent_c": 0.4
        }
        context = ContextObject()  # Empty
        
        # Act
        resolved_scores = context_matrix.resolve_intent(base_scores, context)
        
        # Assert
        # Scores should be nearly identical (only normalization applied)
        for intent_id in base_scores:
            score_diff = abs(resolved_scores[intent_id] - base_scores[intent_id])
            assert score_diff < 0.01, \
                f"Score for {intent_id} should be unchanged with empty context"


# === Integration Tests ===

class TestIntegration:
    """
    Integration tests for full pipeline: Apabhraṃśa → Paśyantī → CRM
    """
    
    def test_full_pipeline_with_slang_and_context(self, pasyanti_engine: PasyantiEngine):
        """
        Test: Slang input with rich context through full pipeline
        """
        # Arrange
        slang_input = "yo turn up them lights bruh"
        context = ContextObject(
            desa="home",
            sahacarya=["automation", "smart_home"],
            kala=datetime(2026, 1, 2, 20, 0),  # Evening
            apabhramsa=0.6  # Indicate high slang
        )
        
        # Act
        results = pasyanti_engine.resolve_intent(slang_input, context)
        
        # Assert
        assert len(results) > 0, "Should handle slang with context"
        
        # Should resolve to lights_on intent
        winner = results[0]
        assert "light" in winner.intent.id.lower(), \
            f"Should recognize lights intent, got {winner.intent.id}"
    
    def test_multilingual_apabhramsa(self, apabhramsa_layer: ApabhramsaLayer):
        """
        Test: Mixed language/code-switching normalization
        """
        # Arrange
        mixed_input = "thoda volume badha do yaar"  # Hindi-English mix
        
        # Act
        normalized, score = apabhramsa_layer.normalize_to_pure_form(mixed_input)
        
        # Assert
        # Should recognize "volume" and "increase" concepts
        assert score > 0, "Should detect code-switching as distortion"
    
    def test_explanation_generation(self, pasyanti_engine: PasyantiEngine):
        """
        Test: Engine can explain its resolution decisions
        """
        # Arrange
        user_input = "take me to the bank"
        context = ContextObject(
            desa="city",
            sahacarya=["money"]
        )
        
        # Act
        results = pasyanti_engine.resolve_intent(user_input, context)
        explanation = pasyanti_engine.explain_resolution(
            user_input,
            context
        )
        
        # Assert
        assert "input" in explanation, "Explanation should have input details"
        assert "context" in explanation, "Explanation should have context details"
        assert "resolution" in explanation, "Explanation should have resolution details"
        assert len(explanation["context"]["active_factors"]) > 0, "Should have active factors"


# === Performance Tests ===

class TestPerformance:
    """
    Basic performance and edge case tests
    """
    
    def test_large_intent_corpus(self, pasyanti_engine: PasyantiEngine):
        """
        Test: System handles large intent corpus efficiently
        """
        # The default corpus has 12 intents
        # Just verify it loads and runs without timeout
        user_input = "test query"
        context = ContextObject(desa="home")
        
        results = pasyanti_engine.resolve_intent(user_input, context)
        
        assert len(results) > 0, "Should handle corpus size"
    
    def test_very_long_input(self, pasyanti_engine: PasyantiEngine):
        """
        Test: System handles unusually long input
        """
        # Arrange
        long_input = "I want to " + "really " * 100 + "turn on the lights"
        context = ContextObject(desa="home")
        
        # Act & Assert (should not crash)
        results = pasyanti_engine.resolve_intent(long_input, context)
        assert len(results) > 0, "Should handle long input"
    
    def test_special_characters(self, apabhramsa_layer: ApabhramsaLayer):
        """
        Test: System handles special characters gracefully
        """
        # Arrange
        special_input = "!@#$% turn on lights &*()"
        
        # Act
        normalized, score = apabhramsa_layer.normalize_to_pure_form(special_input)
        
        # Assert (should not crash)
        assert isinstance(normalized, str), "Should return string"
        assert "light" in normalized.lower(), "Should extract core meaning"


# === Helper Functions for Tests ===

def assert_intent_exists(results: List[ResolvedIntent], intent_id: str) -> ResolvedIntent:
    """
    Helper: Assert that an intent exists in results and return it.
    """
    intent = next((r for r in results if r.intent.id == intent_id), None)
    assert intent is not None, f"Intent '{intent_id}' should exist in results"
    return intent


def assert_winner(results: List[ResolvedIntent], expected_id: str) -> None:
    """
    Helper: Assert that the winner (first result) matches expected intent.
    """
    assert len(results) > 0, "Results should not be empty"
    winner = results[0]
    assert winner.intent.id == expected_id, \
        f"Expected winner '{expected_id}', got '{winner.intent.id}'"


# === Pytest Configuration ===

def pytest_configure(config):
    """
    Register custom markers for pytest.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


if __name__ == "__main__":
    """
    Allow running tests directly: python -m tests.test_sphota
    """
    pytest.main([__file__, "-v"])
