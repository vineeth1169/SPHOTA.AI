# Sphota FastAPI Swagger UI Polish Guide

## Overview

The FastAPI Swagger UI (`/docs`) has been refactored with **professional Enterprise Product metadata** to create a rich, self-documenting API that looks production-ready.

**Files Refactored:**
- `main.py` (823 lines) - FastAPI application with enhanced OpenAPI metadata
- `models.py` (447 lines) - New models module with rich Pydantic schema examples

---

## What Changed

### 1. **New Models Module** (`models.py`)

Extracted all Pydantic models into a separate, well-documented module with rich metadata:

**Models Included:**
- `ContextModel` - 12-factor context snapshot with detailed descriptions
- `IntentRequest` - User input + context wrapper with examples
- `ResolutionFactor` - Individual factor contribution
- `IntentResponse` - Full resolution result with audit trail
- `HealthResponse` - System health status

Each model includes:
- ✅ **Rich docstrings** - Business context and use cases
- ✅ **Field descriptions** - What each field does
- ✅ **Field examples** - Sample values for each field
- ✅ **json_schema_extra** - Multiple example payloads
- ✅ **Pydantic v2 model_config** - JSON schema customization

---

## FastAPI App Metadata

### Previous (Basic)
```python
app = FastAPI(
    title="Sphota Intent Engine",
    description="Deterministic Intent Resolution Microservice - Production-Grade REST API",
    version="2.0.0",
)
```

### Now (Enterprise Grade)
```python
app = FastAPI(
    title="Sphota Deterministic Context Engine",
    description="""
A **12-Factor NLU Middleware** for Enterprise-Grade Intent Resolution

Resolves ambiguous user input to specific intents using **Time**, **Location**, and **User History**.
Optimized for Banking & Automotive industries with deterministic, fully-auditable results.

### Key Features
- **Deterministic Resolution**: Same input + context = Identical output
- **Sub-5ms Latency**: <5ms P99 inference time
- **Explainable AI**: 12-factor contribution audit trail
- **Enterprise-Ready**: Full compliance audit trails, zero randomness

### The 12 Context Factors
1. association_history
2. conflict_markers
3. goal_alignment
4. situation_context
5. linguistic_indicators
6. semantic_capacity
7. social_propriety
8. location_context
9. temporal_context
10. user_profile
11. prosodic_features
12. input_fidelity
""",
    version="1.0.0-beta",
    contact={
        "name": "Sphota Development Team",
        "url": "https://github.com/vineeth1169/SPHOTA.AI",
        "email": "support@sphota.ai",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/vineeth1169/SPHOTA.AI/blob/main/LICENSE",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Local development"},
        {"url": "https://api.sphota.ai", "description": "Production server"},
    ],
    tags=[
        {
            "name": "Intent Resolution",
            "description": "Core operations - The primary API for user input interpretation"
        },
        {
            "name": "System",
            "description": "Health, status, and metadata endpoints"
        }
    ]
)
```

---

## `/resolve-intent` Endpoint Documentation

### Enhanced Endpoint Decorator

```python
@app.post(
    "/resolve-intent",
    response_model=IntentResponse,
    status_code=status.HTTP_200_OK,
    tags=["Intent Resolution"],
    summary="Resolve User Intent (12-Factor Context Engine)",
    description="""
**Deterministically resolve ambiguous user input to specific intents** using the 12-Factor Context Resolution Engine.

This endpoint accepts raw user input and optional contextual factors, then returns:
1. **Resolved Intent** - Top-ranked interpretation with confidence score
2. **Contributing Factors** - Which of the 12 factors influenced the decision
3. **Alternative Intents** - Runner-up interpretations for edge case detection
4. **Audit Trail** - Full decision history for compliance/debugging
5. **Performance Metrics** - Inference latency (target: <5ms)

### Input Schema

The `context` object requires **strict English keys** (not Sanskrit terminology):

- `location_context`: GPS, branch code, or physical location
- `temporal_context`: ISO 8601 timestamp (e.g., "2026-01-17T14:30:00Z")
- `user_profile`: User role/demographic (e.g., "analyst", "commuter")
- `association_history`: List of past intents
- `goal_alignment`: User's primary objective
- `semantic_capacity`: Input richness [0.0-1.0]
- `social_propriety`: Appropriateness in context [-1.0 to 1.0]
- `linguistic_indicators`: Grammar pattern (e.g., "question", "command")
- `situation_context`: Scenario type (e.g., "work_session", "commute_morning")
- `prosodic_features`: Speech patterns (e.g., "emphasized_destination")
- `conflict_markers`: Contradiction signals
- `input_fidelity`: Signal clarity [0.0-1.0]

### Determinism Guarantee

> **Same `command_text` + `context` = Identical `resolved_intent` + `confidence_score`**
> 
> Reproducible across requests, sessions, and deployments.
> Ideal for compliance auditing and regression testing.

### Response Structure

- `resolved_intent` (str): Top-ranked intent ID
- `confidence_score` (float): Confidence [0.0-1.0]
- `contributing_factors` (list): Ordered by contribution magnitude
- `alternative_intents` (dict): Runner-up scores
- `action_payload` (dict): Structured data for downstream execution
- `audit_trail` (dict): Full decision log
- `processing_time_ms` (float): Inference latency

### Banking Example

Request:
```json
{
  "command_text": "Transfer 500 to John's account",
  "context": {
    "location_context": "bank_branch_nyc",
    "user_profile": "analyst",
    "temporal_context": "2026-01-17T14:30:00Z",
    "semantic_capacity": 0.95,
    "social_propriety": 0.90
  }
}
```

Response:
```json
{
  "resolved_intent": "transfer_to_account",
  "confidence_score": 0.94,
  "contributing_factors": [
    {"factor_name": "location_context", "delta": 0.18, "influence": "boost"},
    {"factor_name": "temporal_context", "delta": 0.12, "influence": "boost"}
  ],
  "processing_time_ms": 3.2
}
```

### Automotive Example

Request:
```json
{
  "command_text": "Take me home",
  "context": {
    "location_context": "vehicle_interior",
    "goal_alignment": "navigate",
    "temporal_context": "2026-01-17T09:00:00Z",
    "semantic_capacity": 0.70,
    "input_fidelity": 0.72
  }
}
```

Response:
```json
{
  "resolved_intent": "navigate_home",
  "confidence_score": 0.88,
  "contributing_factors": [
    {"factor_name": "goal_alignment", "delta": 0.22, "influence": "boost"},
    {"factor_name": "location_context", "delta": 0.15, "influence": "boost"}
  ],
  "processing_time_ms": 2.8
}
```
""",
    response_description="Resolved intent with confidence, audit trail, and performance metrics",
)
```

---

## Pydantic Model Examples

### IntentRequest with Examples

```python
class IntentRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "summary": "Simple Command",
                    "description": "Minimal input with default context",
                    "value": {
                        "command_text": "Transfer 500"
                    }
                },
                {
                    "summary": "Contextual Banking Request",
                    "description": "Transfer with rich contextual factors",
                    "value": {
                        "command_text": "Transfer 500 to John's account",
                        "context": {
                            "location_context": "bank_branch_nyc",
                            "user_profile": "analyst",
                            "semantic_capacity": 0.95,
                            "temporal_context": "2026-01-17T14:30:00Z",
                            "social_propriety": 0.90,
                            "input_fidelity": 0.98
                        }
                    }
                },
                {
                    "summary": "Automotive Navigation",
                    "description": "Voice input with vehicle context",
                    "value": {
                        "command_text": "Take me home",
                        "context": {
                            "location_context": "vehicle_interior",
                            "goal_alignment": "navigate",
                            "situation_context": "commute_morning",
                            "user_profile": "commuter",
                            "semantic_capacity": 0.70,
                            "temporal_context": "2026-01-17T09:00:00Z",
                            "input_fidelity": 0.72
                        }
                    }
                }
            ]
        }
    )

    command_text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="**Raw user input command to resolve.** Can be natural language or structured command syntax.",
        json_schema_extra={"example": "Transfer 500 to John"}
    )

    context: ContextModel = Field(
        default_factory=ContextModel,
        description="**Optional contextual factors for disambiguation.** Leave empty for default context."
    )
```

### ContextModel with Detailed Fields

```python
class ContextModel(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Banking Transfer Example",
                    "value": {
                        "location_context": "bank_branch_nyc",
                        "user_profile": "analyst",
                        "semantic_capacity": 0.95,
                        "social_propriety": 0.85,
                        "temporal_context": "2026-01-17T14:30:00Z",
                        "association_history": ["check_balance", "view_accounts"],
                        "linguistic_indicators": "command",
                        "input_fidelity": 0.98
                    }
                },
                {
                    "name": "Automotive Navigation Example",
                    "value": {
                        "location_context": "vehicle_interior",
                        "temporal_context": "2026-01-17T09:00:00Z",
                        "goal_alignment": "navigate",
                        "situation_context": "commute_morning",
                        "user_profile": "commuter",
                        "association_history": ["check_weather", "play_podcast"],
                        "semantic_capacity": 0.70,
                        "input_fidelity": 0.72
                    }
                }
            ]
        }
    )

    association_history: Optional[List[str]] = Field(
        default=None,
        description="**Co-occurrence patterns:** Recent user intents for pattern matching.",
        json_schema_extra={"example": ["check_balance", "view_accounts", "initiate_transfer"]}
    )

    location_context: Optional[str] = Field(
        default=None,
        description="**Geographic/physical location:** GPS coords, branch code, 'vehicle_interior', 'home_office'.",
        json_schema_extra={"example": "bank_branch_nyc"}
    )

    temporal_context: Optional[str] = Field(
        default=None,
        description="**Time reference:** ISO 8601 timestamp for time-of-day reasoning.",
        json_schema_extra={"example": "2026-01-17T14:30:00Z"}
    )

    # ... (8 more fields with similar rich documentation)
```

---

## Swagger UI Appearance

When you visit `http://localhost:8000/docs`, you'll see:

### ✅ **API Title & Description**
- Large, eye-catching title: "Sphota Deterministic Context Engine"
- Markdown-formatted description with key features, use cases, and 12 factors
- Version badge: "1.0.0-beta"

### ✅ **Contact & License Info**
- Development team contact
- GitHub repository link
- MIT License link

### ✅ **Server Selection Dropdown**
- Local development: `http://localhost:8000`
- Production: `https://api.sphota.ai`

### ✅ **Tag Organization**
- "Intent Resolution" endpoint group
- "System" endpoint group

### ✅ **Endpoint Details**
- Rich markdown descriptions with formatting
- Code examples (Banking, Automotive)
- JSON request/response examples
- Input schema documentation
- Response descriptions

### ✅ **Example Payloads in Schemas**
- Multiple example tabs in request/response bodies
- Pre-filled "Try it out" examples
- Easy copy-paste for testing

---

## File Structure

```
c:\Users\vinee\Sphota.AI\
├── main.py (823 lines)          ← FastAPI application with enhanced OpenAPI
├── models.py (447 lines)         ← NEW: Pydantic models with rich metadata
├── core/                         ← Engine implementation
├── data/                         ← Datasets
├── docs/                         ← Documentation
├── tests/                        ← Test suite
└── scripts/                      ← Utilities
```

---

## Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **API Title** | Generic | Enterprise-grade: "Sphota Deterministic Context Engine" |
| **Description** | 1-line | Markdown with features, factors, use cases (300+ chars) |
| **Endpoint Docs** | Basic | Rich markdown with examples, input schema, determinism guarantee |
| **Model Examples** | Simple | Multiple realistic examples (Banking, Automotive, Simple) |
| **Field Descriptions** | Short | Detailed with business context and use case explanation |
| **Contact Info** | None | Team name, GitHub, email |
| **License** | None | MIT with link |
| **Servers** | None | Dev + Production endpoints |
| **Tags** | None | Organized by Intent Resolution & System |
| **Response Description** | None | Detailed field-by-field explanation |

---

## Usage

### Development
```bash
cd c:\Users\vinee\Sphota.AI
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Visit Swagger UI
```
http://localhost:8000/docs
```

### Try It Out
1. Click on **POST /resolve-intent**
2. Click **"Try it out"**
3. Select an example from the dropdown
4. Click **"Execute"**
5. See the response with audit trail

---

## Pydantic v2 Configuration

All models use `ConfigDict` with `json_schema_extra` for OpenAPI customization:

```python
model_config = ConfigDict(
    json_schema_extra={
        "examples": [
            {"summary": "...", "value": {...}},
            {"summary": "...", "value": {...}},
        ]
    }
)
```

This ensures:
- ✅ Multiple example tabs in Swagger UI
- ✅ Realistic payloads for testing
- ✅ Easy onboarding for developers
- ✅ Professional, polished appearance

---

## Next Steps

1. **Run the server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Open Swagger UI:**
   ```
   http://localhost:8000/docs
   ```

3. **Test endpoints:**
   - Select example payloads
   - Click "Try it out"
   - View responses with audit trails

4. **Share with stakeholders:**
   - Interactive API documentation
   - Professional appearance
   - Self-explaining with rich metadata
   - Ready for production deployment

---

## Files Modified

- **models.py** (NEW - 447 lines)
  - ContextModel
  - IntentRequest
  - ResolutionFactor
  - IntentResponse
  - HealthResponse

- **main.py** (REFACTORED - 823 lines)
  - Imports from `models.py`
  - Enhanced FastAPI metadata
  - Rich endpoint documentation
  - Markdown descriptions
  - Response descriptions

---

**Result:** Your FastAPI Swagger UI now looks like a professional Enterprise Product! 🎉
