#!/usr/bin/env python
"""Quick validation of ContextManager and app integration."""

import sys
sys.path.insert(0, 'c:/Users/vinee/Sphota.AI')

print("\n" + "="*70)
print("TESTING CONTEXT MANAGER - 12 FACTOR MATRIX")
print("="*70)

# Test 1: ContextManager Import
print("\n[1] Testing ContextManager Import...")
try:
    from core.context_manager import ContextManager
    print("✓ ContextManager imported successfully")
except Exception as e:
    print(f"✗ Failed to import ContextManager: {e}")
    sys.exit(1)

# Test 2: ContextManager Initialization
print("\n[2] Testing ContextManager Initialization...")
try:
    mgr = ContextManager()
    assert len(mgr.get_command_history()) == 0
    print("✓ ContextManager initialized with empty history")
except Exception as e:
    print(f"✗ Initialization failed: {e}")
    sys.exit(1)

# Test 3: Basic Confidence Calculation
print("\n[3] Testing Basic Confidence Calculation...")
try:
    intent = {
        'type': 'test_action',
        'keywords': ['test'],
        'register': 'Neutral',
        'vocabulary_level': 'Neutral'
    }
    
    context = {
        'command_history': [],
        'system_state': 'OFF',
        'user_input': 'test',
        'current_task_id': None,
        'current_screen': None,
        'social_mode': 'Casual',
        'gps_tag': None,
        'current_hour': 12,
        'user_demographic': 'Millennial',
        'audio_pitch': 'Neutral',
        'input_confidence': 0.9
    }
    
    score = mgr.calculate_confidence(intent, context, 0.5)
    assert 0.0 <= score <= 1.0, f"Score out of bounds: {score}"
    print(f"✓ Basic confidence calculation works: score={score:.3f}")
except Exception as e:
    print(f"✗ Calculation failed: {e}")
    sys.exit(1)

# Test 4: Factor 1 - Sahacarya (Association History)
print("\n[4] Testing Factor 1: Sahacarya (Association History)...")
try:
    intent = {
        'type': 'booking',
        'keywords': ['flight', 'book'],
        'register': 'Neutral',
        'vocabulary_level': 'Casual'
    }
    
    context = {
        'command_history': ['search for flights', 'check travel dates'],
        'system_state': 'OFF',
        'user_input': 'book it',
        'current_task_id': None,
        'current_screen': None,
        'social_mode': 'Casual',
        'gps_tag': None,
        'current_hour': 12,
        'user_demographic': 'Millennial',
        'audio_pitch': 'Neutral',
        'input_confidence': 0.9
    }
    
    base_score = 0.5
    score = mgr.calculate_confidence(intent, context, base_score)
    boost = score - base_score
    
    # Should have +0.2 boost
    assert boost >= 0.19, f"Expected boost ~0.2, got {boost:.3f}"
    print(f"✓ Sahacarya boost applied: +{boost:.3f}")
except Exception as e:
    print(f"✗ Sahacarya test failed: {e}")
    sys.exit(1)

# Test 5: Factor 2 - Virodhitā (Conflict Check)
print("\n[5] Testing Factor 2: Virodhitā (Conflict Check)...")
try:
    intent = {
        'type': 'turn_on',
        'keywords': ['turn', 'on'],
        'register': 'Neutral',
        'vocabulary_level': 'Casual'
    }
    
    # Conflict: Already ON, trying to turn ON
    context = {
        'command_history': [],
        'system_state': 'ON',
        'user_input': 'turn on lights',
        'current_task_id': None,
        'current_screen': None,
        'social_mode': 'Casual',
        'gps_tag': None,
        'current_hour': 12,
        'user_demographic': 'Millennial',
        'audio_pitch': 'Neutral',
        'input_confidence': 0.9
    }
    
    score = mgr.calculate_confidence(intent, context, 0.8)
    
    # Should have 0.1x multiplier (severe penalty)
    assert score < 0.25, f"Expected severe penalty, got score {score:.3f}"
    print(f"✓ Virodhitā conflict penalty applied: score={score:.3f}")
except Exception as e:
    print(f"✗ Virodhitā test failed: {e}")
    sys.exit(1)

# Test 6: Factor 7 - Aucitī (Propriety)
print("\n[6] Testing Factor 7: Aucitī (Propriety)...")
try:
    intent = {
        'type': 'evaluation',
        'keywords': ['sick'],
        'register': 'Slang',
        'vocabulary_level': 'Casual'
    }
    
    # Business mode with slang - should penalize
    context = {
        'command_history': [],
        'system_state': 'OFF',
        'user_input': 'That\'s sick',
        'current_task_id': None,
        'current_screen': None,
        'social_mode': 'Business',
        'gps_tag': None,
        'current_hour': 12,
        'user_demographic': 'Professional',
        'audio_pitch': 'Neutral',
        'input_confidence': 0.9
    }
    
    score = mgr.calculate_confidence(intent, context, 0.7)
    
    # Should have 0.5x multiplier (50% penalty)
    assert score < 0.4, f"Expected slang penalty in business, got {score:.3f}"
    print(f"✓ Aucitī propriety penalty applied: score={score:.3f}")
except Exception as e:
    print(f"✗ Aucitī test failed: {e}")
    sys.exit(1)

# Test 7: Factor 8 - Deśa (Location)
print("\n[7] Testing Factor 8: Deśa (Location)...")
try:
    intent = {
        'type': 'reference',
        'keywords': ['bank'],
        'required_location': 'downtown business district',
        'register': 'Neutral',
        'vocabulary_level': 'Neutral'
    }
    
    context = {
        'command_history': ['Check account balance'],
        'system_state': 'OFF',
        'user_input': 'bank',
        'current_task_id': None,
        'current_screen': None,
        'social_mode': 'Business',
        'gps_tag': 'Downtown Business District',
        'current_hour': 12,
        'user_demographic': 'Professional',
        'audio_pitch': 'Neutral',
        'input_confidence': 0.9
    }
    
    score = mgr.calculate_confidence(intent, context, 0.5)
    boost = score - 0.5
    
    # Should have +0.2 boost
    assert boost >= 0.19, f"Expected location boost ~0.2, got {boost:.3f}"
    print(f"✓ Deśa location boost applied: +{boost:.3f}")
except Exception as e:
    print(f"✗ Deśa test failed: {e}")
    sys.exit(1)

# Test 8: Factor 11 - Svara (Intonation)
print("\n[8] Testing Factor 11: Svara (Intonation)...")
try:
    intent = {
        'type': 'alarm',
        'keywords': ['urgent'],
        'urgency': 'Urgent',
        'register': 'Neutral'
    }
    
    context = {
        'command_history': [],
        'system_state': 'OFF',
        'user_input': 'urgent!',
        'current_task_id': None,
        'current_screen': None,
        'social_mode': 'Casual',
        'gps_tag': None,
        'current_hour': 12,
        'user_demographic': 'Millennial',
        'audio_pitch': 'High',
        'input_confidence': 0.9
    }
    
    score = mgr.calculate_confidence(intent, context, 0.5)
    boost = score - 0.5
    
    # Should have +0.15 boost
    assert boost >= 0.14, f"Expected intonation boost ~0.15, got {boost:.3f}"
    print(f"✓ Svara intonation boost applied: +{boost:.3f}")
except Exception as e:
    print(f"✗ Svara test failed: {e}")
    sys.exit(1)

# Test 9: Factor 12 - Apabhraṃśa (Fidelity)
print("\n[9] Testing Factor 12: Apabhraṃśa (Fidelity)...")
try:
    intent = {
        'type': 'evaluation',
        'keywords': ['sick'],
        'register': 'Slang',
        'has_alternate_forms': True
    }
    
    # Low confidence with slang - should boost
    context = {
        'command_history': [],
        'system_state': 'OFF',
        'user_input': 'sick',
        'current_task_id': None,
        'current_screen': None,
        'social_mode': 'Casual',
        'gps_tag': None,
        'current_hour': 12,
        'user_demographic': 'Gen Z',
        'audio_pitch': 'Neutral',
        'input_confidence': 0.65
    }
    
    score = mgr.calculate_confidence(intent, context, 0.5)
    multiplier = score / 0.5
    
    # Should have ~1.15x multiplier
    assert multiplier >= 1.10, f"Expected fidelity boost ~1.15x, got {multiplier:.3f}x"
    print(f"✓ Apabhraṃśa fidelity boost applied: {multiplier:.3f}x")
except Exception as e:
    print(f"✗ Apabhraṃśa test failed: {e}")
    sys.exit(1)

# Test 10: Polysemic Disambiguation
print("\n[10] Testing Polysemic Disambiguation...")
try:
    # Test 'bank' disambiguation
    river_intent = {
        'type': 'noun_reference',
        'keywords': ['bank', 'river'],
        'required_location': 'riverside park',
        'register': 'Neutral',
        'vocabulary_level': 'Neutral'
    }
    
    financial_intent = {
        'type': 'noun_reference',
        'keywords': ['bank', 'finance'],
        'required_location': 'downtown business district',
        'register': 'Neutral',
        'vocabulary_level': 'Neutral'
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
    
    city_context = {
        'command_history': ['Check account balance'],
        'system_state': 'OFF',
        'user_input': 'bank',
        'current_task_id': None,
        'current_screen': None,
        'social_mode': 'Business',
        'gps_tag': 'Downtown Business District',
        'current_hour': 10,
        'user_demographic': 'Professional',
        'audio_pitch': 'Neutral',
        'input_confidence': 0.9
    }
    
    # In nature context, river should score higher
    river_score_nature = mgr.calculate_confidence(river_intent, nature_context, 0.5)
    financial_score_nature = mgr.calculate_confidence(financial_intent, nature_context, 0.5)
    
    assert river_score_nature > financial_score_nature, \
        f"River should score higher in nature: {river_score_nature:.3f} vs {financial_score_nature:.3f}"
    
    # In city context, financial should score higher
    river_score_city = mgr.calculate_confidence(river_intent, city_context, 0.5)
    financial_score_city = mgr.calculate_confidence(financial_intent, city_context, 0.5)
    
    assert financial_score_city > river_score_city, \
        f"Financial should score higher in city: {financial_score_city:.3f} vs {river_score_city:.3f}"
    
    print(f"✓ 'bank' polysemic disambiguation:")
    print(f"  - Nature context: river={river_score_nature:.3f} > financial={financial_score_nature:.3f}")
    print(f"  - City context: financial={financial_score_city:.3f} > river={river_score_city:.3f}")
except Exception as e:
    print(f"✗ Polysemic disambiguation failed: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("✓ ALL 12-FACTOR CONTEXT MANAGER TESTS PASSED!")
print("="*70 + "\n")
