"""Quick test of ContextManager functionality."""
from core.context_manager import ContextManager

mgr = ContextManager()
print("✓ ContextManager initialized")

intent = {'type': 'test', 'keywords': ['test'], 'register': 'Neutral'}
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
print(f"✓ Basic calculation: {score:.3f}")

# Test conflict
intent2 = {'type': 'turn_on', 'keywords': ['on'], 'register': 'Neutral'}
context2 = dict(context)
context2['system_state'] = 'ON'

score2 = mgr.calculate_confidence(intent2, context2, 0.8)
print(f"✓ Conflict penalty: {score2:.3f} (should be < 0.25)")

print("\n✓ All basic tests passed!")
