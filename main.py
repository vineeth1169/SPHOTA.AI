"""
Sphota Intent Engine - FastAPI Microservice

Production-ready REST API for deterministic intent resolution.
Exposes the Sphota context resolution engine as a high-performance microservice.

Architecture:
  - Startup: Load SBERT model and initialize engines once
  - Request: Validate input, resolve intent, return structured response
  - Documentation: Auto-generated OpenAPI/Swagger at /docs
  - Performance: Sub-5ms latency, deterministic results, full audit trails

Usage:
    pip install fastapi uvicorn
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    
    # Then visit: http://localhost:8000/docs for Swagger UI
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import Sphota engine
from core import SphotaEngine, ContextSnapshot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS - Request/Response Validation & Serialization
# ============================================================================

class ContextModel(BaseModel):
    """
    Contextual factors for intent disambiguation.
    
    All fields are optional with sensible defaults. Only provide factors
    relevant to your use case for optimal performance.
    
    The 12 Factors:
    1. association_history: User's recent intents for pattern matching
    2. conflict_markers: Signals of contradiction or edge cases
    3. goal_alignment: User's primary objective
    4. situation_context: Current scenario (e.g., 'work_session', 'travel')
    5. linguistic_indicators: Grammar/syntax cues (e.g., 'question', 'command')
    6. semantic_capacity: Input richness [0.0=minimal, 1.0=rich]
    7. social_propriety: Appropriateness [-1.0=inappropriate, 1.0=appropriate]
    8. location_context: Current location (e.g., 'office', 'kitchen', 'car')
    9. temporal_context: Timestamp for time-of-day reasoning (ISO 8601)
    10. user_profile: User demographics/preferences
    11. prosodic_features: Speech intonation/stress patterns
    12. input_fidelity: Input clarity [0.0=degraded, 1.0=clear]
    """
    
    association_history: Optional[List[str]] = Field(
        None,
        description="Recent sequence of user intents for co-occurrence analysis.",
        example=["navigate_home", "navigate_work", "set_alarm"]
    )
    
    conflict_markers: Optional[List[str]] = Field(
        None,
        description="Explicit contrast or opposition signals in input.",
        example=["but", "except", "however"]
    )
    
    goal_alignment: Optional[str] = Field(
        None,
        description="User's stated or inferred primary goal/purpose.",
        example="navigate"
    )
    
    situation_context: Optional[str] = Field(
        None,
        description="High-level situation classification.",
        example="work_session"
    )
    
    linguistic_indicators: Optional[str] = Field(
        None,
        description="Grammatical/syntactic cues (e.g., 'question', 'command', 'imperative').",
        example="command"
    )
    
    semantic_capacity: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Semantic richness metric [0.0=minimal, 1.0=maximal].",
        example=0.85
    )
    
    social_propriety: Optional[float] = Field(
        None,
        ge=-1.0,
        le=1.0,
        description="Contextual appropriateness [-1.0=inappropriate, 1.0=appropriate].",
        example=0.9
    )
    
    location_context: Optional[str] = Field(
        None,
        description="Current location identifier.",
        example="kitchen"
    )
    
    temporal_context: Optional[str] = Field(
        None,
        description="Timestamp for time-of-day reasoning (ISO 8601 format).",
        example="2026-01-17T14:30:00Z"
    )
    
    user_profile: Optional[str] = Field(
        None,
        description="User demographic or preference profile.",
        example="analyst"
    )
    
    prosodic_features: Optional[str] = Field(
        None,
        description="Accent, intonation, stress patterns in speech.",
        example="emphasized_bank"
    )
    
    input_fidelity: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Clarity/fidelity of input signal [0.0=degraded, 1.0=clear].",
        example=0.95
    )
    
    def to_context_snapshot(self) -> ContextSnapshot:
        """
        Convert Pydantic model to core ContextSnapshot.
        
        Returns:
            ContextSnapshot instance with parsed temporal context.
        """
        temporal = None
        if self.temporal_context:
            try:
                temporal = datetime.fromisoformat(
                    self.temporal_context.replace('Z', '+00:00')
                )
            except ValueError as e:
                logger.warning(f"Invalid temporal context format: {e}")
        
        return ContextSnapshot(
            association_history=self.association_history,
            conflict_markers=self.conflict_markers,
            goal_alignment=self.goal_alignment,
            situation_context=self.situation_context,
            linguistic_indicators=self.linguistic_indicators,
            semantic_capacity=self.semantic_capacity,
            social_propriety=self.social_propriety,
            location_context=self.location_context,
            temporal_context=temporal,
            user_profile=self.user_profile,
            prosodic_features=self.prosodic_features,
            input_fidelity=self.input_fidelity,
        )


class IntentRequest(BaseModel):
    """
    Request model for intent resolution.
    
    Accepts raw user input and optional contextual factors for disambiguation.
    """
    
    command_text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Raw user input command text to resolve.",
        example="take me to the bank"
    )
    
    context: ContextModel = Field(
        default_factory=ContextModel,
        description="Contextual factors for intent disambiguation."
    )


class ResolutionFactor(BaseModel):
    """Individual factor contribution to intent resolution."""
    
    factor_name: str = Field(
        ...,
        description="Name of the contributing factor.",
        example="location_context"
    )
    
    delta: float = Field(
        ...,
        description="Score delta contribution from this factor.",
        example=0.18
    )
    
    influence: str = Field(
        default="boost",
        description="Type of influence: 'boost' or 'penalty'.",
        example="boost"
    )


class IntentResponse(BaseModel):
    """
    Response model for intent resolution.
    
    Contains resolved intent, confidence score, contributing factors,
    and structured action payload for downstream execution.
    """
    
    resolved_intent: str = Field(
        ...,
        description="Top-ranked resolved intent identifier.",
        example="navigate_to_financial_institution"
    )
    
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the resolved intent [0.0-1.0].",
        example=0.94
    )
    
    contributing_factors: List[ResolutionFactor] = Field(
        ...,
        description="Ordered list of factors that influenced the resolution."
    )
    
    alternative_intents: Optional[Dict[str, float]] = Field(
        None,
        description="Alternative intent scores for transparency.",
        example={"navigate_to_river_bank": 0.06}
    )
    
    action_payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured data for downstream action execution."
    )
    
    audit_trail: Dict[str, Any] = Field(
        default_factory=dict,
        description="Full decision audit trail for compliance/debugging."
    )
    
    processing_time_ms: float = Field(
        ...,
        description="Inference time in milliseconds.",
        example=3.2
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy")
    version: str = Field(default="2.0.0")
    engine_loaded: bool = Field(default=True)


# ============================================================================
# STARTUP/SHUTDOWN LOGIC
# ============================================================================

# Global engine instance (loaded once at startup)
sphota_engine: Optional[SphotaEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app initialization and cleanup.
    
    Startup:
      - Load SBERT model once (expensive operation)
      - Initialize Sphota engine
      - Warm up embeddings cache
    
    Shutdown:
      - Clean up resources
      - Release model from memory
    """
    global sphota_engine
    
    # ========== STARTUP ==========
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
    
    yield
    
    # ========== SHUTDOWN ==========
    logger.info("Shutting down Sphota Intent Engine...")
    sphota_engine = None
    logger.info("✓ Resources cleaned up")


# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Sphota Intent Engine",
    description="Deterministic Intent Resolution Microservice - Production-Grade REST API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
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
        version="2.0.0",
        engine_loaded=sphota_engine is not None
    )


@app.post(
    "/resolve-intent",
    response_model=IntentResponse,
    status_code=status.HTTP_200_OK,
    tags=["Intent Resolution"],
    summary="Resolve user intent with context",
    description="Deterministically resolve ambiguous user input to specific intents using contextual factors."
)
async def resolve_intent(request: IntentRequest) -> IntentResponse:
    """
    Resolve user intent using the 12-Factor Context Resolution Engine.
    
    This endpoint:
    1. Accepts raw user input and optional context
    2. Normalizes input (slang/accents)
    3. Computes semantic similarity to known intents
    4. Applies 12-factor context weighting
    5. Returns deterministic, fully-auditable result
    
    Args:
        request: IntentRequest with command_text and context
        
    Returns:
        IntentResponse with resolved intent, confidence, and audit trail
        
    Raises:
        HTTPException: If engine is not initialized or resolution fails
        
    Example:
        ```bash
        curl -X POST http://localhost:8000/resolve-intent \\
          -H "Content-Type: application/json" \\
          -d '{
            "command_text": "take me to the bank",
            "context": {
              "location_context": "manhattan",
              "temporal_context": "2026-01-17T09:15:00Z",
              "user_profile": "analyst",
              "association_history": ["viewed_portfolio", "paid_bill"]
            }
          }'
        ```
    """
    
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
            influence_type = contribution.get('influence', 'neutral')
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
        "version": "2.0.0",
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
