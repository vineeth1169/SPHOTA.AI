# Sphota AI Test Suite

## Overview

Comprehensive unit tests for the Sphota Voice AI engine using **pytest** framework.

## Test Coverage

### 1. **Test Context Weighting (The "Bank" Test)**
   - **File**: `tests/test_sphota.py::TestContextWeighting`
   - **Purpose**: Verify that the Context Resolution Matrix correctly disambiguates polysemic words
   - **Test Cases**:
     - `test_bank_financial_context`: "bank" → financial_bank (city + money context)
     - `test_bank_nature_context`: "bank" → river_bank (nature + fishing context)
     - `test_context_flips_outcome`: Proves context changes winner
   - **Key Assertion**: Same input, different context = different winners

### 2. **Test Apabhraṃśa (The Slang Test)**
   - **File**: `tests/test_sphota.py::TestApabhramsa`
   - **Purpose**: Verify slang normalization and distortion scoring
   - **Test Cases**:
     - `test_slang_normalization`: "No cap" → "no lie"/"truthfully"
     - `test_multiple_slang_terms`: Multiple slang in one sentence
     - `test_clean_input_unchanged`: Clean input passes through
     - `test_apabhramsa_affects_confidence`: Slang reduces confidence
   - **Key Assertion**: Slang is bridged to semantic meaning, not treated as error

### 3. **Test 12-Factor Schema**
   - **File**: `tests/test_sphota.py::TestTwelveFactorSchema`
   - **Purpose**: Validate Context Resolution Matrix structure
   - **Test Cases**:
     - `test_all_factors_present`: All 12 Sanskrit factors exist
     - `test_factor_count`: Exactly 12 factors (no more, no less)
     - `test_weight_ranges`: Weights in valid ranges
     - `test_artha_highest_weight`: Artha (Purpose) has highest weight
     - `test_factor_mappings_initialized`: Keyword mappings exist
     - `test_active_factors_detection`: Correctly identifies set factors
   - **Key Assertion**: All 12 factors properly initialized with valid weights

### 4. **Test Zero-Context Fallback**
   - **File**: `tests/test_sphota.py::TestZeroContextFallback`
   - **Purpose**: Verify graceful degradation with missing context
   - **Test Cases**:
     - `test_empty_context_object`: Empty context doesn't crash
     - `test_none_context`: None context handled gracefully
     - `test_highest_raw_probability_wins`: Falls back to raw similarity
     - `test_graceful_degradation`: CRM returns unchanged scores
   - **Key Assertion**: System never crashes, always returns valid results

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify pytest is installed
pytest --version
```

## Running Tests

### Run All Tests
```bash
# Using pytest directly
pytest tests/test_sphota.py -v

# Using helper script
python run_tests.py
```

### Run Specific Test Classes
```bash
# Bank polysemic tests only
pytest tests/test_sphota.py::TestContextWeighting -v

# Slang tests only
pytest tests/test_sphota.py::TestApabhramsa -v

# 12-Factor schema tests only
pytest tests/test_sphota.py::TestTwelveFactorSchema -v

# Zero-context fallback tests only
pytest tests/test_sphota.py::TestZeroContextFallback -v
```

### Run Specific Test Methods
```bash
# Run just the financial bank test
pytest tests/test_sphota.py::TestContextWeighting::test_bank_financial_context -v

# Run just the slang normalization test
pytest tests/test_sphota.py::TestApabhramsa::test_slang_normalization -v
```

### Filter by Keyword
```bash
# Run all tests with "bank" in the name
pytest tests/test_sphota.py -k bank -v

# Run all tests with "slang" in the name
pytest tests/test_sphota.py -k slang -v
```

### Show Test Markers
```bash
pytest tests/test_sphota.py --markers
```

## Test Architecture

### Mocking Strategy
- **SentenceTransformer**: Mocked to avoid loading heavy models (~100MB)
- **Embeddings**: Deterministic fake vectors based on text hash
- **Benefits**: Fast tests (~1-2s instead of ~30s), no network calls

### Fixtures
- `mock_sentence_transformer`: Provides fake SBERT model
- `pasyanti_engine`: Initialized engine with mocked model
- `context_matrix`: Clean CRM instance
- `apabhramsa_layer`: Clean normalization layer

### Test Organization
```
tests/
├── __init__.py
└── test_sphota.py
    ├── TestContextWeighting       # Polysemic resolution
    ├── TestApabhramsa             # Slang normalization
    ├── TestTwelveFactorSchema     # CRM structure validation
    ├── TestZeroContextFallback    # Graceful degradation
    ├── TestIntegration            # Full pipeline tests
    └── TestPerformance            # Edge cases & performance
```

## Expected Output

### Successful Test Run
```
tests/test_sphota.py::TestContextWeighting::test_bank_financial_context PASSED
tests/test_sphota.py::TestContextWeighting::test_bank_nature_context PASSED
tests/test_sphota.py::TestContextWeighting::test_context_flips_outcome PASSED
tests/test_sphota.py::TestApabhramsa::test_slang_normalization PASSED
tests/test_sphota.py::TestApabhramsa::test_multiple_slang_terms PASSED
tests/test_sphota.py::TestApabhramsa::test_clean_input_unchanged PASSED
tests/test_sphota.py::TestApabhramsa::test_apabhramsa_affects_confidence PASSED
tests/test_sphota.py::TestTwelveFactorSchema::test_all_factors_present PASSED
tests/test_sphota.py::TestTwelveFactorSchema::test_factor_count PASSED
tests/test_sphota.py::TestTwelveFactorSchema::test_weight_ranges PASSED
tests/test_sphota.py::TestTwelveFactorSchema::test_artha_highest_weight PASSED
tests/test_sphota.py::TestTwelveFactorSchema::test_factor_mappings_initialized PASSED
tests/test_sphota.py::TestTwelveFactorSchema::test_active_factors_detection PASSED
tests/test_sphota.py::TestZeroContextFallback::test_empty_context_object PASSED
tests/test_sphota.py::TestZeroContextFallback::test_none_context PASSED
tests/test_sphota.py::TestZeroContextFallback::test_highest_raw_probability_wins PASSED
tests/test_sphota.py::TestZeroContextFallback::test_graceful_degradation PASSED

========================== 21 passed in 2.34s ==========================
```

## Debugging Failed Tests

### View Detailed Output
```bash
# Show print statements
pytest tests/test_sphota.py -v -s

# Show full traceback
pytest tests/test_sphota.py -v --tb=long

# Stop at first failure
pytest tests/test_sphota.py -v -x
```

### Common Issues

1. **Import Errors**: Ensure all dependencies installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Path Issues**: Run from project root
   ```bash
   cd c:\Users\vinee\Sphota.AI
   pytest tests/test_sphota.py
   ```

3. **Model Not Found**: Tests use mocked models, should not download anything
   - If real model is being used, check fixture patching

## Continuous Integration

To add to CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=core
```

## Philosophy Behind Tests

Following Bhartṛhari's principle of **Akhaṇḍapakṣa** (Sentence Holism):

1. **Context Changes Meaning**: The "Bank" test proves meaning emerges from totality of context
2. **Distortion ≠ Error**: Apabhraṃśa tests show slang is a bridge to meaning, not noise
3. **Twelve Factors**: Schema tests validate all 12 Sanskrit linguistic determinants
4. **Graceful Degradation**: Zero-context tests ensure system never fails catastrophically

## Contributing Tests

When adding new tests:

1. **Follow naming convention**: `test_<what>_<scenario>`
2. **Use descriptive assertions**: Include failure messages
3. **Mock heavy dependencies**: Keep tests fast
4. **Test both positive and negative cases**
5. **Add docstrings**: Explain what the test validates

Example:
```python
def test_new_feature_success_case(self, pasyanti_engine):
    """
    Test: New feature works correctly under normal conditions.
    
    Expected: Feature returns expected output without errors.
    """
    # Arrange
    input_data = "test input"
    
    # Act
    result = pasyanti_engine.process(input_data)
    
    # Assert
    assert result is not None, "Should return valid result"
    assert result.score > 0.5, "Score should be above threshold"
```

## Resources

- **Pytest Docs**: https://docs.pytest.org/
- **Mocking Guide**: https://docs.python.org/3/library/unittest.mock.html
- **Project Structure**: See [core/context_matrix.py](core/context_matrix.py) for implementation details

---

**Vākyasphoṭa through Testing**: Every test is a flash of insight into system behavior.
