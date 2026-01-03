"""Test PasyantiEngine with mocked SentenceTransformer"""
import sys
from unittest.mock import Mock, MagicMock, patch
import numpy as np

sys.path.insert(0, 'c:/Users/vinee/Sphota.AI')

from core.pasyanti_engine import PasyantiEngine
from core.context_matrix import ContextObject

print("Testing PasyantiEngine with mock...")

# Create mock SentenceTransformer
mock_model = MagicMock()

def mock_encode(texts, **kwargs):
    """Generate fake embeddings"""
    if isinstance(texts, str):
        texts = [texts]
    
    embeddings = []
    for text in texts:
        seed = hash(text) % 10000
        np.random.seed(seed)
        embedding = np.random.randn(384)
        embedding = embedding / np.linalg.norm(embedding)
        embeddings.append(embedding)
    
    return np.array(embeddings)

mock_model.encode = Mock(side_effect=mock_encode)

# Patch and create engine
with patch('core.pasyanti_engine.SentenceTransformer', return_value=mock_model):
    engine = PasyantiEngine(intents_path="data/intents.json")
    print(f"✓ Engine initialized with {len(engine.intents)} intents")
    
    # Test resolve_intent with ContextObject
    user_input = "take me to the bank"
    context = ContextObject(desa="city", sahacarya=["money"])
    
    results = engine.resolve_intent(user_input, context)
    print(f"✓ resolve_intent works with ContextObject: {len(results)} results")
    print(f"  Winner: {results[0].intent.id} (score: {results[0].context_adjusted_score:.4f})")
    
    # Test with Dict context
    context_dict = {"desa": "nature", "sahacarya": ["fishing"]}
    results2 = engine.resolve_intent(user_input, context_dict)
    print(f"✓ resolve_intent works with Dict: {len(results2)} results")
    print(f"  Winner: {results2[0].intent.id} (score: {results2[0].context_adjusted_score:.4f})")
    
    # Test explain_resolution
    explanation = engine.explain_resolution(user_input, context)
    print(f"✓ explain_resolution works: {len(explanation)} keys")

print("\n✅ PasyantiEngine working with mocks!")
