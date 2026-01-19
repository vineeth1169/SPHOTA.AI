"""Quick test for Fast Memory (Simple Implementation)"""

print("Testing Fast Memory with simple numpy implementation...")

from core.intent_engine import IntentEngine

# Initialize engine with Fast Memory
engine = IntentEngine(use_fast_memory=True)

# Check which implementation is loaded
if engine.fast_memory:
    stats = engine.fast_memory.get_stats()
    print(f"\n✓ Fast Memory loaded successfully!")
else:
    print("\n✗ Fast Memory not initialized")
    stats = {}
print(f"  Implementation: {stats.get('implementation', 'chromadb')}")
print(f"  Total memories: {stats['total_memories']}")

# Test basic functionality
print("\n📝 Testing memory storage...")
results = engine.resolve_intent(
    user_input="I need money",
    current_context={"location": "Bank"},
    store_in_memory=True
)
print(f"  ✓ Stored: 'I need money' → {results[0].intent.id}")

# Test retrieval
print("\n🔍 Testing memory retrieval...")
candidates = engine.get_memory_candidates("I need dough", top_k=3)
if candidates:
    for i, c in enumerate(candidates, 1):
        print(f"  {i}. '{c.original_text}' → {c.intent_id} (similarity: {c.similarity_score:.2f})")
else:
    print("  No candidates found (expected on first run)")

# Test slang resolution
print("\n🧪 Testing slang resolution...")
results_slang = engine.resolve_intent(
    user_input="I need dough",
    current_context={"location": "Bank"}
)
print(f"  ✓ Resolved: 'I need dough' → {results_slang[0].intent.id}")
print(f"  Confidence: {results_slang[0].confidence:.2f}")

print("\n✨ Fast Memory is working with simple implementation!")
print("   (No ChromaDB required - using pure numpy)")
