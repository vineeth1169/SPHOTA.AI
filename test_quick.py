"""Quick validation script to test core imports"""
import sys
sys.path.insert(0, 'c:/Users/vinee/Sphota.AI')

print("Testing imports...")
from core.context_matrix import ContextResolutionMatrix, ContextObject
from core.apabhramsa_layer import ApabhramsaLayer

print("✓ Imports successful")

# Test CRM
crm = ContextResolutionMatrix()
print(f"✓ CRM initialized with {len(crm.weights)} factors")

# Test Apabhramsa
apabhramsa = ApabhramsaLayer()
normalized, score = apabhramsa.normalize_to_pure_form("yo wassup bruh")
print(f"✓ Apabhramsa normalization works: '{normalized}' (distortion: {score:.2f})")

# Test ContextObject
context = ContextObject(desa="kitchen", sahacarya=["cooking"])
active = crm.get_active_factors(context)
print(f"✓ ContextObject created with {len(active)} active factors: {active}")

print("\n✅ All core components working!")
