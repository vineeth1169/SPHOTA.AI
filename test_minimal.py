"""Minimal pytest test to verify framework works"""
import pytest
from core.context_matrix import ContextResolutionMatrix

def test_crm_initialization():
    """Test that CRM initializes with 12 factors"""
    crm = ContextResolutionMatrix()
    assert len(crm.weights) == 12, f"Expected 12 factors, got {len(crm.weights)}"
    assert "artha" in crm.weights
    assert "desa" in crm.weights
    print("✓ CRM test passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
