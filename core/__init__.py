"""
Sphota - A Cognitive Meaning Engine

Based on Bhartṛhari's Akhaṇḍapakṣa (Sentence Holism).

This package implements intent recognition through:
- Context Resolution Matrix (12 factors)
- Apabhraṃśa normalization
- Paśyantī (flash of insight) recognition
"""

from .pasyanti_engine import PasyantiEngine, Intent, ResolvedIntent
from .context_matrix import ContextResolutionMatrix, ContextObject
from .apabhramsa_layer import ApabhramsaLayer

__version__ = "1.0.0"
__author__ = "Sphota.AI"

__all__ = [
    "PasyantiEngine",
    "Intent",
    "ResolvedIntent",
    "ContextResolutionMatrix",
    "ContextObject",
    "ApabhramsaLayer",
]
