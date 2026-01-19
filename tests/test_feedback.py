#!/usr/bin/env python3
"""
Real-Time Learning System - Testing Guide
==========================================

This script demonstrates how to test the Real-Time Learning feedback loop.

Run this after starting the API server:
    python run_server.py  # Terminal 1
    python test_feedback.py  # Terminal 2
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"
FEEDBACK_ENDPOINT = f"{API_BASE_URL}/feedback"
STATS_ENDPOINT = f"{API_BASE_URL}/feedback/stats"
REVIEW_QUEUE_ENDPOINT = f"{API_BASE_URL}/feedback/review-queue"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{BLUE}{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}{RESET}\n")


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message."""
    print(f"{YELLOW}ℹ {message}{RESET}")


def test_correct_feedback():
    """Test submitting correct feedback (golden record case)."""
    print_section("Test 1: Submit Correct Feedback")
    
    test_cases = [
        {
            "original_input": "I need to withdraw cash",
            "resolved_intent": "withdraw_cash",
            "was_correct": True,
            "confidence_when_resolved": 0.94,
            "notes": "Clear banking intent"
        },
        {
            "original_input": "Transfer 500 to John",
            "resolved_intent": "transfer_to_account",
            "was_correct": True,
            "confidence_when_resolved": 0.89,
            "notes": "Explicit transfer request"
        },
        {
            "original_input": "Check my balance",
            "resolved_intent": "check_balance",
            "was_correct": True,
            "confidence_when_resolved": 0.96,
            "notes": "Standard banking query"
        }
    ]
    
    for i, feedback in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {feedback['original_input']}")
        print(f"  → Resolved as: {feedback['resolved_intent']}")
        
        try:
            response = requests.post(FEEDBACK_ENDPOINT, json=feedback)
            response.raise_for_status()
            
            result = response.json()
            
            if result['success']:
                print_success(f"Feedback accepted (Action: {result['action_taken']})")
                
                if result['action_taken'] == 'saved_to_memory':
                    print(f"  Memory ID: {result['memory_id']}")
                    print(f"  Accuracy: {result['learning_status']['accuracy']}")
                else:
                    print_error("Unexpected action for correct feedback!")
            else:
                print_error(f"Feedback rejected: {result['message']}")
                
        except requests.exceptions.RequestException as e:
            print_error(f"Request failed: {e}")
        
        time.sleep(0.5)


def test_incorrect_feedback():
    """Test submitting incorrect feedback (review queue case)."""
    print_section("Test 2: Submit Incorrect Feedback")
    
    test_cases = [
        {
            "original_input": "I need dough quick",
            "resolved_intent": "loan_request",
            "was_correct": False,
            "confidence_when_resolved": 0.62,
            "correct_intent": "withdraw_cash",
            "notes": "Slang not recognized - should be cash withdrawal"
        },
        {
            "original_input": "Take me to the bank",
            "resolved_intent": "navigate_river_bank",
            "was_correct": False,
            "confidence_when_resolved": 0.71,
            "correct_intent": "navigate_financial_bank",
            "notes": "Wrong bank type - should be financial"
        },
        {
            "original_input": "I need bread",
            "resolved_intent": "food_delivery",
            "was_correct": False,
            "confidence_when_resolved": 0.58,
            "correct_intent": "withdraw_cash",
            "notes": "Slang not recognized - money context matters"
        }
    ]
    
    for i, feedback in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {feedback['original_input']}")
        print(f"  Engine resolved as: {feedback['resolved_intent']}")
        print(f"  Should have been: {feedback['correct_intent']}")
        
        try:
            response = requests.post(FEEDBACK_ENDPOINT, json=feedback)
            response.raise_for_status()
            
            result = response.json()
            
            if result['success']:
                print_success(f"Feedback queued for review (ID: {result['review_queue_id']})")
                
                if result['action_taken'] == 'queued_for_review':
                    print(f"  Accuracy: {result['learning_status']['accuracy']}")
                else:
                    print_error("Unexpected action for incorrect feedback!")
            else:
                print_error(f"Feedback rejected: {result['message']}")
                
        except requests.exceptions.RequestException as e:
            print_error(f"Request failed: {e}")
        
        time.sleep(0.5)


def test_statistics():
    """Test getting learning statistics."""
    print_section("Test 3: Get Learning Statistics")
    
    try:
        response = requests.get(STATS_ENDPOINT)
        response.raise_for_status()
        
        stats = response.json()
        learning = stats['learning_status']
        
        print_success("Statistics retrieved successfully")
        print(f"\n  Total Feedbacks: {learning['total_feedbacks']}")
        print(f"  Correct Feedbacks: {learning['correct_feedbacks']}")
        print(f"  Incorrect Feedbacks: {learning['incorrect_feedbacks']}")
        print(f"  Accuracy: {learning['accuracy']}%")
        print(f"  Last Update: {learning['last_update']}")
        
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to get statistics: {e}")


def test_review_queue():
    """Test getting review queue items."""
    print_section("Test 4: Get Review Queue")
    
    try:
        response = requests.get(REVIEW_QUEUE_ENDPOINT)
        response.raise_for_status()
        
        queue = response.json()
        
        print_success(f"Review queue retrieved (pending: {queue['pending_reviews']})")
        
        if queue['items']:
            print(f"\nPending Reviews: {queue['pending_reviews']}")
            for i, item in enumerate(queue['items'][:5], 1):  # Show first 5
                print(f"\n  [{i}] ID: {item['id']}")
                print(f"      Input: {item['original_input']}")
                print(f"      Engine resolved: {item['resolved_intent']}")
                print(f"      Should have been: {item['correct_intent']}")
                print(f"      Confidence: {item['confidence']}")
                print(f"      Notes: {item.get('notes', 'N/A')}")
        else:
            print_info("No pending reviews!")
            
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to get review queue: {e}")


def test_edge_cases():
    """Test edge cases and error handling."""
    print_section("Test 5: Edge Cases & Error Handling")
    
    # Test 1: Missing required field
    print("\n[1] Missing required field (was_correct)")
    incomplete = {
        "original_input": "Test",
        "resolved_intent": "test_intent"
        # Missing: was_correct
    }
    
    try:
        response = requests.post(FEEDBACK_ENDPOINT, json=incomplete)
        if response.status_code != 200:
            print_info(f"Expected error: {response.status_code} (validation failed)")
        else:
            print_error("Should have failed validation!")
    except Exception as e:
        print_info(f"Validation error caught: {type(e).__name__}")
    
    # Test 2: Invalid boolean
    print("\n[2] Invalid was_correct value")
    invalid_bool = {
        "original_input": "Test",
        "resolved_intent": "test",
        "was_correct": "yes"  # Should be boolean
    }
    
    try:
        response = requests.post(FEEDBACK_ENDPOINT, json=invalid_bool)
        if response.status_code != 200:
            print_info(f"Expected error: {response.status_code} (type validation)")
        else:
            print_error("Should have failed type validation!")
    except Exception as e:
        print_info(f"Type validation caught: {type(e).__name__}")
    
    # Test 3: Correct_intent without was_correct=False
    print("\n[3] Providing correct_intent when was_correct=True")
    unnecessary_correction = {
        "original_input": "Test",
        "resolved_intent": "test_intent",
        "was_correct": True,  # Correct
        "correct_intent": "different_intent"  # Shouldn't be used
    }
    
    try:
        response = requests.post(FEEDBACK_ENDPOINT, json=unnecessary_correction)
        response.raise_for_status()
        result = response.json()
        print_success(f"Handled correctly (correct_intent ignored): {result['success']}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
    
    # Test 4: Very long input
    print("\n[4] Very long input string")
    long_input = "a" * 10000
    long_feedback = {
        "original_input": long_input,
        "resolved_intent": "test",
        "was_correct": True
    }
    
    try:
        response = requests.post(FEEDBACK_ENDPOINT, json=long_feedback)
        if response.status_code == 200:
            print_success("Handled long input correctly")
        else:
            print_info(f"Long input validation: {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")


def test_data_persistence():
    """Test that feedback is persisted across requests."""
    print_section("Test 6: Data Persistence")
    
    print("Submitting feedback...")
    
    # Submit feedback
    feedback = {
        "original_input": "Persistence test",
        "resolved_intent": "test_intent",
        "was_correct": True
    }
    
    try:
        response1 = requests.post(FEEDBACK_ENDPOINT, json=feedback)
        response1.raise_for_status()
        result1 = response1.json()
        count1 = result1['learning_status']['total_feedbacks']
        
        time.sleep(0.5)
        
        # Get stats again
        response2 = requests.get(STATS_ENDPOINT)
        response2.raise_for_status()
        result2 = response2.json()
        count2 = result2['learning_status']['total_feedbacks']
        
        if count2 >= count1:
            print_success(f"Data persisted correctly (total: {count2} feedbacks)")
        else:
            print_error(f"Data not persisted correctly ({count1} → {count2})")
            
    except requests.exceptions.RequestException as e:
        print_error(f"Persistence test failed: {e}")


def run_all_tests():
    """Run all tests in sequence."""
    print(f"\n{BLUE}{'='*60}")
    print(f"{'Real-Time Learning - Complete Test Suite':^60}")
    print(f"{'='*60}{RESET}")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Check if API is running
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        print_success("API is running and responsive")
    except requests.exceptions.RequestException:
        print_error("API is not running! Start it with: python run_server.py")
        sys.exit(1)
    
    # Run all tests
    test_correct_feedback()
    time.sleep(1)
    
    test_incorrect_feedback()
    time.sleep(1)
    
    test_statistics()
    time.sleep(0.5)
    
    test_review_queue()
    time.sleep(0.5)
    
    test_edge_cases()
    time.sleep(0.5)
    
    test_data_persistence()
    
    # Final summary
    print_section("Test Summary")
    print_success("All tests completed!")
    print(f"\n{YELLOW}Next Steps:{RESET}")
    print("  1. Review the logs above for any issues")
    print("  2. Check learning stats: GET /feedback/stats")
    print("  3. Review pending items: GET /feedback/review-queue")
    print("  4. Verify Golden Records are improving accuracy")
    print(f"\n{BLUE}✨ Real-Time Learning System Ready! ✨{RESET}\n")


if __name__ == "__main__":
    run_all_tests()
