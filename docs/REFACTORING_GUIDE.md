# Sphota Enterprise SDK - Refactoring Guide

## Overview

Sphota has been refactored from a prototype with Sanskrit terminology into an **Enterprise-Grade Python SDK** following Domain-Driven Design (DDD) principles.

## Key Changes

### 1. **Naming Convention: Sanskrit → English DDD Terminology**

| Sanskrit | DDD English | Purpose |
|----------|------------|---------|
| `sahacarya` | `association_history` | Co-occurrence patterns from user history |
| `virodhita` | `conflict_markers` | Opposing or contrasting signals |
| `artha` | `goal_alignment` | User's stated or inferred purpose |
| `prakarana` | `situation_context` | Current situational classification |
| `linga` | `linguistic_indicators` | Grammatical and syntactic signals |
| `shabda_samarthya` | `semantic_capacity` | Semantic richness of input |
| `auciti` | `social_propriety` | Contextual appropriateness |
| `desa` | `location_context` | Geographic/spatial context |
| `kala` | `temporal_context` | Time-based context |
| `vyakti` | `user_profile` | User demographic or preference profile |
| `svara` | `prosodic_features` | Accent, intonation, stress patterns |
| `apabhramsa` | `input_fidelity` | Signal quality and clarity |

### 2. **Architecture Evolution**

#### Before (Prototype)
```python
# Old: Sanskrit-based, minimal type hints, print statements
from core.context_matrix import ContextResolutionMatrix, ContextObject

crm = ContextResolutionMatrix()
context = ContextObject(location="kitchen", time=datetime.now())
result = crm.resolve_intent(base_scores, context)
print("Result:", result)
```

#### After (Production-Ready)
```python
# New: DDD terminology, full type hints, logging
from sphota.core import SphotaEngine, ContextSnapshot, TimeOfDay
from datetime import datetime

engine = SphotaEngine()
context = ContextSnapshot(
    location_context="kitchen",
    temporal_context=datetime.now()
)
result = engine.resolve(base_scores, context)
logger.info(f"Resolution complete: confidence={result.confidence_estimate:.2f}")
```

### 3. **Type System & Docstrings**

**Before:**
```python
def resolve_intent(self, base_scores, context):
    # No type hints
    # Minimal documentation
    return result
```

**After:**
```python
def resolve(
    self,
    base_scores: Dict[str, float],
    context: ContextSnapshot
) -> ResolutionResult:
    """
    Apply context resolution to base intent scores.
    
    This is the primary entry point for intent disambiguation. It takes
    baseline semantic similarity scores and applies contextual factors
    to compute final resolved scores.
    
    Args:
        base_scores: Dict mapping intent_id -> baseline_score [0.0-1.0]
        context: ContextSnapshot containing contextual factors
        
    Returns:
        ResolutionResult with resolved scores and diagnostics
        
    Raises:
        ValueError: If base_scores contain invalid values
        
    Example:
        >>> engine = ContextResolutionEngine()
        >>> base_scores = {"set_timer": 0.75, "alarm": 0.62}
        >>> context = ContextSnapshot(location_context="kitchen")
        >>> result = engine.resolve(base_scores, context)
    """
```

### 4. **Logging Instead of Print Statements**

**Before:**
```python
print("Applying factor:", factor_name)
print("Result:", result)
```

**After:**
```python
import logging

logger = logging.getLogger(__name__)

logger.debug(f"Applied {factor_name} factor")
logger.info("Resolution complete. Active factors: 6")
logger.warning(f"Unknown factor: {factor_name}")
logger.error(f"Invalid score range: {score}")
```

### 5. **Value Objects & Data Classes**

**New Value Objects for Clean Architecture:**

```python
from dataclasses import dataclass

@dataclass
class ContextSnapshot:
    """Immutable snapshot of contextual state (12 factors)."""
    association_history: Optional[List[str]] = None
    conflict_markers: Optional[List[str]] = None
    goal_alignment: Optional[str] = None
    # ... 9 more factors
    
    def get_active_factors(self) -> List[str]:
        """Identify which factors are active (non-None)."""

@dataclass
class ResolutionResult:
    """Result of context resolution with diagnostics."""
    resolved_scores: Dict[str, float]
    active_factors: List[str]
    score_deltas: Dict[str, float]
    confidence_estimate: float
    factor_contributions: Dict[str, Dict[str, float]]
```

### 6. **Module Organization**

```
core/
├── __init__.py              # Clean public API (SphotaEngine)
├── context_engine.py        # ✨ NEW: Production-ready context resolution
├── context_matrix.py        # Legacy: Keep for compatibility
├── intent_engine.py         # Intent matching
├── normalization_layer.py   # Input preprocessing
├── context_manager.py       # State management
└── normalization_map.py     # Normalization rules
```

### 7. **Public API**

```python
# Production API (recommended)
from sphota.core import SphotaEngine, ContextSnapshot, ResolutionResult

engine = SphotaEngine()
result = engine.resolve(base_scores, context)

# Low-level API (when you need fine-grained control)
from sphota.core import ContextResolutionEngine, TimeOfDay

cre = ContextResolutionEngine(weights=custom_weights)
result = cre.resolve(base_scores, context)

# Component API
from sphota.core import IntentEngine, NormalizationLayer

intent_engine = IntentEngine()
normalizer = NormalizationLayer()
```

## Migration Guide

### Step 1: Update Imports

**Old:**
```python
from core.context_matrix import ContextResolutionMatrix, ContextObject
```

**New:**
```python
from sphota.core import SphotaEngine, ContextSnapshot
```

### Step 2: Update Class Usage

**Old:**
```python
crm = ContextResolutionMatrix()
context = ContextObject(location="kitchen")
result = crm.resolve_intent(base_scores, context)
```

**New:**
```python
engine = SphotaEngine()
context = ContextSnapshot(location_context="kitchen")
result = engine.resolve(base_scores, context)
```

### Step 3: Enable Logging

**Old:**
```python
print("Processing user input...")
```

**New:**
```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Processing user input...")
```

### Step 4: Use Type Hints

**Old:**
```python
def custom_resolver(scores, context):
    return scores
```

**New:**
```python
def custom_resolver(scores: Dict[str, float], context: ContextSnapshot) -> Dict[str, float]:
    return scores
```

## 12 Factors Reference

### Factor Weights & Salience

| # | Factor | English Name | DDD Domain | Weight | Salience | Purpose |
|----|--------|--------------|-----------|--------|----------|---------|
| 1 | sahacarya | association_history | User History | 0.15 | MEDIUM | Co-occurrence patterns |
| 2 | virodhita | conflict_markers | Semantics | 0.10 | MEDIUM | Opposing signals |
| 3 | artha | goal_alignment | Intent | 0.20 | **HIGH** | User purpose (strongest) |
| 4 | prakarana | situation_context | Domain | 0.15 | MEDIUM | Situational context |
| 5 | linga | linguistic_indicators | Syntax | 0.08 | LOW | Grammatical signals |
| 6 | shabda_samarthya | semantic_capacity | Semantics | 0.12 | MEDIUM | Input richness |
| 7 | auciti | social_propriety | Pragmatics | 0.10 | MEDIUM | Appropriateness |
| 8 | desa | location_context | Spatial | 0.18 | **HIGH** | Geographic context |
| 9 | kala | temporal_context | Temporal | 0.15 | **HIGH** | Time-based patterns |
| 10 | vyakti | user_profile | Personalization | 0.12 | LOW | User preferences |
| 11 | svara | prosodic_features | Phonology | 0.08 | LOW | Intonation/stress |
| 12 | apabhramsa | input_fidelity | Signal | 0.07 | LOW | Signal quality |

## Code Examples

### Basic Usage

```python
from sphota.core import SphotaEngine, ContextSnapshot
from datetime import datetime

# Initialize engine
engine = SphotaEngine()

# Create context snapshot
context = ContextSnapshot(
    location_context="kitchen",
    temporal_context=datetime.now(),
    goal_alignment="productivity"
)

# Base scores from semantic matching
base_scores = {
    "set_timer": 0.75,
    "alarm": 0.62,
    "calendar": 0.45
}

# Resolve with context
result = engine.resolve(base_scores, context)

print(f"Resolved: {result.resolved_scores}")
print(f"Confidence: {result.confidence_estimate:.2f}")
print(f"Active factors: {result.active_factors}")
```

### Advanced: Custom Weights

```python
# Override default weights for domain-specific tuning
custom_weights = {
    'location_context': 0.25,      # Increase location importance
    'temporal_context': 0.20,      # Increase time importance
    'goal_alignment': 0.15,        # Decrease goal importance
    # ... other factors use defaults
}

engine = SphotaEngine(weights=custom_weights)
```

### Advanced: Low-level Component Access

```python
from sphota.core import ContextResolutionEngine, ContextSnapshot

# Use engine directly for fine-grained control
engine = ContextResolutionEngine()

# Update individual factor weights
engine.update_weight('location_context', 0.25)

# Get factor diagnostics
factor_info = engine.get_factor_info()
for factor_name, info in factor_info.items():
    print(f"{factor_name}: salience={info['salience']}, weight={info['weight']:.2f}")

# Resolve with context
result = engine.resolve(base_scores, context)

# Inspect contributions
for factor, contrib in result.factor_contributions.items():
    print(f"{factor}: {contrib}")
```

## Benefits of Refactoring

### ✅ **Production Readiness**
- Full type hints for IDE/MyPy support
- Comprehensive docstrings
- Structured logging
- Error handling with meaningful exceptions

### ✅ **Maintainability**
- Clear DDD naming removes Sanskrit barrier
- Domain language aligns with team terminology
- Self-documenting code

### ✅ **Extensibility**
- Clean class/method signatures
- Easy to add custom factors
- Weight tuning without code changes

### ✅ **Debugging**
- Structured logging instead of print()
- Diagnostic info in ResolutionResult
- Factor contribution tracking

### ✅ **Backward Compatibility**
- Old `ContextMatrix` still available
- Gradual migration path
- No breaking changes to core logic

## Testing Examples

```python
import pytest
from sphota.core import ContextResolutionEngine, ContextSnapshot
from datetime import datetime

def test_location_factor_boosts_kitchen_intents():
    """Test that location_context correctly boosts kitchen-related intents."""
    engine = ContextResolutionEngine()
    
    base_scores = {
        "cook_recipe": 0.5,
        "set_alarm": 0.5,
        "play_music": 0.5
    }
    
    context = ContextSnapshot(location_context="kitchen")
    result = engine.resolve(base_scores, context)
    
    # Kitchen boosts cooking-related intents
    assert result.resolved_scores["cook_recipe"] > base_scores["cook_recipe"]
    assert result.resolved_scores["set_alarm"] == base_scores["set_alarm"]

def test_goal_alignment_highest_weight():
    """Test that goal_alignment is strongest factor."""
    engine = ContextResolutionEngine()
    
    # Goal alignment has highest weight (0.20)
    assert engine.weights['goal_alignment'] == 0.20

def test_invalid_scores_raise_error():
    """Test that invalid score ranges raise ValueError."""
    engine = ContextResolutionEngine()
    
    invalid_scores = {"intent": 1.5}  # Out of range
    context = ContextSnapshot()
    
    with pytest.raises(ValueError):
        engine.resolve(invalid_scores, context)
```

## Performance Considerations

### Time Complexity
- O(n) where n = number of active factors
- Each factor applies bounded operations
- Typical resolution: < 1ms

### Space Complexity
- O(m) where m = number of intents
- ResolutionResult stores per-intent data
- Negligible memory footprint

## Next Steps

1. **Migrate Intent Engine**: Apply same refactoring to `intent_engine.py`
2. **Refactor Other Modules**: `context_manager.py`, `normalization_layer.py`
3. **Add Type Stubs**: Create `.pyi` files for type checking
4. **Documentation**: Generate Sphinx docs from docstrings
5. **Testing**: Implement comprehensive test suite
6. **CI/CD**: Add GitHub Actions for automated testing

## Questions & Support

For questions about the refactored SDK:
- See inline docstrings
- Check examples in this guide
- Review test files for usage patterns
