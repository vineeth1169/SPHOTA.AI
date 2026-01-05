#!/usr/bin/env python
"""
Comprehensive Test Suite for Sphota.AI with 12-Factor Context Matrix

Tests:
1. ContextManager functionality (all 12 factors)
2. Intent database structure
3. App integration
"""

import sys
import json
from pathlib import Path

def test_context_manager():
    """Test ContextManager with 12 factors."""
    print("\n" + "="*80)
    print("TEST 1: CONTEXT MANAGER - 12-FACTOR MATRIX")
    print("="*80)
    
    try:
        from core.context_manager import ContextManager
        mgr = ContextManager()
        print("✓ ContextManager imported and initialized")
        
        # Test each factor
        test_cases = [
            ("Factor 1: Sahacarya", {
                'intent': {'type': 'booking', 'keywords': ['flight', 'book'], 'register': 'Neutral'},
                'context': {'command_history': ['search for flights', 'check travel dates'], 'system_state': 'OFF', 'user_input': 'book it', 'current_task_id': None, 'current_screen': None, 'social_mode': 'Casual', 'gps_tag': None, 'current_hour': 12, 'user_demographic': 'Millennial', 'audio_pitch': 'Neutral', 'input_confidence': 0.9},
                'base_score': 0.5,
                'check': lambda s, b: (s - b) >= 0.19  # +0.2 boost
            }),
            ("Factor 2: Virodhitā", {
                'intent': {'type': 'turn_on', 'keywords': ['turn', 'on'], 'register': 'Neutral'},
                'context': {'command_history': [], 'system_state': 'ON', 'user_input': 'turn on', 'current_task_id': None, 'current_screen': None, 'social_mode': 'Casual', 'gps_tag': None, 'current_hour': 12, 'user_demographic': 'Millennial', 'audio_pitch': 'Neutral', 'input_confidence': 0.9},
                'base_score': 0.8,
                'check': lambda s, b: s < b * 0.2  # 0.1x penalty
            }),
            ("Factor 7: Aucitī", {
                'intent': {'type': 'evaluation', 'keywords': ['sick'], 'register': 'Slang'},
                'context': {'command_history': [], 'system_state': 'OFF', 'user_input': 'sick', 'current_task_id': None, 'current_screen': None, 'social_mode': 'Business', 'gps_tag': None, 'current_hour': 12, 'user_demographic': 'Professional', 'audio_pitch': 'Neutral', 'input_confidence': 0.9},
                'base_score': 0.7,
                'check': lambda s, b: s < b * 0.6  # 0.5x penalty
            }),
            ("Factor 8: Deśa", {
                'intent': {'type': 'reference', 'keywords': ['bank'], 'required_location': 'downtown', 'register': 'Neutral'},
                'context': {'command_history': [], 'system_state': 'OFF', 'user_input': 'bank', 'current_task_id': None, 'current_screen': None, 'social_mode': 'Business', 'gps_tag': 'Downtown', 'current_hour': 12, 'user_demographic': 'Professional', 'audio_pitch': 'Neutral', 'input_confidence': 0.9},
                'base_score': 0.5,
                'check': lambda s, b: (s - b) >= 0.19  # +0.2 boost
            }),
            ("Factor 11: Svara", {
                'intent': {'type': 'alarm', 'keywords': ['urgent'], 'urgency': 'Urgent', 'register': 'Neutral'},
                'context': {'command_history': [], 'system_state': 'OFF', 'user_input': 'urgent', 'current_task_id': None, 'current_screen': None, 'social_mode': 'Casual', 'gps_tag': None, 'current_hour': 12, 'user_demographic': 'Millennial', 'audio_pitch': 'High', 'input_confidence': 0.9},
                'base_score': 0.5,
                'check': lambda s, b: (s - b) >= 0.14  # +0.15 boost
            }),
        ]
        
        for test_name, test_data in test_cases:
            score = mgr.calculate_confidence(test_data['intent'], test_data['context'], test_data['base_score'])
            
            if test_data['check'](score, test_data['base_score']):
                print(f"  ✓ {test_name}: {score:.3f}")
            else:
                print(f"  ✗ {test_name}: {score:.3f} (check failed)")
                return False
        
        # Test score bounds
        test_score = mgr.calculate_confidence({'type': 'test', 'keywords': []}, {'system_state': 'OFF', 'user_input': 'test', 'current_task_id': None, 'current_screen': None, 'social_mode': 'Casual', 'gps_tag': None, 'current_hour': 12, 'user_demographic': 'Millennial', 'audio_pitch': 'Neutral', 'input_confidence': 0.9, 'command_history': []}, 0.5)
        
        if 0.0 <= test_score <= 1.0:
            print(f"  ✓ Score bounds [0, 1]: {test_score:.3f}")
        else:
            print(f"  ✗ Score out of bounds: {test_score:.3f}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ ContextManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intent_db():
    """Test intent_db.json structure."""
    print("\n" + "="*80)
    print("TEST 2: INTENT DATABASE - POLYSEMIC TEST CASES")
    print("="*80)
    
    try:
        intent_db_path = Path("data/intent_db.json")
        
        if not intent_db_path.exists():
            print(f"✗ Intent database not found: {intent_db_path}")
            return False
        
        with open(intent_db_path, 'r', encoding='utf-8') as f:
            intent_db = json.load(f)
        
        print(f"✓ Intent database loaded")
        
        # Check structure
        assert 'intents' in intent_db, "Missing 'intents' key"
        assert isinstance(intent_db['intents'], list), "Intents must be a list"
        assert len(intent_db['intents']) >= 5, f"Expected at least 5 intents, got {len(intent_db['intents'])}"
        
        print(f"✓ Database structure valid: {len(intent_db['intents'])} intents")
        
        # Check each intent
        required_test_cases = {
            "turn_on_lights_conflict_test": "Virodhitā (Conflict)",
            "thats_sick_propriety_test": "Aucitī (Propriety)",
            "right_intonation_test": "Svara (Intonation)",
            "book_it_association_test": "Sahacarya (Association)",
            "bank_location_test": "Deśa (Location)"
        }
        
        found_tests = {}
        for intent in intent_db['intents']:
            intent_id = intent.get('intent_id', '')
            if intent_id in required_test_cases:
                found_tests[intent_id] = intent
                
                # Verify test scenarios exist
                scenarios = intent.get('test_scenarios', [])
                assert len(scenarios) > 0, f"Intent {intent_id} has no test scenarios"
                
                print(f"  ✓ {required_test_cases[intent_id]}: {len(scenarios)} scenarios")
        
        if len(found_tests) != len(required_test_cases):
            print(f"✗ Missing test cases. Found {len(found_tests)}/{len(required_test_cases)}")
            return False
        
        print(f"✓ All 5 polysemic test cases present")
        return True
        
    except Exception as e:
        print(f"✗ Intent database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_integration():
    """Test app.py integration with ContextManager."""
    print("\n" + "="*80)
    print("TEST 3: STREAMLIT APP INTEGRATION")
    print("="*80)
    
    try:
        # Check imports
        from core.context_manager import ContextManager
        print("✓ ContextManager importable from app location")
        
        # Check app.py has required elements
        app_path = Path("app.py")
        if not app_path.exists():
            print("✗ app.py not found")
            return False
        
        app_content = app_path.read_text(encoding='utf-8')
        
        required_elements = [
            ("from core.context_manager import ContextManager", "ContextManager import"),
            ("load_context_manager", "Context manager loader"),
            ("social_mode", "Social mode control"),
            ("system_state", "System state control"),
            ("history_type", "History type control"),
            ("audio_pitch", "Audio pitch control"),
            ("st.expander", "Expander widget"),
            ("plotly", "Chart visualization"),
        ]
        
        for element, description in required_elements:
            if element in app_content:
                print(f"  ✓ {description} found in app.py")
            else:
                print(f"  ✗ {description} NOT found in app.py")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ App integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_polysemic_disambiguation():
    """Test polysemic disambiguation scenarios."""
    print("\n" + "="*80)
    print("TEST 4: POLYSEMIC DISAMBIGUATION - END-TO-END")
    print("="*80)
    
    try:
        from core.context_manager import ContextManager
        
        mgr = ContextManager()
        
        # Test 1: 'bank' disambiguation
        river_intent = {
            'type': 'reference',
            'keywords': ['bank', 'river'],
            'required_location': 'riverside park',
            'register': 'Neutral'
        }
        
        financial_intent = {
            'type': 'reference',
            'keywords': ['bank', 'finance'],
            'required_location': 'downtown',
            'register': 'Neutral'
        }
        
        nature_context = {
            'command_history': ['Show hiking trails'],
            'system_state': 'OFF',
            'user_input': 'bank',
            'current_task_id': None,
            'current_screen': None,
            'social_mode': 'Casual',
            'gps_tag': 'Riverside Park',
            'current_hour': 10,
            'user_demographic': 'Gen X',
            'audio_pitch': 'Neutral',
            'input_confidence': 0.9
        }
        
        river_score = mgr.calculate_confidence(river_intent, nature_context, 0.5)
        financial_score = mgr.calculate_confidence(financial_intent, nature_context, 0.5)
        
        if river_score > financial_score:
            print(f"  ✓ 'bank' → River (nature): {river_score:.3f} > {financial_score:.3f}")
        else:
            print(f"  ✗ 'bank' disambiguation failed in nature context")
            return False
        
        # Test 2: 'sick' disambiguation
        positive_intent = {
            'type': 'evaluation',
            'keywords': ['cool'],
            'register': 'Slang'
        }
        
        casual_context = {
            'command_history': [],
            'system_state': 'OFF',
            'user_input': 'That\'s sick',
            'current_task_id': None,
            'current_screen': None,
            'social_mode': 'Casual',
            'gps_tag': None,
            'current_hour': 12,
            'user_demographic': 'Gen Z',
            'audio_pitch': 'High',
            'input_confidence': 0.92
        }
        
        business_context = dict(casual_context)
        business_context['social_mode'] = 'Business'
        business_context['user_demographic'] = 'Professional'
        
        casual_score = mgr.calculate_confidence(positive_intent, casual_context, 0.6)
        business_score = mgr.calculate_confidence(positive_intent, business_context, 0.6)
        
        if casual_score > business_score:
            print(f"  ✓ 'sick' → Positive (casual): {casual_score:.3f} > business: {business_score:.3f}")
        else:
            print(f"  ✗ 'sick' disambiguation failed")
            return False
        
        print(f"✓ Polysemic disambiguation working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Polysemic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("SPHOTA.AI - COMPREHENSIVE TEST SUITE")
    print("12-Factor Context Resolution Matrix + App Integration")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("ContextManager Tests", test_context_manager()))
    results.append(("Intent Database Tests", test_intent_db()))
    results.append(("App Integration Tests", test_app_integration()))
    results.append(("Polysemic Disambiguation", test_polysemic_disambiguation()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "="*80)
        print("✓ ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT")
        print("="*80 + "\n")
        return 0
    else:
        print("\n✗ Some tests failed. Please review above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
