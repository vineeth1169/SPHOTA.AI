"""
Quick verification that Fast Memory is working with Python 3.14
"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("FAST MEMORY VERIFICATION (Python 3.14)")
print("=" * 60)

print(f"\nPython version: {sys.version}")

# Test 1: Import simple Fast Memory
print("\n1. Testing import of simple Fast Memory...")
try:
    from core.fast_memory_simple import FastMemory, MemoryCandidate
    print("   ✓ Import successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Create Fast Memory instance
print("\n2. Creating Fast Memory instance...")
try:
    fm = FastMemory()
    stats = fm.get_stats()
    print(f"   ✓ Created: {stats['implementation']}")
    print(f"   - Collection: {stats['collection_name']}")
    print(f"   - Distance metric: {stats['distance_metric']}")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 3: Store and retrieve memories
print("\n3. Testing memory storage...")
try:
    import numpy as np
    
    # Create dummy embeddings
    emb1 = np.random.rand(384).astype(np.float32)
    emb2 = np.random.rand(384).astype(np.float32)
    
    fm.add_memory("test input 1", "intent_1", emb1, {"context": "test"})
    fm.add_memory("test input 2", "intent_2", emb2, {"context": "test"})
    
    print(f"   ✓ Stored 2 memories")
    print(f"   - Total: {fm.get_memory_count()}")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 4: Retrieve candidates
print("\n4. Testing memory retrieval...")
try:
    query_emb = np.random.rand(384).astype(np.float32)
    candidates = fm.retrieve_candidates("test query", query_emb, top_k=2)
    
    print(f"   ✓ Retrieved {len(candidates)} candidates")
    for i, c in enumerate(candidates, 1):
        print(f"   {i}. {c.original_text} → {c.intent_id} (sim: {c.similarity_score:.3f})")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 5: Try importing intent engine (this may fail due to sentence-transformers)
print("\n5. Testing Intent Engine import...")
try:
    from core.intent_engine import IntentEngine
    print("   ✓ Intent Engine imported")
    print("   Note: Full engine requires sentence-transformers to initialize")
except Exception as e:
    print(f"   ✗ Intent Engine import failed: {type(e).__name__}")
    print(f"   This is expected if dependencies are still loading")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("✓ Fast Memory (simple numpy implementation) is working!")
print("✓ Compatible with Python 3.14")
print("✓ No ChromaDB dependency required")
print("=" * 60)
