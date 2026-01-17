#!/usr/bin/env python3
"""
Quick Test Script for Sphota FastAPI Microservice

This script demonstrates how to test the /resolve-intent endpoint
with various context scenarios.

Usage:
    python test_api.py

Requirements:
    pip install httpx
"""

import asyncio
import json
from datetime import datetime, timezone

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: pip install httpx")
    exit(1)


BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Test the /health endpoint."""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")


async def test_get_factors():
    """Test the /factors endpoint."""
    print("\n" + "="*70)
    print("TEST 2: Get Resolution Factors")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/factors")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Total Factors: {data['total_factors']}")
        print(f"Total Weight: {data['total_weight']}")
        print(f"\nFirst 3 Factors:")
        for i, (name, info) in enumerate(list(data['factors'].items())[:3]):
            print(f"  {i+1}. {name}: weight={info['weight']}")


async def test_resolve_intent_scenario_1():
    """
    Scenario 1: "Take me to the bank" in financial context
    Expected: navigate_to_financial_institution
    """
    print("\n" + "="*70)
    print("TEST 3: Resolve Intent - Financial Scenario")
    print("="*70)
    print("Input: 'take me to the bank'")
    print("Context: Manhattan, business hours, analyst user")
    print("-"*70)
    
    request_data = {
        "command_text": "take me to the bank",
        "context": {
            "location_context": "manhattan",
            "temporal_context": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "user_profile": "analyst",
            "association_history": ["viewed_portfolio", "paid_bill"],
            "goal_alignment": "finance"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/resolve-intent",
            json=request_data
        )
        
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"\nResolved Intent: {data['resolved_intent']}")
        print(f"Confidence: {data['confidence_score']:.1%}")
        print(f"Processing Time: {data['processing_time_ms']:.2f}ms")
        print(f"\nTop Contributing Factors:")
        for i, factor in enumerate(data['contributing_factors'][:3]):
            print(f"  {i+1}. {factor['factor_name']}: delta={factor['delta']:+.2f} ({factor['influence']})")
        
        if data.get('alternative_intents'):
            print(f"\nAlternative Intents:")
            for intent, score in list(data['alternative_intents'].items())[:2]:
                print(f"  - {intent}: {score:.1%}")


async def test_resolve_intent_scenario_2():
    """
    Scenario 2: "Take me to the bank" in outdoor context
    Expected: navigate_to_river_bank
    """
    print("\n" + "="*70)
    print("TEST 4: Resolve Intent - Outdoor Scenario")
    print("="*70)
    print("Input: 'take me to the bank'")
    print("Context: Nature, outdoor, fishing activity")
    print("-"*70)
    
    request_data = {
        "command_text": "take me to the bank",
        "context": {
            "location_context": "nature_reserve",
            "situation_context": "outdoor_hiking",
            "association_history": ["fishing", "outdoor_gear", "trail_maps"],
            "goal_alignment": "recreation",
            "input_fidelity": 0.95
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/resolve-intent",
            json=request_data
        )
        
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"\nResolved Intent: {data['resolved_intent']}")
        print(f"Confidence: {data['confidence_score']:.1%}")
        print(f"Processing Time: {data['processing_time_ms']:.2f}ms")
        print(f"\nTop Contributing Factors:")
        for i, factor in enumerate(data['contributing_factors'][:3]):
            print(f"  {i+1}. {factor['factor_name']}: delta={factor['delta']:+.2f} ({factor['influence']})")


async def test_resolve_intent_minimal():
    """
    Scenario 3: Minimal context (just command text)
    Expected: Baseline resolution without contextual boosts
    """
    print("\n" + "="*70)
    print("TEST 5: Resolve Intent - Minimal Context")
    print("="*70)
    print("Input: 'set a 5 minute timer'")
    print("Context: Empty (baseline)")
    print("-"*70)
    
    request_data = {
        "command_text": "set a 5 minute timer",
        "context": {}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/resolve-intent",
            json=request_data
        )
        
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"\nResolved Intent: {data['resolved_intent']}")
        print(f"Confidence: {data['confidence_score']:.1%}")
        print(f"Processing Time: {data['processing_time_ms']:.2f}ms")
        print(f"Active Factors: {len(data['audit_trail']['active_factors'])}")
        print(f"\nAll Scores:")
        for intent, score in data['audit_trail']['all_scores'].items():
            print(f"  {intent}: {score:.1%}")


async def test_error_handling():
    """
    Test error handling with invalid input
    """
    print("\n" + "="*70)
    print("TEST 6: Error Handling - Invalid Context")
    print("="*70)
    print("Input: Invalid semantic_capacity value (should be 0-1)")
    print("-"*70)
    
    request_data = {
        "command_text": "turn on the lights",
        "context": {
            "semantic_capacity": 1.5,  # Invalid: > 1.0
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/resolve-intent",
            json=request_data
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error Response:\n{json.dumps(response.json(), indent=2)}")
        else:
            print("✓ Request succeeded (validation passed)")


async def main():
    """Run all tests."""
    print("\n" + "█"*70)
    print("SPHOTA FASTAPI MICROSERVICE - TEST SUITE")
    print("█"*70)
    print(f"Base URL: {BASE_URL}")
    print("Make sure the server is running: uvicorn main:app --port 8000")
    
    try:
        # Test endpoint availability
        async with httpx.AsyncClient() as client:
            await client.get(f"{BASE_URL}/health", timeout=2.0)
    except Exception as e:
        print(f"\n✗ ERROR: Cannot connect to {BASE_URL}")
        print(f"  Make sure the server is running!")
        print(f"  Start it with: uvicorn main:app --port 8000")
        return
    
    print("\n✓ Server is running!\n")
    
    # Run tests
    await test_health_check()
    await test_get_factors()
    await test_resolve_intent_scenario_1()
    await test_resolve_intent_scenario_2()
    await test_resolve_intent_minimal()
    await test_error_handling()
    
    # Summary
    print("\n" + "█"*70)
    print("TEST SUITE COMPLETE")
    print("█"*70)
    print("\n✓ All tests executed successfully!")
    print("\nNext steps:")
    print("1. Review the output for correctness")
    print("2. Check http://localhost:8000/docs for interactive API testing")
    print("3. Review logs for performance metrics")
    print("4. Deploy to production when ready")


if __name__ == "__main__":
    asyncio.run(main())
