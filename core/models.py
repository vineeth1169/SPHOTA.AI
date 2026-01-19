"""
Sphota Context Resolution Engine - Pydantic Models

Rich data models with enterprise-grade metadata for OpenAPI documentation.
Includes JSON schema examples, field constraints, and detailed descriptions.

Models:
  - ContextModel: 12-factor context snapshot for disambiguation
  - IntentRequest: User input + context wrapper
  - ResolutionFactor: Individual factor contribution
  - IntentResponse: Full resolution result with audit trail
  - HealthResponse: System health status
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from pydantic import BaseModel, Field, ConfigDict

# Only needed for type checkers to resolve return annotation without runtime import
if TYPE_CHECKING:
    from core import ContextSnapshot


# ============================================================================
# CONTEXT MODEL - 12-FACTOR CONTEXT SNAPSHOT
# ============================================================================

class ContextModel(BaseModel):
    """
    12-Factor Contextual Snapshot for Deterministic Intent Disambiguation
    
    The Sphota engine uses 12 independent context factors to resolve ambiguous
    user input to specific intents. All fields are optional with sensible defaults.
    
    **The 12 Factors:**
    
    1. **association_history** - Co-occurrence patterns from past interactions
    2. **conflict_markers** - Explicit contradictions or edge case signals  
    3. **goal_alignment** - User's primary objective or stated purpose
    4. **situation_context** - High-level scenario (e.g., 'work_session', 'home_leisure')
    5. **linguistic_indicators** - Grammar, sentiment, speech act patterns
    6. **semantic_capacity** - Input richness/specificity [0.0=minimal, 1.0=rich]
    7. **social_propriety** - Cultural/organizational norm alignment [-1.0 to 1.0]
    8. **location_context** - Geographic location (GPS, network, inferred)
    9. **temporal_context** - Time-of-day, season, calendar context
    10. **user_profile** - Demographic profile, role, permissions
    11. **prosodic_features** - Speech intonation, emphasis, accent patterns
    12. **input_fidelity** - Signal clarity/degradation [0.0=noisy, 1.0=clear]
    
    **Use in Banking/Automotive:**
    
    - Banking: Disambiguate "bank" (financial institution vs. river bank)
    - Automotive: Resolve "go home" to specific navigation target
    
    **Best Practices:**
    
    - Provide only relevant factors (engine handles None values)
    - Use ISO 8601 timestamps for `temporal_context`
    - Keep `association_history` limited to recent intents (5-20 items)
    """

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
        description="**Co-occurrence patterns:** Sequence of recent user intents for pattern matching. Enables context-aware disambiguation based on interaction history.",
        json_schema_extra={
            "example": ["check_balance", "view_accounts", "initiate_transfer"],
            "minItems": 1,
            "maxItems": 20
        }
    )

    conflict_markers: Optional[List[str]] = Field(
        default=None,
        description="**Contradiction signals:** Explicit contrast words that indicate edge cases or exceptions ('but', 'except', 'however', 'instead'). Used to flag alternative interpretations.",
        json_schema_extra={
            "example": ["but", "except", "however"],
            "minItems": 1
        }
    )

    goal_alignment: Optional[str] = Field(
        default=None,
        description="**Primary objective:** User's stated or inferred goal (e.g., 'navigate', 'communicate', 'transact'). Constrains resolution to goal-aligned intents.",
        json_schema_extra={"example": "transact"}
    )

    situation_context: Optional[str] = Field(
        default=None,
        description="**Scenario classification:** High-level situation type such as 'work_session', 'home_leisure', 'commute_morning', 'driving'. Context-dependent factor weighting.",
        json_schema_extra={"example": "work_session"}
    )

    linguistic_indicators: Optional[str] = Field(
        default=None,
        description="**Grammatical cues:** Speech act or syntactic indicator ('question', 'command', 'imperative', 'assertion'). Disambiguates intent from sentence structure.",
        json_schema_extra={"example": "command"}
    )

    semantic_capacity: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="**Input richness:** Semantic specificity metric. 0.0=minimal vocabulary, 1.0=rich/detailed. Confidence in semantic interpretation.",
        json_schema_extra={"example": 0.85}
    )

    social_propriety: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="**Norm alignment:** Contextual appropriateness in organizational/cultural context. -1.0=inappropriate, 1.0=appropriate, 0.0=neutral.",
        json_schema_extra={"example": 0.90}
    )

    location_context: Optional[str] = Field(
        default=None,
        description="**Geographic/physical location:** Current location identifier (GPS coords, branch code, 'vehicle_interior', 'home_office'). Critical for location-dependent disambiguation.",
        json_schema_extra={"example": "bank_branch_nyc"}
    )

    temporal_context: Optional[str] = Field(
        default=None,
        description="**Time reference:** ISO 8601 timestamp for time-of-day reasoning, seasonal context, business hours detection. Example: `2026-01-17T14:30:00Z`",
        json_schema_extra={"example": "2026-01-17T14:30:00Z"}
    )

    user_profile: Optional[str] = Field(
        default=None,
        description="**User demographics:** Role, permission level, or preference profile (e.g., 'analyst', 'trader', 'commuter', 'premium_member'). Enables personalization.",
        json_schema_extra={"example": "analyst"}
    )

    prosodic_features: Optional[str] = Field(
        default=None,
        description="**Speech acoustics:** Accent, intonation, stress patterns in voice input (e.g., 'emphasized_destination', 'question_tone'). Used in voice intent resolution.",
        json_schema_extra={"example": "emphasized_destination"}
    )

    input_fidelity: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="**Signal clarity:** Input quality/noise level. 0.0=heavily degraded, 1.0=crystal clear. Critical for voice/noisy channels.",
        json_schema_extra={"example": 0.95}
    )

    def to_context_snapshot(self) -> "ContextSnapshot":
        """
        Convert Pydantic model to core engine ContextSnapshot.
        
        Handles ISO 8601 timestamp parsing and validation.
        
        Returns:
            ContextSnapshot instance compatible with SphotaEngine.resolve()
        """
        from core import ContextSnapshot
        
        temporal = None
        if self.temporal_context:
            try:
                temporal = datetime.fromisoformat(
                    self.temporal_context.replace('Z', '+00:00')
                )
            except ValueError as e:
                raise ValueError(f"Invalid temporal context format: {e}")

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


# ============================================================================
# INTENT REQUEST - USER INPUT + CONTEXT WRAPPER
# ============================================================================

class IntentRequest(BaseModel):
    """
    **Intent Resolution Request**
    
    Encapsulates raw user input and optional contextual factors.
    The engine deterministically resolves the input to a specific intent
    using the 12-factor context model.
    
    **Determinism Guarantee:**
    
    > Same `command_text` + `context` → Identical `resolved_intent` + `confidence_score`
    > (Reproducible across requests, sessions, deployments)
    
    **Use Cases:**
    
    - **Banking:** "Transfer 500" → Resolve to `transfer_to_account`
    - **Automotive:** "Take me home" → Resolve to `navigate_home` with GPS context
    - **E-commerce:** "Buy it again" → Resolve to `reorder_last_purchase` with history context
    """

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
                            "user_history": ["salary_deposit", "bill_payment"],
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
        description="**Raw user input command to resolve.** Can be natural language or structured command syntax. Engine normalizes slang, accents, and typos.",
        json_schema_extra={"example": "Transfer 500 to John"}
    )

    context: ContextModel = Field(
        default_factory=ContextModel,
        description="**Optional contextual factors for disambiguation.** Leave empty for default context. Provide only relevant factors for performance."
    )


# ============================================================================
# RESOLUTION FACTOR - INDIVIDUAL FACTOR CONTRIBUTION
# ============================================================================

class ResolutionFactor(BaseModel):
    """
    **Individual Factor Contribution to Intent Resolution**
    
    Represents one of the 12 context factors' contribution to the final resolution.
    Used in the `contributing_factors` list to explain the decision.
    
    **Transparency Feature:**
    
    Enables audit trails and explainability for compliance (banking/automotive).
    Shows exactly which factors influenced the resolution and by how much.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "factor_name": "location_context",
                "delta": 0.18,
                "influence": "boost"
            }
        }
    )

    factor_name: str = Field(
        ...,
        description="**Factor identifier:** One of the 12 context factors (e.g., 'location_context', 'temporal_context')",
        json_schema_extra={"example": "location_context"}
    )

    delta: float = Field(
        ...,
        description="**Score contribution:** Positive (boost) or negative (penalty) delta applied to candidate intents. Range: -1.0 to +1.0",
        json_schema_extra={"example": 0.18}
    )

    influence: str = Field(
        default="neutral",
        description="**Influence type:** 'boost' (increased confidence), 'penalty' (decreased confidence), or 'neutral' (no effect)",
        json_schema_extra={"example": "boost"}
    )


# ============================================================================
# INTENT RESPONSE - FULL RESOLUTION RESULT
# ============================================================================

class IntentResponse(BaseModel):
    """
    **Intent Resolution Response**
    
    Complete result of deterministic intent resolution including:
    - Resolved intent identifier
    - Confidence score
    - Contributing factors (explainability)
    - Alternative intents (edge case detection)
    - Action payload (downstream execution)
    - Audit trail (compliance/debugging)
    - Performance metrics
    
    **Designed for Production Enterprise Use:**
    
    - Compliance: Full audit trail for regulatory requirements
    - Explainability: Transparent factor contributions
    - Reliability: Deterministic, reproducible results
    - Performance: Sub-5ms latency guarantee
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "resolved_intent": "transfer_to_account",
                "confidence_score": 0.94,
                "contributing_factors": [
                    {
                        "factor_name": "location_context",
                        "delta": 0.18,
                        "influence": "boost"
                    },
                    {
                        "factor_name": "temporal_context",
                        "delta": 0.12,
                        "influence": "boost"
                    }
                ],
                "alternative_intents": {
                    "transfer_to_bank_branch": 0.04,
                    "navigate_to_bank": 0.02
                },
                "action_payload": {
                    "intent_category": "transfer",
                    "intent_type": "transfer_to_account",
                    "requires_confirmation": False
                },
                "processing_time_ms": 3.2
            }
        }
    )

    resolved_intent: str = Field(
        ...,
        description="**Top-ranked intent identifier.** The primary interpretation of the user's input given the context. Format: `category_subcategory` (e.g., 'transfer_to_account')",
        json_schema_extra={"example": "transfer_to_account"}
    )

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="**Confidence metric [0.0-1.0].** Probability that the resolved intent is correct. <0.75 typically requires confirmation.",
        json_schema_extra={"example": 0.94}
    )

    contributing_factors: List[ResolutionFactor] = Field(
        default_factory=list,
        description="**Ordered list of 12 factors that influenced resolution.** Sorted by absolute contribution magnitude (descending). Enables transparency and auditability.",
        json_schema_extra={"example": [
            {"factor_name": "location_context", "delta": 0.18, "influence": "boost"},
            {"factor_name": "temporal_context", "delta": 0.12, "influence": "boost"}
        ]}
    )

    alternative_intents: Optional[Dict[str, float]] = Field(
        default=None,
        description="**Runner-up intent scores.** Alternative interpretations ranked by confidence. Useful for edge case detection or user correction.",
        json_schema_extra={"example": {"transfer_to_bank_branch": 0.04, "navigate_to_bank": 0.02}}
    )

    action_payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="**Structured action data for downstream execution.** Keys depend on intent type. Example: transfer intents include account_id, amount, recipient.",
        json_schema_extra={"example": {
            "intent_category": "transfer",
            "intent_type": "transfer_to_account",
            "requires_confirmation": False
        }}
    )

    audit_trail: Dict[str, Any] = Field(
        default_factory=dict,
        description="**Full decision audit trail for compliance/debugging.** Includes normalized text, all candidate scores, resolution timestamp, active factors.",
        json_schema_extra={"example": {
            "input_text": "Transfer 500 to John",
            "normalized_text": "transfer 500 john",
            "active_factors": ["location_context", "temporal_context"],
            "all_scores": {"transfer_to_account": 0.94, "transfer_to_bank_branch": 0.04},
            "resolution_timestamp": "2026-01-17T14:30:15.234Z"
        }}
    )

    processing_time_ms: float = Field(
        ...,
        description="**Inference latency in milliseconds.** SLA target: <5ms for sub-second UX.",
        json_schema_extra={"example": 3.2}
    )


# ============================================================================
# HEALTH RESPONSE - SYSTEM STATUS
# ============================================================================

class HealthResponse(BaseModel):
    """
    **System Health Status**
    
    Reports operational status of the Sphota engine and its components.
    Used by container orchestration and monitoring systems.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0-beta",
                "engine_loaded": True,
                "timestamp": "2026-01-17T14:30:15Z"
            }
        }
    )

    status: str = Field(
        default="healthy",
        description="**Overall health status:** 'healthy', 'degraded', or 'not_ready'",
        json_schema_extra={"example": "healthy"}
    )

    version: str = Field(
        default="1.0.0-beta",
        description="**Engine version identifier** for deployment tracking",
        json_schema_extra={"example": "1.0.0-beta"}
    )

    engine_loaded: bool = Field(
        default=True,
        description="**SBERT model loaded in memory.** False if still initializing or startup failed.",
        json_schema_extra={"example": True}
    )

    timestamp: Optional[str] = Field(
        default=None,
        description="**UTC timestamp of health check.** ISO 8601 format.",
        json_schema_extra={"example": "2026-01-17T14:30:15Z"}
    )

# ============================================================================
# FEEDBACK MODELS - REAL-TIME LEARNING
# ============================================================================

class FeedbackRequest(BaseModel):
    """
    **Real-Time Learning Feedback**
    
    User feedback on whether an intent resolution was correct.
    This enables the engine to continuously learn and improve accuracy.
    
    **Feedback Loop:**
    
    - If `was_correct=True` → Save to ChromaDB as "Golden Record" for future retrieval
    - If `was_correct=False` → Log to SQL Review Queue for manual analysis
    
    **Benefits:**
    
    - Improves accuracy over time (cold-start → warm-start)
    - Captures real user needs vs. training data assumptions
    - Enables A/B testing and progressive refinement
    - 100% deterministic: Same feedback = Same learning
    
    **Example Workflows:**
    
    1. **User Corrects Slang:** "I need dough" incorrectly → "withdraw_cash"
       - User feedback: "was_correct=False"
       - Logged for review + manual correction
       
    2. **System Validates Success:** "Transfer 500 to John"
       - System: "Resolved to transfer_to_account with 0.94 confidence"
       - User: "Yes, that's correct"
       - Saved to ChromaDB for future reference
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "summary": "Correct Resolution (Golden Record)",
                    "description": "User confirms the resolved intent was correct",
                    "value": {
                        "original_input": "Transfer 500 to John",
                        "resolved_intent": "transfer_to_account",
                        "was_correct": True,
                        "confidence_when_resolved": 0.94,
                        "notes": "User confirmed intent was correct"
                    }
                },
                {
                    "summary": "Incorrect Resolution (Review Queue)",
                    "description": "User indicates the resolved intent was wrong",
                    "value": {
                        "original_input": "I need dough quick",
                        "resolved_intent": "withdraw_cash",
                        "was_correct": False,
                        "confidence_when_resolved": 0.65,
                        "correct_intent": "borrow_money",
                        "notes": "Should have resolved to loan request, not cash withdrawal"
                    }
                }
            ]
        }
    )

    original_input: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="**The original user input** that was resolved",
        json_schema_extra={"example": "Transfer 500 to John"}
    )

    resolved_intent: str = Field(
        ...,
        description="**The intent the engine resolved to.** Used to update memory/review queue.",
        json_schema_extra={"example": "transfer_to_account"}
    )

    was_correct: bool = Field(
        ...,
        description="**Whether the resolution was correct.** True → Save to ChromaDB (Golden Record). False → Log to SQL Review Queue.",
        json_schema_extra={"example": True}
    )

    confidence_when_resolved: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="**Engine confidence when this intent was resolved.** Used for precision/recall tracking.",
        json_schema_extra={"example": 0.94}
    )

    correct_intent: Optional[str] = Field(
        default=None,
        description="**If was_correct=False, the actual correct intent.** Helps with training data correction.",
        json_schema_extra={"example": "loan_request"}
    )

    notes: Optional[str] = Field(
        default=None,
        max_length=500,
        description="**Optional notes from user.** Useful for understanding why feedback was given.",
        json_schema_extra={"example": "Should have resolved to loan request, not cash withdrawal"}
    )


class FeedbackResponse(BaseModel):
    """
    **Real-Time Learning Feedback Response**
    
    Confirmation that feedback was processed and learning occurred.
    """

    success: bool = Field(
        ...,
        description="**Whether feedback was successfully processed.**",
        json_schema_extra={"example": True}
    )

    action_taken: str = Field(
        ...,
        description="**Action taken based on feedback.** One of: 'saved_to_memory' (was_correct=True) or 'queued_for_review' (was_correct=False).",
        json_schema_extra={"example": "saved_to_memory"}
    )

    memory_id: Optional[str] = Field(
        default=None,
        description="**If was_correct=True, the ID of the saved memory record.** Can be used to track or recall this feedback.",
        json_schema_extra={"example": "transfer_to_account_1705502415123"}
    )

    review_queue_id: Optional[str] = Field(
        default=None,
        description="**If was_correct=False, the ID of the queued review item.** Useful for following up on manual corrections.",
        json_schema_extra={"example": "review_20260117_001"}
    )

    message: str = Field(
        ...,
        description="**Human-readable confirmation message.**",
        json_schema_extra={"example": "Feedback saved to Fast Memory as Golden Record. Engine will use this for future disambiguation."}
    )

    learning_status: Dict[str, Any] = Field(
        ...,
        description="**Current learning statistics.** Includes memory count, success rate, etc.",
        json_schema_extra={
            "example": {
                "total_feedbacks": 42,
                "correct_feedbacks": 38,
                "incorrect_feedbacks": 4,
                "accuracy_improvement": "90.5%",
                "last_update": "2026-01-17T14:30:15Z"
            }
        }
    )


class ReinforcementFeedbackRequest(BaseModel):
    """
    **Simplified Reinforcement Feedback for Fast Learning Loop**
    
    Minimal data model for rapid feedback submission. Links feedback to original
    resolution request and indicates whether correction was needed.
    
    **Use Cases:**
    - Fast user feedback during interactions
    - Mobile app feedback submission (bandwidth-constrained)
    - Real-time learning loops
    - A/B testing and experimentation
    
    **Workflow:**
    1. Engine resolves intent → Returns request_id
    2. User provides feedback with request_id + correction
    3. Engine learns and improves future resolutions
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "summary": "Positive Feedback",
                    "description": "User confirms resolution was correct",
                    "value": {
                        "request_id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_correction": "transfer_to_account",
                        "was_successful": True
                    }
                },
                {
                    "summary": "Negative Feedback with Correction",
                    "description": "User indicates wrong resolution and provides correction",
                    "value": {
                        "request_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                        "user_correction": "borrow_money",
                        "was_successful": False
                    }
                }
            ]
        }
    )
    
    request_id: str = Field(
        ...,
        description="**UUID linking to original intent resolution request.** Enables tracking and learning.",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"}
    )
    
    user_correction: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="**Correct intent ID or description.** Used if resolution was incorrect, or confirmed intent if correct.",
        json_schema_extra={"example": "transfer_to_account"}
    )
    
    was_successful: bool = Field(
        ...,
        description="**Whether the original resolution was correct.** True → Strengthen pattern. False → Review and correct.",
        json_schema_extra={"example": False}
    )


class ReinforcementFeedbackResponse(BaseModel):
    """
    **Reinforcement Feedback Processing Confirmation**
    
    Confirms that feedback was received, processed, and engine learning updated.
    """
    
    success: bool = Field(
        ...,
        description="Whether feedback was successfully processed",
        json_schema_extra={"example": True}
    )
    
    request_id: str = Field(
        ...,
        description="Echo of the request_id for tracking",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"}
    )
    
    feedback_type: str = Field(
        default="reinforcement",
        description="Type of feedback submitted",
        json_schema_extra={"example": "reinforcement"}
    )
    
    action_taken: str = Field(
        ...,
        description="Action taken: 'logged_for_learning' (successful) or 'queued_for_review' (needs correction)",
        json_schema_extra={"example": "queued_for_review"}
    )
    
    user_correction: str = Field(
        ...,
        description="Confirmed or corrected intent",
        json_schema_extra={"example": "borrow_money"}
    )
    
    message: str = Field(
        ...,
        description="Human-readable confirmation message",
        json_schema_extra={"example": "✓ Feedback received and processed. Engine will review this pattern."}
    )
    
    learning_status: Dict[str, Any] = Field(
        ...,
        description="Current learning statistics",
        json_schema_extra={
            "example": {
                "total_feedbacks": 127,
                "correct_feedbacks": 112,
                "incorrect_feedbacks": 15,
                "last_update": "2026-01-18T10:30:45Z"
            }
        }
    )
    
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp of feedback processing",
        json_schema_extra={"example": "2026-01-18T10:30:45Z"}
    )
