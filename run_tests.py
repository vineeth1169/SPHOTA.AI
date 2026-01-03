"""
Quick test runner for Sphota AI test suite.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Verbose output
    python run_tests.py -k bank      # Run only "bank" tests
    python run_tests.py --markers    # List available markers

Note: This should be run with the venv Python:
    .venv/Scripts/python.exe run_tests.py
"""

import sys
import pytest

if __name__ == "__main__":
    # Default arguments
    args = ["tests/test_sphota.py", "-v", "--tb=short"]
    
    # Add user arguments if provided
    if len(sys.argv) > 1:
        if "--markers" in sys.argv:
            args = ["--markers"]
        else:
            args = ["tests/test_sphota.py"] + sys.argv[1:]
    
    # Run pytest
    print(f"Running pytest with Python: {sys.executable}")
    print(f"Arguments: {' '.join(args)}\n")
    exit_code = pytest.main(args)
    sys.exit(exit_code)
