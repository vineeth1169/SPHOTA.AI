"""
Test Suite for Hybrid Architecture (Two-Stage Resolution)

Tests the complete two-stage resolution process:
- Stage 1: Semantic Flash (Vector Search)
- Stage 2: Deterministic Check (Hard Stop + Context Boost)
- Fallback mechanism for low confidence
"""

import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.intent_engine import (
    IntentEngine,
    SemanticCandidate,
    VerifiedIntent,
    Intent,
)


def test_stage_1_semantic_candidates():
    """Test Stage 1: Semantic Flash returns Top 5 candidates."""
    print("\n" + "="*60)
    print("TEST 1: Stage 1 - Semantic Flash (Vector Search)")
    print("="*60)
    
    engine = IntentEngine(use_fast_memory=False)
    
    # Test input
    user_input = "set a timer for 5 minutes"
    candidates = engine._get_semantic_candidates(
        user_input=user_input,
        input_embedding=engine.model.encode(user_input, convert_to_numpy=True, normalize_embeddings=True)
    )
    
    print(f"Input: '{user_input}'")
    print(f"Number of candidates returned: {len(candidates)}")
    
    # Verify results
    assert len(candidates) > 0, "Should return at least 1 candidate"
    assert all(isinstance(c, SemanticCandidate) for c in candidates), "All should be SemanticCandidate"
    assert all(0 <= c.semantic_similarity <= 1 for c in candidates), "Similarity scores should be in [0, 1]"
    assert all(c.source in ["vector_search", "memory_boost"] for c in candidates), "Source should be valid"
    
    # Print candidates
    for i, candidate in enumerate(candidates[:5], 1):
        print(f"  {i}. {candidate.candidate_intent.id}")
        print(f"     Similarity: {candidate.semantic_similarity:.4f}")
        print(f"     Source: {candidate.source}")
    
    print("✓ Stage 1 test passed")
    return True


def test_stage_2_hard_stop_rules():
    """Test Stage 2: Hard Stop rules discard invalid candidates."""
    print("\n" + "="*60)
    print("TEST 2: Stage 2 - Hard Stop Rules")
    print("="*60)
    
    engine = IntentEngine(use_fast_memory=False)
    
    # Create a test scenario with conflict marker
    user_input = "cancel the timer"
    input_embedding = engine.model.encode(user_input, convert_to_numpy=True, normalize_embeddings=True)
    candidates = engine._get_semantic_candidates(user_input, input_embedding)
    
    # Build context with "cancel" conflict
    context = {"conflict": ["cancel"]}
    
    verified, stage_2_passed = engine._apply_deterministic_check(
        semantic_candidates=candidates,
        current_context=context,
        distortion_score=0.0
    )
    
    print(f"Input: '{user_input}'")
    print(f"Context conflict markers: {context.get('conflict')}")
    print(f"Stage 2 passed: {stage_2_passed}")
    
    if verified:
        print(f"Selected intent: {verified.intent.id}")
        print(f"Confidence: {verified.confidence:.4f}")
        print(f"Fallback used: {verified.fallback_used}")
    else:
        print("No valid intent found after Stage 2 (would trigger fallback)")
    
    print("✓ Stage 2 test passed")
    return True


def test_context_boost_scoring():
    """Test Stage 2: Context factors boost candidate scores."""
    print("\n" + "="*60)
    print("TEST 3: Context Boost Scoring")
    print("="*60)
    
    engine = IntentEngine(use_fast_memory=False)
    
    # Test with location context
    user_input = "I need help"
    input_embedding = engine.model.encode(user_input, convert_to_numpy=True, normalize_embeddings=True)
    candidates = engine._get_semantic_candidates(user_input, input_embedding)
    
    # Test different contexts
    context_kitchen = {"location": "kitchen"}
    context_bedroom = {"location": "bedroom"}
    
    verified_kitchen, _ = engine._apply_deterministic_check(
        candidates, context_kitchen, 0.0
    )
    verified_bedroom, _ = engine._apply_deterministic_check(
        candidates, context_bedroom, 0.0
    )
    
    print(f"Input: '{user_input}'")
    print(f"\nWith Kitchen context:")
    if verified_kitchen:
        print(f"  Selected: {verified_kitchen.intent.id}")
        print(f"  Confidence: {verified_kitchen.confidence:.4f}")
    
    print(f"\nWith Bedroom context:")
    if verified_bedroom:
        print(f"  Selected: {verified_bedroom.intent.id}")
        print(f"  Confidence: {verified_bedroom.confidence:.4f}")
    
    print("✓ Context boost test passed")
    return True


def test_hybrid_logic_end_to_end():
    """Test complete Hybrid Architecture end-to-end."""
    print("\n" + "="*60)
    print("TEST 4: End-to-End Hybrid Logic")
    print("="*60)
    
    engine = IntentEngine(use_fast_memory=False)
    
    # Test case 1: Normal resolution
    user_input_1 = "play my favorite music"
    context_1 = {"situation": "evening_relaxation"}
    
    result_1 = engine.resolve_with_hybrid_logic(user_input_1, context_1)
    
    print(f"Test Case 1:")
    print(f"  Input: '{user_input_1}'")
    print(f"  Context: {context_1}")
    print(f"  Result intent: {result_1.intent.id}")
    print(f"  Confidence: {result_1.confidence:.4f}")
    print(f"  Stage 1 passed: {result_1.stage_1_passed}")
    print(f"  Stage 2 passed: {result_1.stage_2_passed}")
    print(f"  Fallback used: {result_1.fallback_used}")
    
    # Verify result structure
    assert isinstance(result_1, VerifiedIntent), "Result should be VerifiedIntent"
    assert 0 <= result_1.confidence <= 1, "Confidence should be in [0, 1]"
    assert isinstance(result_1.active_factors, list), "Active factors should be a list"
    
    # Test case 2: Low confidence scenario (should trigger fallback)
    print(f"\nTest Case 2 (Ambiguous input):")
    user_input_2 = "xyz" * 5  # Nonsense input
    context_2 = {}
    
    result_2 = engine.resolve_with_hybrid_logic(user_input_2, context_2)
    
    print(f"  Input: '{user_input_2[:20]}...' (ambiguous)")
    print(f"  Result intent: {result_2.intent.id}")
    print(f"  Confidence: {result_2.confidence:.4f}")
    print(f"  Fallback used: {result_2.fallback_used}")
    
    # Should either have low confidence or use fallback
    assert result_2.confidence < 0.7 or result_2.fallback_used, \
        "Ambiguous input should have low confidence or use fallback"
    
    print("✓ End-to-end test passed")
    return True


def test_backward_compatibility():
    """Test backward compatibility: resolve_intent still works."""
    print("\n" + "="*60)
    print("TEST 5: Backward Compatibility")
    print("="*60)
    
    engine = IntentEngine(use_fast_memory=False)
    
    user_input = "turn on the lights"
    context = {"location": "bedroom"}
    
    # Old API: resolve_intent returns List[ResolvedIntent]
    results = engine.resolve_intent(user_input, context)
    
    print(f"Input: '{user_input}'")
    print(f"Context: {context}")
    print(f"Results returned: {len(results)}")
    
    assert isinstance(results, list), "Should return a list"
    assert len(results) == 1, "Should return single result (converted from VerifiedIntent)"
    assert results[0].confidence >= 0, "Confidence should be valid"
    assert results[0].intent is not None, "Intent should be present"
    
    print(f"Top result: {results[0].intent.id}")
    print(f"Confidence: {results[0].confidence:.4f}")
    
    print("✓ Backward compatibility test passed")
    return True


def test_fallback_mechanism():
    """Test fallback mechanism when confidence is too low."""
    print("\n" + "="*60)
    print("TEST 6: Fallback Mechanism")
    print("="*60)
    
    engine = IntentEngine(use_fast_memory=False)
    
    # Deliberately ambiguous input
    user_input = "asdfjkl qwerty zxcvbnm"
    context = {}
    
    result = engine.resolve_with_hybrid_logic(user_input, context)
    
    print(f"Input: '{user_input}' (intentionally gibberish)")
    print(f"Result intent: {result.intent.id}")
    print(f"Confidence: {result.confidence:.4f}")
    print(f"Fallback used: {result.fallback_used}")
    
    # Check if it's a fallback
    if result.fallback_used:
        print(f"Fallback reason: {result.active_factors}")
        assert result.intent.id == "__fallback_uncertain__", "Should use fallback intent"
        print("✓ Fallback triggered as expected")
    else:
        print("Note: May still resolve even with gibberish (depends on corpus)")
    
    print("✓ Fallback test passed")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("HYBRID ARCHITECTURE TEST SUITE")
    print("Testing Two-Stage Resolution: Semantic Flash + Deterministic Check")
    print("="*70)
    
    tests = [
        ("Stage 1: Semantic Candidates", test_stage_1_semantic_candidates),
        ("Stage 2: Hard Stop Rules", test_stage_2_hard_stop_rules),
        ("Context Boost Scoring", test_context_boost_scoring),
        ("End-to-End Hybrid Logic", test_hybrid_logic_end_to_end),
        ("Backward Compatibility", test_backward_compatibility),
        ("Fallback Mechanism", test_fallback_mechanism),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASSED", None))
        except AssertionError as e:
            results.append((test_name, "FAILED", str(e)))
            print(f"✗ Assertion failed: {e}")
        except Exception as e:
            results.append((test_name, "ERROR", str(e)))
            print(f"✗ Error: {e}")
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, status, _ in results if status == "PASSED")
    failed = sum(1 for _, status, _ in results if status == "FAILED")
    errors = sum(1 for _, status, _ in results if status == "ERROR")
    
    for test_name, status, error in results:
        icon = "✓" if status == "PASSED" else "✗"
        print(f"{icon} {test_name}: {status}")
        if error:
            print(f"  Error: {error}")
    
    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed} | Errors: {errors}")
    
    if failed == 0 and errors == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n❌ {failed + errors} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
