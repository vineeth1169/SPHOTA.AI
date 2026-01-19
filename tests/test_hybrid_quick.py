#!/usr/bin/env python3
"""
Quick validation test for Hybrid Architecture
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("Testing Hybrid Architecture Implementation...")
    print("=" * 60)
    
    # Test 1: Import classes
    print("\n1. Testing imports...")
    try:
        from core.intent_engine import (
            IntentEngine,
            SemanticCandidate,
            VerifiedIntent,
            Intent,
        )
        print("   ✓ All classes imported successfully")
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        return False
    
    # Test 2: Initialize engine
    print("\n2. Initializing engine...")
    try:
        engine = IntentEngine(use_fast_memory=False)
        print(f"   ✓ Engine initialized with {len(engine.intents)} intents")
    except Exception as e:
        print(f"   ✗ Initialization failed: {e}")
        return False
    
    # Test 3: Stage 1 - Semantic Candidates
    print("\n3. Testing Stage 1 (Semantic Flash)...")
    try:
        user_input = "play music"
        embedding = engine.model.encode(
            user_input,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        candidates = engine._get_semantic_candidates(user_input, embedding)
        print(f"   ✓ Stage 1 returned {len(candidates)} candidates")
        
        if candidates:
            print(f"     Top candidate: {candidates[0].candidate_intent.id}")
            print(f"     Similarity: {candidates[0].semantic_similarity:.4f}")
    except Exception as e:
        print(f"   ✗ Stage 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Stage 2 - Deterministic Check
    print("\n4. Testing Stage 2 (Deterministic Check)...")
    try:
        context = {"location": "living_room"}
        verified, stage_2_passed = engine._apply_deterministic_check(
            semantic_candidates=candidates,
            current_context=context,
            distortion_score=0.0
        )
        print(f"   ✓ Stage 2 completed")
        if verified:
            print(f"     Selected: {verified.intent.id}")
            print(f"     Confidence: {verified.confidence:.4f}")
            print(f"     Stage 2 passed: {stage_2_passed}")
        else:
            print("     No intent selected (would trigger fallback)")
    except Exception as e:
        print(f"   ✗ Stage 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Hybrid Logic (Full End-to-End)
    print("\n5. Testing Hybrid Logic (End-to-End)...")
    try:
        result = engine.resolve_with_hybrid_logic(
            user_input="set a reminder",
            current_context={"purpose": "productivity"}
        )
        print(f"   ✓ Hybrid logic returned VerifiedIntent")
        print(f"     Intent: {result.intent.id}")
        print(f"     Confidence: {result.confidence:.4f}")
        print(f"     Stage 1 passed: {result.stage_1_passed}")
        print(f"     Stage 2 passed: {result.stage_2_passed}")
        print(f"     Fallback used: {result.fallback_used}")
    except Exception as e:
        print(f"   ✗ Hybrid logic failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Backward Compatibility
    print("\n6. Testing Backward Compatibility...")
    try:
        results = engine.resolve_intent(
            user_input="turn on lights",
            current_context={"location": "bedroom"}
        )
        print(f"   ✓ resolve_intent returned {len(results)} result(s)")
        if results:
            print(f"     Intent: {results[0].intent.id}")
            print(f"     Confidence: {results[0].confidence:.4f}")
    except Exception as e:
        print(f"   ✗ Backward compatibility failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 7: Fallback Mechanism
    print("\n7. Testing Fallback Mechanism...")
    try:
        result = engine.resolve_with_hybrid_logic(
            user_input="asdfjkl qwerty zxcvbnm",
            current_context={}
        )
        print(f"   ✓ Fallback test completed")
        print(f"     Intent: {result.intent.id}")
        print(f"     Fallback used: {result.fallback_used}")
        if result.fallback_used:
            print(f"     Reason: {result.active_factors}")
    except Exception as e:
        print(f"   ✗ Fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✓ All validation tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
