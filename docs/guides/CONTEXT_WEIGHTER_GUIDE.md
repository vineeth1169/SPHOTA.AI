"""
CONTEXT WEIGHTER - USAGE GUIDE

The ContextWeighter implements a comprehensive 12-factor weighting system
for intent confidence scoring in the Sphota engine.

This guide explains how to use, integrate, and customize the weighter.
"""

# ============================================================================
# QUICK START
# ============================================================================

from core.context_weighter import ContextWeighter

# Create a weighter instance
weighter = ContextWeighter()

# Define an intent
intent = {
    'id': 'lights_on',
    'action': 'turn_on',
    'type': 'command',
    'tags': ['lights', 'home'],
    'goal_alignment': 'home_control',
    'valid_screens': ['home', 'settings'],
    'formality': 'casual',
    'contains_slang': False,
    'required_location': 'home',
    'time_specific': '',
    'vocabulary_level': 'neutral'
}

# Define context
context = {
    'base_score': 0.85,  # Semantic similarity score from SBERT
    'user_history': ['lights', 'brightness', 'home'],
    'system_state': 'OFF',
    'active_goal': 'home_control',
    'current_screen': 'home',
    'syntax_flags': ['statement', 'imperative'],
    'social_mode': 'casual',
    'location': 'home',
    'time_of_day': 'evening',
    'user_profile': 'homeowner',
    'audio_features': {'pitch': 'flat', 'tone': 'relaxed'},
    'input_fidelity': 0.95
}

# Calculate final score
final_score = weighter.apply_weights(intent, context)
print(f"Final confidence: {final_score:.2f}")  # Output: 0.89+


# ============================================================================
# THE 12 FACTORS EXPLAINED
# ============================================================================

"""
FACTOR 1: ASSOCIATION (User History)
────────────────────────────────────

What it does:
  Checks if the current intent matches recent user command history.
  Recent user behavior is a strong predictor of future intent.

Logic:
  - Examines last 3 commands in user_history
  - If intent tags match any history item, boost by +0.15
  - Strongly reinforces repeated patterns

Example:
  User history: ['turn on lights', 'set brightness', 'adjust lighting']
  Intent: lights_on (tags: ['lights', 'home'])
  Result: +0.15 boost (user frequently interacts with lights)

Configuration:
  context['user_history'] = ['command1', 'command2', 'command3']
  intent['tags'] = ['tag1', 'tag2', 'tag3']


FACTOR 2: OPPOSITION (Conflict Detection)
──────────────────────────────────────────

What it does:
  Detects contradictions between the intent and current system state.
  Prevents meaningless commands (e.g., "Turn on" when already ON).

Logic:
  - Matches intent action (turn_on, turn_off, etc) vs system_state
  - If contradiction found, multiply score by 0.1 (severe penalty)
  - Prevents redundant/nonsensical commands

Example:
  System state: 'ON'
  Intent action: 'turn_on'
  Result: Score *= 0.1 (penalize - already on)

Configuration:
  context['system_state'] = 'ON' | 'OFF' | 'RUNNING' | etc
  intent['action'] = 'turn_on' | 'turn_off' | 'start' | etc


FACTOR 3: PURPOSE (Goal Alignment)
───────────────────────────────────

What it does:
  Aligns intent with the user's current high-level goal.
  Prioritizes intents that support ongoing tasks.

Logic:
  - Compares active_goal vs intent's goal_alignment
  - Exact match: +0.20 boost
  - Partial match: +0.10 boost
  - Supports multi-step task completion

Example:
  Active goal: 'booking_flight'
  Intent goal alignment: 'travel_booking'
  Result: +0.10 boost (partially supports goal)

Configuration:
  context['active_goal'] = 'goal_name'
  intent['goal_alignment'] = 'supporting_goal'


FACTOR 4: SITUATION (Screen State)
───────────────────────────────────

What it does:
  Validates that the intent is actionable on the current UI screen.
  Prevents impossible operations.

Logic:
  - Checks if current_screen is in valid_screens list
  - If valid: +0.15 boost
  - If invalid: -0.05 penalty (reduces confidence)

Example:
  Current screen: 'home'
  Valid screens for intent: ['home', 'settings']
  Result: +0.15 boost (intent actionable here)

Configuration:
  context['current_screen'] = 'screen_name'
  intent['valid_screens'] = ['screen1', 'screen2']


FACTOR 5: INDICATOR (Syntax Cues)
──────────────────────────────────

What it does:
  Matches syntax patterns with intent type.
  Questions should match query intents, commands should match actions.

Logic:
  - Analyzes syntax_flags (question, exclamation, statement)
  - Matches with intent type (query, command, statement)
  - Matching patterns: +0.08 boost

Example:
  Syntax flag: 'question'
  Intent type: 'query'
  Result: +0.08 boost (question matches query intent)

Configuration:
  context['syntax_flags'] = ['question', 'exclamation', 'statement']
  intent['type'] = 'query' | 'command' | 'statement'


FACTOR 6: WORD CAPACITY (Base Score)
─────────────────────────────────────

What it does:
  Incorporates the raw SBERT semantic similarity score.
  This is the foundation of all other adjustments.

Logic:
  - base_score already included in context
  - All factors adjust relative to this score
  - Bounds final result to [0.0, 1.0]

Note:
  You must provide the semantic similarity score in:
  context['base_score'] = <float 0.0-1.0>

Configuration:
  context['base_score'] = semantic_similarity_score


FACTOR 7: PROPRIETY (Social Mode)
──────────────────────────────────

What it does:
  Ensures communication matches the social context.
  Prevents inappropriate language in formal settings.

Logic:
  - Checks intent formality vs social_mode
  - If business mode + vulgar content: Score *= 0.0 (block)
  - If matching formality: Score *= 1.1 (small boost)
  - Handles register/tone consistency

Example:
  Social mode: 'business'
  Intent contains slang: True
  Result: Score *= 0.0 (completely blocked in business context)

Configuration:
  context['social_mode'] = 'business' | 'casual'
  intent['formality'] = 'formal' | 'casual' | 'neutral'
  intent['contains_slang'] = True | False


FACTOR 8: PLACE (Location Context)
────────────────────────────────────

What it does:
  Validates that the intent is relevant to the current location.
  Strong disambiguator (location changes meaning significantly).

Logic:
  - Matches required_location with current location
  - Exact match: +0.18 boost (highest single factor boost!)
  - Wrong location: -0.15 penalty
  - Unknown location: -0.05 penalty

Example:
  Current location: 'kitchen'
  Required location: 'kitchen'
  Result: +0.18 boost (intent makes sense in this location)

Configuration:
  context['location'] = 'location_name'
  intent['required_location'] = 'required_location'


FACTOR 9: TIME (Temporal Context)
──────────────────────────────────

What it does:
  Validates time-specific intents (e.g., "Good morning" only works at dawn).
  Prevents time-inappropriate commands.

Logic:
  - Checks if current time_of_day matches required time
  - Exact match: +0.15 boost
  - No time requirement: no change
  - Mismatch: -0.05 penalty

Example:
  Time of day: 'evening'
  Intent time specific: 'evening'
  Result: +0.15 boost (it's the right time for this intent)

Configuration:
  context['time_of_day'] = 'morning' | 'afternoon' | 'evening' | 'night'
  intent['time_specific'] = 'required_time_period'


FACTOR 10: INDIVIDUAL (User Profile)
──────────────────────────────────────

What it does:
  Personalizes based on user demographic and vocabulary level.
  Different age groups use different language styles.

Logic:
  - Matches user_profile with intent vocabulary_level
  - Exact match: +0.12 boost
  - Partial match: +0.06 boost
  - Neutral vocabulary: +0.06 (works for all profiles)

Example:
  User profile: 'gen_z'
  Intent vocabulary level: 'informal_modern'
  Result: +0.06 boost (partial match)

Configuration:
  context['user_profile'] = 'gen_z' | 'millennial' | 'professional'
  intent['vocabulary_level'] = 'formal' | 'casual' | 'neutral'


FACTOR 11: INTONATION (Audio Features)
───────────────────────────────────────

What it does:
  Analyzes voice characteristics to disambiguate intent type.
  Rising pitch suggests questions, flat pitch suggests statements.

Logic:
  - Analyzes pitch pattern from audio
  - Rising pitch (questions) matches query intents: +0.08
  - Flat pitch (statements) matches command intents: +0.08

Example:
  Audio pitch: 'rising'
  Intent type: 'query'
  Result: +0.08 boost (rising pitch = question)

Configuration:
  context['audio_features'] = {'pitch': 'rising' | 'flat', ...}
  intent['type'] = 'query' | 'command' | 'statement'


FACTOR 12: DISTORTION (Input Fidelity)
───────────────────────────────────────

What it does:
  Handles noisy/unclear input by triggering normalization.
  Gracefully degrades confidence when input quality is poor.

Logic:
  - Checks input_fidelity score (0.0 = completely noisy, 1.0 = perfect)
  - If fidelity < 0.5: triggers ApabhramsaLayer for normalization
  - Score *= (0.5 + input_fidelity)
  - Reduces confidence proportionally to noise level

Example:
  Input: "turn on da lights" (misspelled, speech noise)
  Input fidelity: 0.35
  Result: Score *= (0.5 + 0.35) = 0.85x reduction
  Also triggers normalization to map to correct intent

Configuration:
  context['input_fidelity'] = float between 0.0 and 1.0
  (Calculate from ASR confidence, spelling checks, etc)
"""


# ============================================================================
# INTEGRATION PATTERNS
# ============================================================================

"""
PATTERN 1: WITH PASYANTI ENGINE
────────────────────────────────

from core.pasyanti_engine import PasyantiEngine
from core.context_weighter import ContextWeighter

# Engine provides raw semantic scores
engine = PasyantiEngine()
results = engine.resolve_intent("user input", context)

# Weighter refines scores with 12 factors
weighter = ContextWeighter()
for result in results:
    intent_dict = {...}  # Prepare intent metadata
    context['base_score'] = result.raw_similarity
    final_score = weighter.apply_weights(intent_dict, context)


PATTERN 2: WITH CONTEXT MANAGER
────────────────────────────────

from core.context_manager import ContextManager
from core.context_weighter import ContextWeighter

manager = ContextManager()
context = manager.build_context(user_id, location, time, etc)

weighter = ContextWeighter()
final_score = weighter.apply_weights(intent, context)


PATTERN 3: WITH STREAMLIT APP
──────────────────────────────

# In sidebar, collect context
location = st.select_box("Location", ["Home", "Office"])
time = st.select_box("Time", ["Morning", "Evening"])

# Build context from selections
context = {
    'location': location.lower(),
    'time_of_day': time.lower(),
    'base_score': semantic_score,
    ...
}

weighter = ContextWeighter()
final_score = weighter.apply_weights(intent, context)

st.metric("Final Confidence", f"{final_score:.1%}")
"""


# ============================================================================
# CUSTOMIZATION
# ============================================================================

"""
ADJUST FACTOR WEIGHTS
─────────────────────

The default weights sum to 1.65 (normalized), but you can customize:

weighter = ContextWeighter()
weighter.factor_weights['association'] = 0.20  # Increase history importance
weighter.factor_weights['place'] = 0.25        # Increase location importance
weighter.factor_weights['time'] = 0.10         # Decrease time importance

# Now when you call apply_weights(), it uses your custom weights


CREATE CUSTOM WEIGHTING FACTORS
───────────────────────────────

Extend the ContextWeighter class:

class CustomWeighter(ContextWeighter):
    def _apply_custom_domain_factor(self, score, intent, context):
        '''Your custom business logic here'''
        if context.get('domain') == 'healthcare':
            if intent.get('contains_sensitive_info'):
                score *= 0.5
        return score
    
    def apply_weights(self, intent, context):
        score = super().apply_weights(intent, context)
        score = self._apply_custom_domain_factor(score, intent, context)
        return max(0.0, min(1.0, score))


DISABLE SPECIFIC FACTORS
────────────────────────

To disable a factor (set it to 0):

weighter.factor_weights['opposition'] = 0.0  # Disable conflict detection

To completely skip a factor in apply_weights(), modify the method:
# Comment out or remove the factor application line


DYNAMIC WEIGHT ADJUSTMENT
─────────────────────────

Adjust weights based on user or context:

def get_user_weights(user_profile):
    base_weights = ContextWeighter().factor_weights
    
    if user_profile == 'power_user':
        base_weights['association'] = 0.25  # Trust user history more
    elif user_profile == 'new_user':
        base_weights['association'] = 0.05  # Trust user history less
    
    return base_weights

weighter = ContextWeighter()
weighter.factor_weights = get_user_weights(user_profile)
"""


# ============================================================================
# DEBUGGING & ANALYSIS
# ============================================================================

"""
TRACE FACTOR CONTRIBUTIONS
──────────────────────────

To see how each factor affects the score:

class DebugWeighter(ContextWeighter):
    def apply_weights(self, intent, context):
        base_score = context.get('base_score', 0.5)
        score = base_score
        factors_applied = {}
        
        # Apply each factor and track changes
        before_assoc = score
        score = self._apply_association(score, intent, context)
        factors_applied['association'] = score - before_assoc
        
        before_opp = score
        score = self._apply_opposition(score, intent, context)
        factors_applied['opposition'] = score - before_opp
        
        # ... etc for all 12 factors
        
        # Print the breakdown
        for factor, change in factors_applied.items():
            print(f"  {factor}: {change:+.3f}")
        
        score = max(0.0, min(1.0, score))
        return score

# Usage
weighter = DebugWeighter()
final = weighter.apply_weights(intent, context)
# Prints which factors helped/hurt the score


COMPARE SCORES WITH/WITHOUT CONTEXT
────────────────────────────────────

context_empty = {'base_score': 0.75}
context_rich = {
    'base_score': 0.75,
    'user_history': ['lights'],
    'location': 'home',
    'active_goal': 'home_control',
    ...
}

weighter = ContextWeighter()

score_without = weighter.apply_weights(intent, context_empty)
score_with = weighter.apply_weights(intent, context_rich)

print(f"Without context: {score_without:.2f}")
print(f"With context: {score_with:.2f}")
print(f"Improvement: {score_with - score_without:+.2f}")
"""


# ============================================================================
# TESTING SCENARIOS
# ============================================================================

"""
TEST 1: Polysemic Disambiguation (The "Bank" Example)
──────────────────────────────────

Input: "Take me to the bank"
Base semantic score: 0.70 (ambiguous)

Scenario A: Nature/Fishing Context
──────────────────────────────────
context = {
    'base_score': 0.70,
    'location': 'nature_reserve',
    'user_history': ['fishing', 'outdoor'],
    'active_goal': 'outdoor_activity',
    'time_of_day': 'afternoon'
}

Expected: river_bank intent wins
Factors that help:
  - Place: +0.18 (nature_reserve matches river requirement)
  - Association: +0.15 (fishing in history)
  - Time: +0.15 (afternoon good for outdoor)

Scenario B: Urban/Finance Context
──────────────────────────────────
context = {
    'base_score': 0.70,
    'location': 'city_center',
    'user_history': ['transfer', 'balance'],
    'active_goal': 'financial_management',
    'current_screen': 'banking_app'
}

Expected: financial_bank intent wins
Factors that help:
  - Place: +0.18 (city_center matches financial requirement)
  - Association: +0.15 (banking in history)
  - Situation: +0.15 (banking_app is valid screen)


TEST 2: Invalid Commands (Opposition Factor)
──────────────────────────────────────────

Input: "Turn on the lights"
Current state: Already ON
Base score: 0.85

Expected: lights_on intent gets penalized
Factors:
  - Opposition: *= 0.1 (already on, pointless command)
  - Result: 0.85 * 0.1 = 0.085 (severe penalty)

This prevents nonsensical commands from winning.


TEST 3: Formal vs Casual (Propriety Factor)
────────────────────────────────────────────

Input: "Yo, turn off them lights"
Base score: 0.80
Contains slang: True

Scenario A: Casual Mode
──────────────────────
context['social_mode'] = 'casual'
Intent formality: 'casual'

Result: Score boosted (matches social context)

Scenario B: Business Mode
──────────────────────
context['social_mode'] = 'business'
Intent formality: 'casual'
Intent contains_slang: True

Result: Score *= 0.0 (blocked - inappropriate for business)
"""


# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

"""
1. CACHE INTENT METADATA
   - Load intent database once at startup
   - Don't reload for every scoring operation
   - Use in-memory dictionaries for O(1) lookups

2. BATCH CONTEXT PREPARATION
   - Build context once for the user session
   - Update only changed fields for new inputs
   - Avoid rebuilding entire context object each time

3. PROFILE COMMON PATHS
   - Most queries use 5-6 factors out of 12
   - Cache which factors apply to your use case
   - Skip unnecessary checks

4. PRE-COMPUTE USER PROFILES
   - Build user profile once during login
   - Update periodically (daily/weekly)
   - Improves vocabulary_level matching

5. USE EFFICIENT DATA STRUCTURES
   - Use lists for user_history (O(n) checks)
   - Use sets for tags (O(1) membership)
   - Use dicts for intent metadata (O(1) lookup)

Example optimization:
class OptimizedWeighter(ContextWeighter):
    def __init__(self):
        super().__init__()
        self.intent_cache = {}  # Cache intent metadata
        self.user_profile_cache = {}
    
    def apply_weights(self, intent, context):
        # Use cached metadata if available
        intent_id = intent['id']
        if intent_id not in self.intent_cache:
            self.intent_cache[intent_id] = intent
        
        cached_intent = self.intent_cache[intent_id]
        # ... rest of weighting with cached data
"""


print("""
╔════════════════════════════════════════════════════════════════╗
║         CONTEXT WEIGHTER - 12 FACTOR SYSTEM                    ║
║                                                                ║
║  1. Association (History)        7. Propriety (Social Mode)    ║
║  2. Opposition (Conflict)        8. Place (Location)           ║
║  3. Purpose (Goal)               9. Time (Temporal)            ║
║  4. Situation (Screen)          10. Individual (Profile)       ║
║  5. Indicator (Syntax)          11. Intonation (Audio)         ║
║  6. Word Capacity (Base)        12. Distortion (Fidelity)      ║
║                                                                ║
║  Maximum precision in intent resolution through               ║
║  comprehensive contextual analysis.                           ║
╚════════════════════════════════════════════════════════════════╝
""")
