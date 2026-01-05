"""
Optional: Import Helper for ContextWeighter

Add this to core/__init__.py to make imports cleaner:

from core.context_weighter import ContextWeighter
from core.pasyanti_engine import PasyantiEngine
from core.context_matrix import ContextResolutionMatrix, ContextObject
from core.context_manager import ContextManager

Then use as:
    from core import ContextWeighter, PasyantiEngine
    weighter = ContextWeighter()
"""

# This file documents optional import setup

IMPORT_OPTIONS = {
    "Option 1 - Explicit": """
    from core.context_weighter import ContextWeighter
    weighter = ContextWeighter()
    """,
    
    "Option 2 - Via core module": """
    # Add to core/__init__.py:
    from core.context_weighter import ContextWeighter
    
    # Then use:
    from core import ContextWeighter
    weighter = ContextWeighter()
    """,
    
    "Option 3 - Full import": """
    from core.context_weighter import ContextWeighter
    from core.pasyanti_engine import PasyantiEngine
    from integration_example import IntegratedIntentResolver
    
    # Use both:
    engine = PasyantiEngine()
    weighter = ContextWeighter()
    # or
    resolver = IntegratedIntentResolver()
    """
}
