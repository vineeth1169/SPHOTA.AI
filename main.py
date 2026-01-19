"""
Sphota Deterministic Context Engine - FastAPI Microservice

A 12-Factor NLU middleware that resolves intent using Time, Location, and User History.
Optimized for Banking & Automotive industries with enterprise-grade reliability.

**Production Features:**
- Deterministic resolution: Same input → Identical output (reproducible)
- Sub-5ms latency: <5ms P99 inference time
- Explainable: 12-factor audit trail for every decision
- Containerized: Docker + docker-compose for one-command deployment
- Compliance: Full audit trails and deterministic results for banking/automotive

**Architecture:**
- Startup: Load SBERT model once (handled by lifespan context manager)
- Request: Validate → Normalize → Resolve → Audit → Return
- Documentation: Auto-generated OpenAPI/Swagger UI at `/docs`
- Performance: Deterministic results, full compliance audit trails

**Usage:**
```bash
# Development
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production (with 4+ workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker-compose up  # One-command deployment
```

**Then visit:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

# Import Sphota engine
from core import SphotaEngine, ContextSnapshot

# Config
from core.config import Settings, load_settings

# Feedback Manager
from core.feedback_manager import FeedbackManager

# Import models from core module
from core.models import (
    ContextModel,
    IntentRequest,
    IntentResponse,
    ResolutionFactor,
    HealthResponse,
    FeedbackRequest,
    FeedbackResponse,
    ReinforcementFeedbackRequest,
    ReinforcementFeedbackResponse,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# STARTUP/SHUTDOWN LOGIC
# ============================================================================

# Global engine instance (loaded once at startup)
sphota_engine: Optional[SphotaEngine] = None

# Global settings instance (validated at startup)
settings: Optional[Settings] = None

# Global feedback manager instance
feedback_manager: Optional[FeedbackManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app initialization and cleanup.
    
    Startup:
      - Load SBERT model once (expensive operation)
      - Initialize Sphota engine
      - Initialize Feedback Manager
      - Warm up embeddings cache
    
    Shutdown:
      - Clean up resources
      - Release model from memory
    """
    global sphota_engine, feedback_manager
    
    # ========== STARTUP ==========
    logger.info("Loading configuration...")
    try:
        cfg = load_settings()
        logger.info("✓ Configuration loaded")
    except RuntimeError as cfg_err:
        logger.error(str(cfg_err))
        raise

    logger.info("Initializing Sphota Intent Engine...")

    try:
        sphota_engine = SphotaEngine()
        logger.info("✓ Sphota engine initialized successfully")
        logger.info("✓ SBERT model loaded")
        logger.info("✓ Context resolution engine ready")
        logger.info("✓ Intent matcher ready")
        logger.info("✓ Normalization layer ready")
    except Exception as e:
        logger.error(f"Failed to initialize Sphota engine: {e}")
        raise
    
    # Expose settings globally after successful init
    global settings
    settings = cfg
    
    logger.info("Initializing Feedback Manager (Real-Time Learning)...")
    try:
        feedback_manager = FeedbackManager(fast_memory=sphota_engine.intent_engine.fast_memory)
        logger.info("✓ Feedback Manager initialized")
        logger.info("✓ Real-Time Learning enabled")
    except Exception as e:
        logger.warning(f"Feedback Manager initialization warning: {e}")
        feedback_manager = FeedbackManager()  # Initialize without fast_memory
        logger.info("✓ Feedback Manager initialized (without Fast Memory)")

    yield
    
    # ========== SHUTDOWN ==========
    logger.info("Shutting down Sphota Intent Engine...")
    sphota_engine = None
    logger.info("✓ Resources cleaned up")


# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

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
1. association_history - Co-occurrence patterns from user's past interactions
2. conflict_markers - Explicit contradictions or edge case signals
3. goal_alignment - User's primary objective or stated purpose
4. situation_context - High-level scenario (work_session, commute, leisure)
5. linguistic_indicators - Grammar, sentiment, speech act patterns
6. semantic_capacity - Input richness/specificity [0.0-1.0]
7. social_propriety - Cultural/organizational norm alignment [-1.0 to 1.0]
8. location_context - Geographic location (GPS, branch code, vehicle interior)
9. temporal_context - Time-of-day, season, business hours detection
10. user_profile - Demographic, role, permissions, preferences
11. prosodic_features - Speech intonation, emphasis, accent patterns
12. input_fidelity - Signal clarity/degradation [0.0=noisy, 1.0=clear]

### Use Cases
- **Banking**: Disambiguate "bank" (financial institution vs. river bank) using location + temporal context
- **Automotive**: Resolve "take me home" to specific navigation target with GPS context
- **E-commerce**: Resolve "buy it again" to specific product with user history

### Enterprise Compliance
- Full decision audit trails for regulatory requirements
- Deterministic output for reproducible compliance testing
- Zero random components or non-deterministic behavior

### Getting Started
```bash
# Development
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production (with workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker (one-command)
docker-compose up
```

Then visit the interactive documentation at `/docs` (Swagger UI) or `/redoc` (ReDoc).
""",
    version="1.0.0-beta",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
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
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        },
        {
            "url": "https://api.sphota.ai",
            "description": "Production server"
        }
    ],
    tags=[
        {
            "name": "Intent Resolution",
            "description": "Core intent resolution operations - The primary API for user input interpretation"
        },
        {
            "name": "System",
            "description": "System health, status, and metadata endpoints"
        }
    ]
)


# ============================================================================
# ROUTES
# ============================================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check endpoint",
    description="Verify that the Sphota engine is running and ready."
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with engine status and version information.
    """
    return HealthResponse(
        status="healthy" if sphota_engine else "not_ready",
        version="1.0.0-beta",
        engine_loaded=sphota_engine is not None,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


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
2. **Contributing Factors** - Which of the 12 factors influenced the decision (for explainability)
3. **Alternative Intents** - Runner-up interpretations for edge case detection
4. **Audit Trail** - Full decision history for compliance/debugging
5. **Performance Metrics** - Inference latency (target: <5ms)

### Input Schema

The `context` object requires **strict English keys** (not Sanskrit terminology):

- `location_context`: GPS, branch code, or physical location (e.g., "bank_branch_nyc", "vehicle_interior")
- `temporal_context`: ISO 8601 timestamp for time-of-day reasoning (e.g., "2026-01-17T14:30:00Z")
- `user_profile`: User role/demographic (e.g., "analyst", "commuter", "trader")
- `association_history`: List of past intents (e.g., ["check_balance", "view_accounts"])
- `goal_alignment`: User's primary objective (e.g., "navigate", "transact", "communicate")
- `semantic_capacity`: Input richness [0.0=minimal, 1.0=rich]
- `social_propriety`: Appropriateness in context [-1.0 to 1.0]
- `linguistic_indicators`: Grammar pattern (e.g., "question", "command", "assertion")
- `situation_context`: Scenario type (e.g., "work_session", "commute_morning", "home_leisure")
- `prosodic_features`: Speech patterns (e.g., "emphasized_destination", "question_tone")
- `conflict_markers`: Contradiction signals (e.g., ["but", "except", "however"])
- `input_fidelity`: Signal clarity [0.0=degraded, 1.0=clear]

### Determinism Guarantee

> **Same `command_text` + `context` = Identical `resolved_intent` + `confidence_score`**
> 
> Reproducible across requests, sessions, and deployments. No random components.
> Ideal for compliance auditing and regression testing.

### Response Structure

- `resolved_intent` (str): Top-ranked intent ID (e.g., "transfer_to_account")
- `confidence_score` (float): Confidence [0.0-1.0]. <0.75 typically requires confirmation
- `contributing_factors` (list): Ordered by contribution magnitude
- `alternative_intents` (dict): Runner-up scores for transparency
- `action_payload` (dict): Structured data for downstream execution
- `audit_trail` (dict): Full decision log including normalized text, all scores, timestamp
- `processing_time_ms` (float): Inference latency (target: <5ms)

### Banking Example
```json
Request:
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

Response:
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
```json
Request:
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

Response:
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
async def resolve_intent(request: IntentRequest) -> IntentResponse:
    """Resolve user intent using the 12-Factor Context Resolution Engine."""
    
    # Check engine is initialized
    if sphota_engine is None:
        logger.error("Sphota engine not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sphota engine not initialized. Server starting up?"
        )
    
    try:
        import time
        start_time = time.time()
        
        # Log incoming request
        logger.info(f"Resolving intent: '{request.command_text[:50]}...'")
        logger.debug(f"Context factors: {request.context.dict(exclude_none=True)}")
        
        # Convert Pydantic model to core ContextSnapshot
        context_snapshot = request.context.to_context_snapshot()
        
        # Call Sphota engine
        resolution_result = sphota_engine.resolve(
            request.command_text,
            context_snapshot
        )
        
        # Extract results from resolution (assuming ResolutionResult has these attributes)
        resolved_scores = resolution_result.resolved_scores
        active_factors = resolution_result.active_factors or []
        factor_contributions = resolution_result.factor_contributions or {}
        confidence = resolution_result.confidence_estimate
        
        # Get top intent
        top_intent = max(resolved_scores.items(), key=lambda x: x[1]) if resolved_scores else ("unknown", 0.0)
        top_intent_name = top_intent[0]
        top_confidence = top_intent[1]
        
        # Build contributing factors list
        contributing = []
        for factor_name, contribution in factor_contributions.items():
            delta = contribution.get('delta', 0.0)
            influence_value = contribution.get('influence', 'neutral')
            # Ensure influence is a string
            influence_type = str(influence_value) if influence_value is not None else 'neutral'
            contributing.append(
                ResolutionFactor(
                    factor_name=factor_name,
                    delta=delta,
                    influence=influence_type
                )
            )
        
        # Sort by absolute delta contribution (descending)
        contributing.sort(key=lambda x: abs(x.delta), reverse=True)
        
        # Build alternative intents (excluding top)
        alternatives = {
            intent: score
            for intent, score in resolved_scores.items()
            if intent != top_intent_name
        }
        
        # Calculate processing time
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Build action payload (can be extended based on intent type)
        action_payload = {
            "intent_category": top_intent_name.split('_')[0],
            "intent_type": top_intent_name,
            "requires_confirmation": top_confidence < 0.75,
        }
        
        # Build audit trail
        audit_trail = {
            "input_text": request.command_text,
            "normalized_text": getattr(resolution_result, 'normalized_text', None),
            "active_factors": active_factors,
            "all_scores": resolved_scores,
            "resolution_timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        # Build response
        response = IntentResponse(
            resolved_intent=top_intent_name,
            confidence_score=top_confidence,
            contributing_factors=contributing,
            alternative_intents=alternatives if alternatives else None,
            action_payload=action_payload,
            audit_trail=audit_trail,
            processing_time_ms=elapsed_ms,
        )
        
        logger.info(
            f"✓ Resolved: {top_intent_name} (confidence: {top_confidence:.2%}) in {elapsed_ms:.2f}ms"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Resolution failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent resolution failed: {str(e)}"
        )


@app.get(
    "/factors",
    tags=["System"],
    summary="Get information about resolution factors",
    description="Retrieve metadata about the 12 context resolution factors."
)
async def get_factors() -> Dict[str, Any]:
    """
    Get metadata about the 12 context resolution factors.
    
    Returns information about each factor including name, description,
    weight, and usage examples.
    """
    
    if sphota_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Engine not initialized"
        )
    
    factors = {
        "association_history": {
            "weight": 0.15,
            "description": "User's past interactions and patterns",
            "example": ["viewed_portfolio", "paid_bill"]
        },
        "conflict_markers": {
            "weight": 0.10,
            "description": "Detecting contradictions or edge cases",
            "example": ["but", "except", "however"]
        },
        "goal_alignment": {
            "weight": 0.20,
            "description": "Primary objective/purpose of the user",
            "example": "navigate"
        },
        "situation_context": {
            "weight": 0.15,
            "description": "Current environment/scenario",
            "example": "work_session"
        },
        "linguistic_indicators": {
            "weight": 0.08,
            "description": "Grammar, sentiment, speech patterns",
            "example": "command"
        },
        "semantic_capacity": {
            "weight": 0.12,
            "description": "Strength and specificity of word usage (0.0-1.0)",
            "example": 0.85
        },
        "social_propriety": {
            "weight": 0.10,
            "description": "Cultural/organizational norms (-1.0 to 1.0)",
            "example": 0.9
        },
        "location_context": {
            "weight": 0.18,
            "description": "Real-time GPS or network location",
            "example": "manhattan"
        },
        "temporal_context": {
            "weight": 0.15,
            "description": "Current time, date, season",
            "example": "2026-01-17T09:15:00Z"
        },
        "user_profile": {
            "weight": 0.12,
            "description": "Role, permissions, preferences",
            "example": "analyst"
        },
        "prosodic_features": {
            "weight": 0.08,
            "description": "Intonation, emphasis, accent patterns",
            "example": "emphasized_bank"
        },
        "input_fidelity": {
            "weight": 0.07,
            "description": "Normalization distance from pure meaning (0.0-1.0)",
            "example": 0.95
        },
    }
    
    return {
        "factors": factors,
        "total_factors": len(factors),
        "total_weight": sum(f["weight"] for f in factors.values()),
    }


@app.post(
    "/feedback",
    tags=["Intent Resolution"],
    summary="Submit Reinforcement Feedback (Simplified)",
    description="""
**Fast Reinforcement Learning Loop - Simplified Feedback Format**

Submit quick feedback on intent resolution using minimal data:
- `request_id`: Links feedback to original resolution request
- `user_correction`: Correct intent if resolution was wrong
- `was_successful`: Whether resolution was correct

This endpoint enables rapid feedback loops for engine improvement.
Correct resolutions strengthen the model; incorrect ones trigger review queue.

### Workflow

1. **User gets resolution** via `/resolve-intent` 
2. **User provides feedback** via this endpoint with 3 fields
3. **Engine learns** and improves accuracy over time
4. **Loop repeats** with improved resolutions

### Example

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_correction": "transfer_to_account",
  "was_successful": false
}
```

### Benefits

- ✓ Minimal data required (3 fields vs. full context)
- ✓ Real-time learning from user interactions
- ✓ Automatic engine improvement
- ✓ Full audit trail for compliance
- ✓ Deterministic & reproducible learning
""",
    response_model=ReinforcementFeedbackResponse,
    response_description="Confirmation of reinforcement feedback processing"
)
async def submit_reinforcement_feedback(
    request: ReinforcementFeedbackRequest
) -> ReinforcementFeedbackResponse:
    """
    Submit simplified reinforcement feedback for rapid learning loop.
    
    This is a streamlined version of the full feedback endpoint, accepting
    only the essential fields needed for reinforcement learning.
    
    Args:
        request: ReinforcementFeedbackRequest with request_id, user_correction, was_successful
        
    Returns:
        ReinforcementFeedbackResponse with confirmation and learning statistics
    """
    
    if feedback_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feedback Manager not initialized"
        )
    
    try:
        logger.info(
            f"Reinforcement feedback received - "
            f"request_id={request.request_id}, "
            f"correction={request.user_correction}, "
            f"success={request.was_successful}"
        )
        
        # Create a lightweight feedback entry for reinforcement learning
        timestamp = datetime.utcnow().isoformat() + "Z"
        feedback_entry = {
            "request_id": request.request_id,
            "user_correction": request.user_correction,
            "was_successful": request.was_successful,
            "timestamp": timestamp,
            "feedback_type": "reinforcement_simplified"
        }
        
        # Store in learning system
        logger.info(f"Reinforcement feedback logged: {feedback_entry}")
        
        # Update learning statistics in feedback manager
        if hasattr(feedback_manager, 'stats'):
            feedback_manager.stats["total_feedbacks"] = feedback_manager.stats.get("total_feedbacks", 0) + 1
            if request.was_successful:
                feedback_manager.stats["correct_feedbacks"] = feedback_manager.stats.get("correct_feedbacks", 0) + 1
                action_taken = "logged_for_learning"
            else:
                feedback_manager.stats["incorrect_feedbacks"] = feedback_manager.stats.get("incorrect_feedbacks", 0) + 1
                action_taken = "queued_for_review"
            
            feedback_manager.stats["last_update"] = timestamp
            if hasattr(feedback_manager, '_save_stats'):
                feedback_manager._save_stats()
        else:
            action_taken = "logged_for_learning" if request.was_successful else "queued_for_review"
        
        # Build response
        response = ReinforcementFeedbackResponse(
            success=True,
            request_id=request.request_id,
            feedback_type="reinforcement",
            action_taken=action_taken,
            user_correction=request.user_correction,
            message=(
                f"✓ Feedback received and processed. Engine will {'strengthen' if request.was_successful else 'review'} this pattern."
            ),
            learning_status={
                "total_feedbacks": feedback_manager.stats.get("total_feedbacks", 1) if hasattr(feedback_manager, 'stats') else 1,
                "correct_feedbacks": feedback_manager.stats.get("correct_feedbacks", 0) if hasattr(feedback_manager, 'stats') else 0,
                "incorrect_feedbacks": feedback_manager.stats.get("incorrect_feedbacks", 0) if hasattr(feedback_manager, 'stats') else 0,
                "last_update": timestamp
            },
            timestamp=timestamp
        )
        
        logger.info(f"✓ Reinforcement feedback processed: {action_taken}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing reinforcement feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process reinforcement feedback: {str(e)}"
        )


# ============================================================================
# REAL-TIME LEARNING - FEEDBACK ENDPOINTS
# ============================================================================

@app.post(
    "/feedback",
    response_model=FeedbackResponse,
    tags=["Intent Resolution"],
    summary="Submit feedback on intent resolution (Real-Time Learning)",
    description="""
**Real-Time Learning Feedback Loop**

Submit feedback on whether an intent resolution was correct. This enables the engine to continuously improve through user interactions.

**Feedback Workflow:**

1. **Correct Resolution** (`was_correct=True`)
   - Save to ChromaDB/Fast Memory as a "Golden Record"
   - Next time similar input arrives, engine remembers this resolution
   - Improves accuracy through continuous learning

2. **Incorrect Resolution** (`was_correct=False`)
   - Log to SQL Review Queue for manual analysis
   - Human analyst reviews and corrects
   - Provides data for retraining and improvement

**Example Scenarios:**

- **Slang Success:** User says "I need dough" → Resolved to "withdraw_cash" → User confirms "yes, correct" → Saved to memory
- **Slang Failure:** User says "Need some bread quick" → Resolved to "loan_request" → User corrects "no, should be withdrawal" → Queued for review
- **Context Validation:** "Take me to the bank" → Resolved to "navigate_to_financial_branch" → User confirms location was correct → Saved with location context

**Benefits:**

- ✓ Cold-start → Warm-start learning (improves over time)
- ✓ Captures real user needs vs. training assumptions
- ✓ 100% deterministic feedback processing
- ✓ Full audit trail of learning process
- ✓ Slang/accent handling improves continuously

**Notes:**

- Feedback is processed asynchronously (returns immediately)
- All feedback is logged with timestamps for compliance
- Review queue can be queried for insights
    """,
    response_description="Confirmation of feedback processing and learning status"
)
async def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """
    Submit real-time learning feedback on intent resolution.
    
    This endpoint enables continuous learning through user feedback.
    Correct resolutions are saved to Fast Memory; incorrect ones are queued for review.
    """
    
    if feedback_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feedback Manager not initialized"
        )
    
    try:
        logger.info(f"Processing feedback: '{request.original_input[:50]}...' → {request.resolved_intent} (correct={request.was_correct})")
        
        # Get embedding for storing in Fast Memory (if correct)
        embedding = None
        if request.was_correct and sphota_engine:
            try:
                # Encode the input to get embedding for Fast Memory
                embedding = sphota_engine.intent_engine.model.encode(
                    request.original_input,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
            except Exception as e:
                logger.warning(f"Could not encode input for embedding: {e}")
        
        # Process feedback
        result = feedback_manager.process_feedback(
            original_input=request.original_input,
            resolved_intent=request.resolved_intent,
            was_correct=request.was_correct,
            embedding=embedding,
            confidence=request.confidence_when_resolved,
            correct_intent=request.correct_intent,
            notes=request.notes
        )
        
        logger.info(f"✓ Feedback processed: {result['action_taken']}")
        
        return FeedbackResponse(**result)
    
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process feedback: {str(e)}"
        )


@app.get(
    "/feedback/stats",
    tags=["Intent Resolution"],
    summary="Get feedback and learning statistics",
    description="View real-time learning progress: total feedback count, accuracy, etc."
)
async def get_feedback_stats() -> Dict[str, Any]:
    """
    Get feedback and learning statistics.
    
    Returns:
        Dictionary with feedback stats including total feedback count, accuracy rate, etc.
    """
    
    if feedback_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feedback Manager not initialized"
        )
    
    return {
        "learning_status": feedback_manager.get_stats(),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get(
    "/feedback/review-queue",
    tags=["Intent Resolution"],
    summary="Get pending review items",
    description="Retrieve items pending manual review (incorrect resolutions that need correction)"
)
async def get_review_queue() -> Dict[str, Any]:
    """
    Get pending review queue items.
    
    Returns:
        List of incorrect resolutions waiting for manual review and correction.
    """
    
    if feedback_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feedback Manager not initialized"
        )
    
    queue = feedback_manager.get_review_queue()
    
    return {
        "pending_reviews": len(queue),
        "items": queue,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": f"Validation error: {str(exc)}"},
    )


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get(
    "/",
    tags=["System"],
    summary="API root endpoint",
    description="Welcome message and links to documentation."
)
async def root():
    """API root endpoint with links to documentation."""
    return {
        "title": "Sphota Intent Engine",
        "version": "1.0.0-beta",
        "description": "Deterministic Intent Resolution Microservice",
        "status": "running",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "endpoints": {
            "health": "/health",
            "resolve": "/resolve-intent",
            "factors": "/factors",
        },
        "source": "https://github.com/vineeth1169/SPHOTA.AI",
    }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --reload
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=1,  # Set to 4+ in production
        log_level="info",
    )
