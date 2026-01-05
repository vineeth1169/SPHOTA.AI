"""
Sphota - A Cognitive Meaning Engine

Based on Holistic Sentence View (Sentence Holism).

This package implements intent recognition through:
- Context Resolution Matrix (12 factors)
- Input normalization layer
- Flash insight recognition
"""

from .intent_engine import IntentEngine, Intent, ResolvedIntent
from .context_matrix import ContextResolutionMatrix, ContextObject
from .normalization_layer import NormalizationLayer
from .context_manager import ContextManager

__version__ = "1.0.0"
__author__ = "Sphota.AI"

__all__ = [
    "IntentEngine",
    "Intent",
    "ResolvedIntent",
    "ContextResolutionMatrix",
    "ContextObject",
    "NormalizationLayer",
    "ContextManager",
]
