# Hybrid Architecture: Two-Stage Resolution Process

## Overview

The Hybrid Architecture implements a **two-stage resolution process** that combines semantic vector search with deterministic context validation. This produces more accurate intent recognition in real-world scenarios where ambiguity is common.

## Architecture

```
User Input
    ↓
[STAGE 1: Semantic Flash]
    • Encode input to semantic vector
    • Query vector DB (ChromaDB) for Top 5 similar intents
    • Return SemanticCandidate objects with similarity scores
    ↓
[STAGE 2: Deterministic Check]
    • Apply Hard Stop Rules (discard invalid candidates)
    • Apply Context Boost (amplify valid candidates)
    • Return VerifiedIntent with stage tracking
    ↓
[FALLBACK MECHANISM]
    • If confidence < 0.6 → return FallbackIntent
    • User receives "I'm not certain, please rephrase" message
```

## Key Components

### 1. SemanticCandidate (Stage 1 Output)

Represents a candidate intent found through vector similarity search.

```python
@dataclass
class SemanticCandidate:
    candidate_intent: Intent          # The potential match
    semantic_similarity: float        # Cosine similarity [0, 1]
    source: str                       # "vector_search" or "memory_boost"
```

**Purpose:** Captures the top semantic matches before context validation.

### 2. VerifiedIntent (Final Result)

The resolved intent after both stages of processing, with stage tracking.

```python
@dataclass
class VerifiedIntent:
    intent: Intent                    # Final selected intent
    semantic_candidates: List[SemanticCandidate]  # Candidates from Stage 1
    stage_1_passed: bool              # Did vector search succeed?
    stage_2_passed: bool              # Did context validation pass?
    fallback_used: bool               # Was fallback triggered?
    confidence: float                 # Final confidence [0, 1]
    context_adjusted_score: float     # Score after context boost
    active_factors: List[str]         # Context factors that helped
```

### 3. Stage 1: Semantic Flash

**Method:** `_get_semantic_candidates(user_input, input_embedding) -> List[SemanticCandidate]`

**Process:**
1. Encode user input to semantic vector using SBERT (`all-MiniLM-L6-v2`)
2. Query Fast Memory for top candidates (previously encountered similar intents)
3. Calculate cosine similarity to all intents in corpus
4. Return top 5 candidates sorted by similarity

**Output:** Ordered list of `SemanticCandidate` objects

**Example:**
```
Input: "I need dough"

Candidates (Stage 1):
1. "I need money" (sim: 0.87, source: memory_boost)
2. "I need bread" (sim: 0.74, source: vector_search)
3. "I need cash" (sim: 0.71, source: vector_search)
4. "I need baking supplies" (sim: 0.62, source: vector_search)
5. "I need help" (sim: 0.58, source: vector_search)
```

### 4. Stage 2: Deterministic Check

**Method:** `_apply_deterministic_check(candidates, context, distortion) -> (VerifiedIntent, bool)`

**Hard Stop Rules** (discard candidate if):

1. **Conflict Check**
   - If context has conflict marker (e.g., "cancel", "stop")
   - Discard intents that contradict (e.g., "create", "start")
   ```
   Scenario: User says "cancel the timer" → "start_timer" intent is discarded
   ```

2. **Location Mismatch**
   - If intent requires specific location
   - Discard if current location doesn't match
   ```
   Scenario: Intent requires "kitchen", user is in "bedroom" → discarded
   ```

3. **User Profile Incompatibility**
   - If intent has user profile requirements
   - Discard if user profile doesn't match

**Context Boost** (amplify scores for valid candidates):

1. **Purpose Alignment** (+0.20)
   - If context purpose matches intent's required purpose
   ```
   Scenario: Purpose="productivity" + "schedule_meeting" intent → +0.20
   ```

2. **Situational Relevance** (+0.15)
   - If context situation matches intent's situation
   ```
   Scenario: Situation="morning_routine" + "set_alarm" intent → +0.15
   ```

3. **Location Bonus** (+0.09)
   - If current location matches intent's helpful location
   ```
   Scenario: Location="kitchen" + "recipe_search" intent → +0.09
   ```

4. **Historical Patterns** (+0.15)
   - If user history matches intent's associated intents
   ```
   Scenario: History=["music_player"] + "increase_volume" intent → +0.15
   ```

**Output:** `(VerifiedIntent, stage_2_passed: bool)`

**Example (Continuing):**
```
Context: {"location": "Bank", "purpose": "finance"}

After Hard Stops:
- "I need money" (PASS - no conflicts)
- "I need bread" (PASS - no conflicts)
- "I need baking supplies" (PASS)

After Context Boost:
- "I need money" → 0.87 + 0.18 (location) = 0.95 ✓
- "I need bread" → 0.74 (no boosts)
- "I need baking supplies" → 0.62 (no boosts)

Selected: "I need money" (confidence: 0.95)
```

### 5. Hybrid Logic Orchestration

**Method:** `resolve_with_hybrid_logic(user_input, context) -> VerifiedIntent`

**Flow:**
1. Encode user input to semantic vector
2. Stage 1: Get top 5 semantic candidates
3. Stage 2: Validate with Hard Stop rules + context boost
4. If confidence < 0.6 OR Stage 2 failed → Fallback
5. Return `VerifiedIntent` with stage tracking

### 6. Fallback Mechanism

**Method:** `_create_fallback_intent(user_input, reason, confidence) -> VerifiedIntent`

**When Triggered:**
- No semantic candidates found (Stage 1 failed)
- No candidates pass Hard Stop rules (Stage 2 failed)
- Best confidence < 0.6 (too uncertain)

**Fallback Intent:**
```
Intent ID: "__fallback_uncertain__"
Message: "I'm not certain about your intent. Please rephrase."
```

**Advantages:**
- Better UX than wrong intent selection
- User can provide clarification
- Avoids costly mistakes (e.g., "cancel" acting on wrong intent)

## Integration with Existing Components

### Context Resolution Matrix (CRM)

The CRM already implements 12 contextual factors:
- History (Association)
- Conflict (Opposition)
- Purpose (Goal)
- Situation (Context)
- Indicator (Signs)
- Word Power (Capacity)
- Propriety (Fitness)
- Location (Place)
- Time (Temporal)
- User Profile (Individualization)
- Intonation (Prosody)
- Distortion (Slang)

**Hybrid Architecture uses:**
- CRM's Hard Stop detection (conflict, location)
- CRM's weights for context boost calculations
- CRM's `get_active_factors()` for result explanation

### Fast Memory Layer

Vector database (ChromaDB with numpy fallback) stores:
- Past user inputs
- Associated intent IDs
- Confidence scores
- Contextual metadata

**Stage 1 uses:**
- `retrieve_candidates()` for memory-boosted candidates
- Similarity scores as confidence values

## Usage Examples

### Basic Usage (No Context)

```python
from core.intent_engine import IntentEngine

engine = IntentEngine()

result = engine.resolve_with_hybrid_logic(
    user_input="play my favorite song"
)

print(f"Intent: {result.intent.id}")
print(f"Confidence: {result.confidence}")
print(f"Fallback used: {result.fallback_used}")
```

### With Context

```python
context = {
    "location": "bedroom",
    "purpose": "relaxation",
    "time": "evening",
    "history": ["music_playing"]
}

result = engine.resolve_with_hybrid_logic(
    user_input="play something relaxing",
    current_context=context
)
```

### Accessing Stage Details

```python
result = engine.resolve_with_hybrid_logic(user_input, context)

# Stage tracking
if result.stage_1_passed:
    print(f"Found {len(result.semantic_candidates)} candidates")
    
if result.stage_2_passed:
    print(f"Passed Hard Stop rules: {result.active_factors}")
    
if result.fallback_used:
    print(f"Fallback triggered: {result.active_factors[0]}")
```

### Backward Compatibility

```python
# Old API still works (returns List[ResolvedIntent])
results = engine.resolve_intent(
    user_input="set a timer",
    current_context={"location": "kitchen"}
)

# Internally uses hybrid logic, but wrapped for compatibility
print(results[0].intent.id)
print(results[0].confidence)
```

## Testing

### Stage 1 Testing

Test that vector search returns candidates:
```python
candidates = engine._get_semantic_candidates(user_input, embedding)
assert len(candidates) > 0
assert all(0 <= c.semantic_similarity <= 1 for c in candidates)
```

### Stage 2 Testing

Test that Hard Stop rules work:
```python
context = {"conflict": ["cancel"]}
verified, passed = engine._apply_deterministic_check(
    candidates, context, 0.0
)
assert verified.intent.id != "start_timer"  # Should be discarded
```

### End-to-End Testing

```python
result = engine.resolve_with_hybrid_logic("I need help", {"location": "kitchen"})
assert result.confidence >= 0 and result.confidence <= 1
assert hasattr(result, 'stage_1_passed')
assert hasattr(result, 'stage_2_passed')
```

## Performance Characteristics

| Stage | Operation | Time | Notes |
|-------|-----------|------|-------|
| **Stage 1** | Encode input | ~5ms | Using SBERT |
| **Stage 1** | Query Top 5 | ~10ms | ChromaDB indexed search |
| **Stage 2** | Hard Stop check | ~2ms | Rule-based validation |
| **Stage 2** | Context boost | ~3ms | CRM calculation |
| **Total** | End-to-end | ~20ms | Fast enough for real-time |

## Confidence Interpretation

- **0.9+** : Very confident (e.g., exact match boosted by context)
- **0.7-0.9** : Confident (e.g., good vector match + some context boost)
- **0.5-0.7** : Moderate (e.g., semantic match with weak context)
- **<0.5** : Low (triggers fallback or ambiguous)

## Terminology

All English, no Sanskrit in user-facing code:
- "Semantic Candidate" (vector search result)
- "Verified Intent" (final result after validation)
- "Hard Stop Rule" (mandatory constraint)
- "Context Boost" (optional score amplification)
- "Fallback Intent" (uncertainty response)

## Future Enhancements

1. **Machine Learning Hard Stops**
   - Learn new Hard Stop patterns from user corrections

2. **Dynamic Weight Adjustment**
   - Adjust CRM weights based on accuracy feedback

3. **Confidence Calibration**
   - Calibrate thresholds based on corpus characteristics

4. **Intent Clustering**
   - Group similar intents to improve matching

5. **Multi-language Support**
   - Extend to non-English inputs with proper encoding

## References

- **Context Resolution Matrix:** `core/context_matrix.py`
- **Fast Memory:** `core/fast_memory.py` and `core/fast_memory_simple.py`
- **Intent Corpus:** `data/intents.json`
- **Tests:** `tests/test_hybrid_architecture.py`

---

**Version:** 1.0  
**Last Updated:** 2024  
**Status:** Complete and tested
