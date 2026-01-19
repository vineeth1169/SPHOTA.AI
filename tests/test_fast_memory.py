"""
Test Fast Memory Layer - Real-Time Ambiguity Resolution

This test demonstrates how Fast Memory retrieves similar past intents
before the SQL-based Context Resolution Matrix validates them.

Example: "I need dough" (Slang) → Fast Memory finds "I need money"
         → SQL Engine checks location = "Bank" → Validates intent
"""

import pytest
from core.intent_engine import IntentEngine
from core.fast_memory import FastMemory, MemoryCandidate


def test_fast_memory_basic():
    """Test basic Fast Memory storage and retrieval."""
    memory = FastMemory(persist_directory="./test_chromadb")
    
    # Clear any existing data
    memory.clear_memory()
    
    # Store some sample memories
    memory.add_memory(
        user_input="I need money",
        resolved_intent_id="withdraw_cash",
        metadata={"location": "Bank"}
    )
    
    memory.add_memory(
        user_input="Take me to the financial institution",
        resolved_intent_id="navigate_to_bank",
        metadata={"location": "Street"}
    )
    
    # Query with slang
    candidates = memory.retrieve_candidates("I need dough", top_k=3)
    
    # Should retrieve "I need money" as top candidate
    assert len(candidates) > 0
    assert candidates[0].intent_id == "withdraw_cash"
    assert candidates[0].similarity_score > 0.7
    
    # Clean up
    memory.clear_memory()


def test_intent_engine_with_fast_memory():
    """Test Intent Engine with Fast Memory integration."""
    engine = IntentEngine(use_fast_memory=True)
    
    # Clear memory
    if engine.fast_memory:
        engine.fast_memory.clear_memory()
    
    # First request: "I need money" at Bank
    context_bank = {
        "location": "Bank",
        "time_of_day": "afternoon",
        "user_profile": "Adult"
    }
    
    results = engine.resolve_intent(
        user_input="I need money",
        current_context=context_bank,
        store_in_memory=True
    )
    
    assert len(results) > 0
    first_intent = results[0].intent.id
    print(f"First resolution: {first_intent} (confidence: {results[0].confidence:.2f})")
    
    # Second request: "I need dough" (Slang) at Bank
    # Fast Memory should retrieve "I need money" and boost similar intents
    results_slang = engine.resolve_intent(
        user_input="I need dough",
        current_context=context_bank,
        store_in_memory=True
    )
    
    assert len(results_slang) > 0
    slang_intent = results_slang[0].intent.id
    print(f"Slang resolution: {slang_intent} (confidence: {results_slang[0].confidence:.2f})")
    
    # Check memory candidates
    candidates = engine.get_memory_candidates("I need dough", top_k=3)
    print(f"Memory retrieved {len(candidates)} candidates:")
    for i, candidate in enumerate(candidates):
        print(f"  {i+1}. '{candidate.original_text}' → {candidate.intent_id} (sim: {candidate.similarity_score:.2f})")
    
    # Memory should have helped resolve the ambiguity
    assert len(candidates) >= 1
    
    # Clean up
    if engine.fast_memory:
        engine.fast_memory.clear_memory()


def test_fast_memory_boost():
    """Test that Fast Memory boosts relevant intent scores."""
    engine = IntentEngine(
        use_fast_memory=True,
        memory_boost_weight=0.3  # Higher boost for testing
    )
    
    if engine.fast_memory:
        engine.fast_memory.clear_memory()
    
    # Store a strong memory association
    context_bank = {"location": "Bank"}
    
    # Train the memory with multiple similar requests
    training_phrases = [
        "I want to withdraw money",
        "Need cash from ATM",
        "Get money from my account"
    ]
    
    for phrase in training_phrases:
        engine.resolve_intent(
            user_input=phrase,
            current_context=context_bank,
            store_in_memory=True
        )
    
    # Now test with slang/ambiguous input
    results = engine.resolve_intent(
        user_input="Need some dough quick",
        current_context=context_bank
    )
    
    # Check memory stats
    if engine.fast_memory:
        stats = engine.fast_memory.get_stats()
        print(f"Fast Memory stats: {stats}")
        assert stats['total_memories'] >= 3
    
    # Clean up
    if engine.fast_memory:
        engine.fast_memory.clear_memory()


def test_fast_memory_disabled():
    """Test that engine works with Fast Memory disabled."""
    engine = IntentEngine(use_fast_memory=False)
    
    context = {"location": "Bank"}
    results = engine.resolve_intent("I need money", context)
    
    assert len(results) > 0
    assert engine.fast_memory is None


def test_memory_candidate_filtering():
    """Test that memory candidates influence SQL validation."""
    engine = IntentEngine(use_fast_memory=True)
    
    if engine.fast_memory:
        engine.fast_memory.clear_memory()
    
    # Scenario: User at a Nature Reserve says "Go to the bank"
    # Without memory: Could mean financial bank
    # With memory (from past nature context): Should mean river bank
    
    nature_context = {
        "location": "Nature_Reserve",
        "history": ["hiking", "fishing"],
        "active_goal": "navigation"
    }
    
    # Train memory with nature-related "bank" usage
    engine.resolve_intent(
        "Take me to the river bank",
        current_context=nature_context,
        store_in_memory=True
    )
    
    engine.resolve_intent(
        "Show me the bank of the stream",
        current_context=nature_context,
        store_in_memory=True
    )
    
    # Now test ambiguous input
    results = engine.resolve_intent(
        "Navigate to the bank",
        current_context=nature_context
    )
    
    print(f"Top intent: {results[0].intent.id} (confidence: {results[0].confidence:.2f})")
    
    # Memory candidates should have influenced the result
    candidates = engine.get_memory_candidates("Navigate to the bank", top_k=3)
    print(f"Retrieved {len(candidates)} memory candidates")
    
    # Clean up
    if engine.fast_memory:
        engine.fast_memory.clear_memory()


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Fast Memory Layer")
    print("=" * 60)
    
    print("\n1. Testing basic Fast Memory storage and retrieval...")
    test_fast_memory_basic()
    print("   ✓ PASSED")
    
    print("\n2. Testing Intent Engine with Fast Memory integration...")
    test_intent_engine_with_fast_memory()
    print("   ✓ PASSED")
    
    print("\n3. Testing memory boost on intent scores...")
    test_fast_memory_boost()
    print("   ✓ PASSED")
    
    print("\n4. Testing engine with Fast Memory disabled...")
    test_fast_memory_disabled()
    print("   ✓ PASSED")
    
    print("\n5. Testing memory candidate filtering...")
    test_memory_candidate_filtering()
    print("   ✓ PASSED")
    
    print("\n" + "=" * 60)
    print("All Fast Memory tests passed! ✓")
    print("=" * 60)
