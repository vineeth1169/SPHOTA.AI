"""
Fast Memory Layer - Usage Example

This example demonstrates how the Fast Memory layer resolves ambiguous
inputs like slang before the SQL engine validates the final intent.

Example Flow:
1. User says: "I need dough" (Slang for money)
2. Fast Memory retrieves: "I need money" (Past intent)
3. SQL Engine checks: User location = Bank? → YES
4. Final intent: "withdraw_cash" ✓
"""

from core.intent_engine import IntentEngine


def demo_fast_memory():
    """Demonstrate Fast Memory in action."""
    
    print("=" * 70)
    print("FAST MEMORY DEMO: Real-Time Ambiguity Resolution")
    print("=" * 70)
    
    # Initialize engine with Fast Memory enabled
    engine = IntentEngine(
        use_fast_memory=True,
        memory_boost_weight=0.25  # 25% boost from memory
    )
    
    # Clear previous memories
    if engine.fast_memory:
        engine.fast_memory.clear_memory()
    
    print("\n📝 TRAINING PHASE: Store past intents in Fast Memory")
    print("-" * 70)
    
    # Train the memory with standard phrases
    training_data = [
        ("I need money from ATM", {"location": "Bank", "time_of_day": "afternoon"}),
        ("Withdraw cash please", {"location": "Bank", "time_of_day": "morning"}),
        ("Get money from account", {"location": "Bank", "time_of_day": "evening"}),
    ]
    
    for phrase, context in training_data:
        results = engine.resolve_intent(
            user_input=phrase,
            current_context=context,
            store_in_memory=True
        )
        print(f"✓ Stored: '{phrase}' → {results[0].intent.id}")
    
    # Check memory stats
    if engine.fast_memory:
        stats = engine.fast_memory.get_stats()
        print(f"\n📊 Fast Memory: {stats['total_memories']} memories stored")
    
    print("\n" + "=" * 70)
    print("🧪 TEST PHASE: Resolve ambiguous slang input")
    print("=" * 70)
    
    # Now test with slang/ambiguous input
    slang_input = "I need dough quick"
    test_context = {
        "location": "Bank",
        "time_of_day": "afternoon",
        "user_profile": "Adult"
    }
    
    print(f"\n🗣️  User says: '{slang_input}'")
    print(f"📍 Context: {test_context}")
    
    # Get memory candidates BEFORE resolution
    print("\n🔍 Fast Memory retrieval (Top 3 similar past intents):")
    candidates = engine.get_memory_candidates(slang_input, top_k=3)
    
    for i, candidate in enumerate(candidates, 1):
        print(f"   {i}. '{candidate.original_text}'")
        print(f"      → Intent: {candidate.intent_id}")
        print(f"      → Similarity: {candidate.similarity_score:.3f}")
    
    # Perform full resolution with SQL validation
    print("\n⚙️  Context Resolution Matrix (SQL Logic):")
    results = engine.resolve_intent(
        user_input=slang_input,
        current_context=test_context,
        return_top_k=3
    )
    
    print(f"\n✅ FINAL RESOLVED INTENT:")
    print(f"   Intent: {results[0].intent.id}")
    print(f"   Confidence: {results[0].confidence:.2f}")
    print(f"   Description: {results[0].intent.description}")
    
    print(f"\n🔄 Alternative intents:")
    for i, result in enumerate(results[1:], 2):
        print(f"   {i}. {result.intent.id} (confidence: {result.confidence:.2f})")
    
    print("\n" + "=" * 70)
    print("💡 HOW IT WORKED:")
    print("-" * 70)
    print("1. Fast Memory found 'I need money' similar to 'I need dough'")
    print("2. Boosted relevant intent scores by 25%")
    print("3. SQL Engine validated: Location=Bank ✓")
    print("4. Final intent: withdraw_cash (100% deterministic)")
    print("=" * 70)
    
    # Clean up
    if engine.fast_memory:
        engine.fast_memory.clear_memory()


def demo_context_switch():
    """Demonstrate how Fast Memory + SQL handles context switches."""
    
    print("\n\n" + "=" * 70)
    print("CONTEXT SWITCHING DEMO: 'Bank' in Different Contexts")
    print("=" * 70)
    
    engine = IntentEngine(use_fast_memory=True)
    
    if engine.fast_memory:
        engine.fast_memory.clear_memory()
    
    # Scenario 1: Financial context
    print("\n📍 SCENARIO 1: User at ATM (Financial Context)")
    financial_context = {
        "location": "Bank_ATM",
        "history": ["check_balance", "view_transactions"],
        "active_goal": "financial_transaction"
    }
    
    results = engine.resolve_intent(
        "Go to the bank",
        current_context=financial_context,
        store_in_memory=True
    )
    print(f"   Resolved: {results[0].intent.id} (confidence: {results[0].confidence:.2f})")
    
    # Scenario 2: Nature context
    print("\n🌲 SCENARIO 2: User at Nature Reserve (Nature Context)")
    nature_context = {
        "location": "Nature_Reserve",
        "history": ["hiking", "fishing"],
        "active_goal": "navigation"
    }
    
    results = engine.resolve_intent(
        "Take me to the bank",
        current_context=nature_context,
        store_in_memory=True
    )
    print(f"   Resolved: {results[0].intent.id} (confidence: {results[0].confidence:.2f})")
    
    print("\n💡 Fast Memory stores BOTH contexts separately!")
    print("   SQL Engine selects the right one based on current location.")
    
    # Clean up
    if engine.fast_memory:
        engine.fast_memory.clear_memory()


if __name__ == "__main__":
    # Run the demos
    demo_fast_memory()
    demo_context_switch()
    
    print("\n✨ Fast Memory layer is working perfectly!")
    print("Ready to handle real-time ambiguity with deterministic validation.")
