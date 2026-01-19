# Hybrid Architecture Quick Reference

## Quick Start

```python
from core.intent_engine import IntentEngine

# Initialize
engine = IntentEngine()

# Resolve with hybrid logic
result = engine.resolve_with_hybrid_logic(
    user_input="play relaxing music",
    current_context={"location": "bedroom"}
)

# Check result
print(f"Intent: {result.intent.id}")
print(f"Confidence: {result.confidence}")
print(f"Stages passed: {result.stage_1_passed}, {result.stage_2_passed}")
print(f"Fallback: {result.fallback_used}")
```

## Architecture Flow

```
Input → Stage 1 (Semantic Flash) → Stage 2 (Deterministic Check) → Result
                    ↓                         ↓
            Get Top 5 via          Apply Hard Stops +
            Vector Search          Context Boost
                    ↓                         ↓
            SemanticCandidate      VerifiedIntent
```

## New Classes

### SemanticCandidate
- From Stage 1 (vector search)
- Has: `candidate_intent`, `semantic_similarity`, `source`

### VerifiedIntent
- Final result with tracking
- Has: `intent`, `semantic_candidates`, `stage_1_passed`, `stage_2_passed`, `fallback_used`, `confidence`, `context_adjusted_score`, `active_factors`

## New Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `_get_semantic_candidates()` | Stage 1: Find Top 5 via vector | `List[SemanticCandidate]` |
| `_apply_deterministic_check()` | Stage 2: Validate + Boost | `(VerifiedIntent, bool)` |
| `resolve_with_hybrid_logic()` | Full two-stage process | `VerifiedIntent` |
| `_create_fallback_intent()` | Create uncertain response | `VerifiedIntent` |

## Hard Stop Rules

1. **Conflict Check** - Discard if context conflict contradicts intent
2. **Location Mismatch** - Discard if required location doesn't match
3. **User Profile** - Discard if profile requirements not met

## Context Boosts

| Factor | Boost | Example |
|--------|-------|---------|
| Purpose match | +0.20 | Purpose="productivity" + meeting intent |
| Situation match | +0.15 | Situation="evening" + relaxation intent |
| Location match | +0.09 | Location="kitchen" + cooking intent |
| History match | +0.15 | History=["music"] + volume intent |

## Confidence Levels

- **0.9+**: Very confident
- **0.7-0.9**: Confident
- **0.5-0.7**: Moderate
- **<0.5**: Triggers fallback

## Fallback Trigger

When confidence < 0.6:
```python
result.fallback_used = True
result.intent.id = "__fallback_uncertain__"
result.intent.pure_text = "I'm not certain. Please rephrase."
```

## Backward Compatibility

Old API still works:
```python
results = engine.resolve_intent("set a timer")  # Returns List[ResolvedIntent]
```

## Testing

Run tests:
```bash
python tests/test_hybrid_quick.py          # Quick validation
python tests/test_hybrid_architecture.py  # Full suite
```

## File Locations

| File | Purpose |
|------|---------|
| `core/intent_engine.py` | Main implementation |
| `docs/HYBRID_ARCHITECTURE.md` | Complete guide |
| `docs/HYBRID_IMPLEMENTATION_SUMMARY.md` | This implementation |
| `tests/test_hybrid_*.py` | Test suites |

## Example Scenarios

### Scenario 1: Clear Intent with Context
```
Input: "play relaxing music"
Context: {"location": "bedroom", "time": "evening"}

Stage 1: music_play (0.88) → music_relaxation (0.81) → ...
Stage 2: music_relaxation passes all checks
         Boost: location (bedroom) → +0.09
         Result: 0.81 + 0.09 = 0.90
         
Output: VerifiedIntent(intent=music_relaxation, confidence=0.90)
```

### Scenario 2: Ambiguous Intent
```
Input: "I need dough"
Context: {"location": "Bank"}

Stage 1: need_money (0.87) → dough_recipe (0.74) → ...
Stage 2: need_money passes all checks
         Boost: location (Bank) → +0.18
         Result: 0.87 + 0.18 = 0.95
         dough_recipe fails (not relevant in Bank)

Output: VerifiedIntent(intent=need_money, confidence=0.95)
```

### Scenario 3: Conflicting Intent
```
Input: "cancel the timer"
Context: {"conflict": ["cancel"]}

Stage 1: timer_stop (0.80) → timer_start (0.75) → ...
Stage 2: timer_stop passes all checks
         timer_start HARD STOP: Conflict with "cancel"
         
Output: VerifiedIntent(intent=timer_stop, confidence=0.80)
```

### Scenario 4: Low Confidence
```
Input: "asdfjkl qwerty"
Context: {}

Stage 1: No candidates with similarity > 0.5
Stage 2: All candidates fail or have < 0.6 confidence

Output: VerifiedIntent(
    intent=__fallback_uncertain__,
    confidence=0.0,
    fallback_used=True
)
```

## Performance

- **Typical E2E time:** ~20ms
- **Stage 1:** ~15ms (encode + query)
- **Stage 2:** ~5ms (validate + boost)
- **Memory:** ~100MB (model + corpus + cache)

## Configuration

```python
engine = IntentEngine(
    intents_path="data/intents.json",      # Corpus
    model_name="all-MiniLM-L6-v2",         # SBERT model
    use_normalization=True,                # Input cleaning
    use_fast_memory=True,                  # Vector cache
    memory_boost_weight=0.2                # Memory influence
)
```

## Debugging

Access all stage details:
```python
result = engine.resolve_with_hybrid_logic(user_input, context)

# Stage 1 results
for candidate in result.semantic_candidates:
    print(f"{candidate.candidate_intent.id}: {candidate.semantic_similarity:.2f}")

# Stage 2 results
print(f"Passed validation: {result.stage_2_passed}")
print(f"Active factors: {result.active_factors}")

# Final result
print(f"Final intent: {result.intent.id}")
print(f"Final confidence: {result.confidence:.2f}")
print(f"Fallback used: {result.fallback_used}")
```

## Common Issues

**Issue:** Low confidence on valid input
- **Cause:** Corpus doesn't have good match
- **Solution:** Add examples to intents.json

**Issue:** Wrong intent selected
- **Cause:** Context boost too aggressive
- **Solution:** Adjust CRM weights in context_matrix.py

**Issue:** Fallback triggered too often
- **Cause:** Threshold too high (0.6)
- **Solution:** Lower threshold in resolve_with_hybrid_logic()

**Issue:** No memory boost found
- **Cause:** First time seeing input
- **Solution:** Normal - vector search still works

---

**Version:** 1.0  
**Status:** Production Ready  
**Last Updated:** 2024
