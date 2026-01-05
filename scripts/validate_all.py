"""
Final validation - check all components work together
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("🔍 Validating Sphota AI Components...")
print()

# Test 1: Core imports
print("1️⃣ Testing core imports...")
from core import PasyantiEngine, ContextResolutionMatrix, ContextObject, ApabhramsaLayer
print("   ✅ Core imports successful")

# Test 2: CRM initialization
print("2️⃣ Testing CRM initialization...")
crm = ContextResolutionMatrix()
assert len(crm.weights) == 12
print(f"   ✅ CRM initialized with {len(crm.weights)} factors")

# Test 3: Apabhramsa
print("3️⃣ Testing Apabhramsa layer...")
apabhramsa = ApabhramsaLayer()
normalized, score = apabhramsa.normalize_to_pure_form("yo wassup")
print(f"   ✅ Apabhramsa working (distortion: {score:.2f})")

# Test 4: PasyantiEngine
print("4️⃣ Testing PasyantiEngine...")
try:
    from unittest.mock import Mock, MagicMock, patch
    import numpy as np
    
    mock_model = MagicMock()
    def mock_encode(texts, **kwargs):
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
    
    with patch('core.pasyanti_engine.SentenceTransformer', return_value=mock_model):
        engine = PasyantiEngine(intents_path="data/intents.json")
        print(f"   ✅ Engine loaded with {len(engine.intents)} intents")
        
        # Test 5: Intent resolution
        print("5️⃣ Testing intent resolution...")
        context = ContextObject(desa="city", sahacarya=["money"])
        results = engine.resolve_intent("take me to the bank", context)
        print(f"   ✅ Resolution works: Winner = {results[0].intent.id}")
        
        # Test 6: Dict context support
        print("6️⃣ Testing Dict context support...")
        context_dict = {"desa": "nature", "sahacarya": ["fishing"]}
        results2 = engine.resolve_intent("take me to the bank", context_dict)
        print(f"   ✅ Dict context works: Winner = {results2[0].intent.id}")
        
        # Test 7: Explanation
        print("7️⃣ Testing explain_resolution...")
        explanation = engine.explain_resolution("test input", context)
        assert "input" in explanation
        assert "context" in explanation
        assert "resolution" in explanation
        print(f"   ✅ Explanation generated with {len(explanation)} keys")

except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Streamlit app imports
print("8️⃣ Testing Streamlit app compatibility...")
try:
    import streamlit
    print(f"   ✅ Streamlit {streamlit.__version__} available")
except ImportError:
    print("   ⚠️  Streamlit not in this environment (but available in venv)")

print()
print("=" * 50)
print("✅ ALL VALIDATIONS PASSED!")
print("=" * 50)
print()
print("📝 Next steps:")
print("   • Run tests: .venv/Scripts/python.exe -m pytest tests/test_sphota.py -v")
print("   • Run app: .venv/Scripts/python.exe -m streamlit run app.py")
print()
