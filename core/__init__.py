"""
Sphota SDK - Enterprise-Grade Intent Recognition Engine

A production-ready Python SDK for context-aware intent disambiguation
using Domain-Driven Design principles and advanced NLP techniques.

Core Components:
  - ContextResolutionEngine: 12-factor context resolution system
  - IntentEngine: Intent matching and ranking
  - NormalizationLayer: Input preprocessing and normalization
  - ContextManager: State management for continuous resolution

Quick Start:
    from sphota.core import SphotaEngine
    
    engine = SphotaEngine()
    result = engine.resolve("set timer 5 minutes", context)
"""

# Production API
from .context_engine import (
    ContextResolutionEngine,
    ContextSnapshot,
    ResolutionResult,
    TimeOfDay
)
from .intent_engine import IntentEngine, Intent, ResolvedIntent
from .normalization_layer import NormalizationLayer
from .context_manager import ContextManager

# Legacy compatibility (deprecated - use new names)
from .context_matrix import ContextResolutionMatrix, ContextObject

__version__ = "2.0.0"
__author__ = "Sphota.AI"
__license__ = "MIT"

# Main SDK entry point
class SphotaEngine:
    """
    Main entry point for the Sphota Intent Recognition SDK.
    
    Combines context resolution, intent matching, and normalization
    into a unified production-ready engine.
    """
    
    def __init__(self, weights: dict = None):
        """Initialize Sphota Engine with optional custom weights."""
        self.context_engine = ContextResolutionEngine(weights=weights)
        self.intent_engine = IntentEngine()
        self.normalizer = NormalizationLayer()
        self.context_manager = ContextManager()
    
    def resolve(self, user_input: str, context: ContextSnapshot = None):
        """
        Resolve user intent with full context resolution pipeline.
        
        Args:
            user_input: Raw user input string
            context: Optional context snapshot for resolution
            
        Returns:
            Resolved intent with confidence scores
        """
        # Normalize input
        normalized = self.normalizer.normalize(user_input)
        
        # Match intents
        base_scores = self.intent_engine.match(normalized)
        
        # Apply context resolution
        if context is None:
            context = ContextSnapshot()
        
        resolution = self.context_engine.resolve(base_scores, context)
        return resolution


__all__ = [
    # Production API
    "SphotaEngine",
    "ContextResolutionEngine",
    "ContextSnapshot",
    "ResolutionResult",
    "TimeOfDay",
    "IntentEngine",
    "Intent",
    "ResolvedIntent",
    "NormalizationLayer",
    "ContextManager",
    
    # Legacy (deprecated)
    "ContextResolutionMatrix",
    "ContextObject",
]

