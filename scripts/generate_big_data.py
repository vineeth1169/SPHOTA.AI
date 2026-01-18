#!/usr/bin/env python3
"""
Generate 10,000 logically consistent test cases for 12-Factor Context Engine.

This script creates data/context_test_data_large.csv with realistic ambiguity
resolution scenarios. Each test case follows strict If-Then logic rules.

Usage:
    python scripts/generate_big_data.py

Output:
    - data/context_test_data_large.csv (10,000 rows)
    - Contains 8,000 normal cases + 2,000 hard edge cases
    - All columns follow strict deterministic logic
"""

import pandas as pd
import uuid
import random
from typing import Tuple, Dict
from dataclasses import dataclass
from pathlib import Path


# ============================================================================
# FACTOR VALUE DEFINITIONS (Strict English Terminology)
# ============================================================================

ASSOCIATIONS = [
    "travel_history", "dining_history", "shopping_history", 
    "home_automation", "work_related", "entertainment", "medical", "none"
]

CONFLICT_CHECKS = [
    "lights_already_on", "ac_already_cool", "door_already_locked",
    "no_conflict", "pending_action", "system_busy", "cache_hit"
]

ACTIVE_GOALS = [
    "book_travel", "order_food", "control_home", "work_task",
    "entertainment", "health_tracking", "social_interaction", "none"
]

SCREEN_STATES = [
    "on_home_screen", "on_map_app", "on_banking_app", "on_restaurant_app",
    "on_airline_app", "on_music_app", "on_weather_app", "locked_screen"
]

SYNTAX_FLAGS = [
    "imperative", "question", "statement", "exclamation",
    "command", "request", "query", "confirmation"
]

BASE_SCORES = [0.2, 0.4, 0.6, 0.8, 0.95]

SOCIAL_MODES = [
    "Business", "Casual", "Intimate", "Formal", "Neutral"
]

LOCATIONS = [
    "Home", "Office", "Car", "City_Center", "Nature/Wilderness",
    "Shopping_Mall", "Restaurant", "Airport", "Unknown"
]

TIME_OF_DAY = [
    "06:00", "08:00", "12:00", "15:00", "18:00", "21:00", "23:00", "02:00"
]

USER_PROFILES = [
    "Executive", "Gen_Z", "Millennial", "Busy_Parent", 
    "Tech_Savvy", "Tech_Novice", "Student", "Retiree"
]

INTONATIONS = [
    "Flat", "Rising", "Falling", "Questioning", "Emphatic", "Neutral"
]

FIDELITIES = [0.95, 0.85, 0.75, 0.5, 0.3]


# ============================================================================
# TEST INPUTS (Core scenarios)
# ============================================================================

TEST_INPUTS = {
    "book_it": "Book it",
    "turn_on_lights": "Turn on lights",
    "sick": "That's sick",
    "no_cap": "No cap",
    "go_bank": "Go to the bank",
    "good_morning": "Good morning",
    "right": "Right",
    "water": "Water",
    "confirm": "Confirm",
    "wake_up": "Wake me up",
    "set_alarm": "Set an alarm for 7 AM",
    "play_music": "Play music",
    "call_mom": "Call mom",
    "order_pizza": "Order pizza",
    "check_weather": "What's the weather",
}

SLANG_INPUTS = ["Wudder", "Wader", "Bet", "Fax", "Slay", "Bussin"]


# ============================================================================
# DETERMINISTIC SCENARIO LOGIC
# ============================================================================

@dataclass
class ContextFactors:
    """Container for all 12 context factors."""
    ctx_association: str
    ctx_conflict_check: str
    ctx_active_goal: str
    ctx_screen_state: str
    ctx_syntax_flag: str
    ctx_base_score: float
    ctx_social_mode: str
    ctx_location: str
    ctx_time_of_day: str
    ctx_user_profile: str
    ctx_intonation: str
    ctx_fidelity: float


def apply_scenario_rules(
    input_text: str,
    factors: ContextFactors,
) -> Tuple[str, str]:
    """
    Apply If-Then logic rules to determine intent resolution.
    
    Each rule explicitly handles a specific ambiguity case where context
    factors disambiguate between multiple valid interpretations.
    
    Returns:
        Tuple of (expected_intent, conflicting_intent)
    """
    
    # RULE 1: Factor 1 - Association (History/Sahacarya)
    if input_text == "Book it":
        if factors.ctx_association == "travel_history":
            return "book_flight", "reserve_table"
        elif factors.ctx_association == "dining_history":
            return "reserve_table", "book_flight"
        elif factors.ctx_association == "shopping_history":
            return "complete_purchase", "book_flight"
        else:
            return "booking_generic", "unknown_booking"
    
    # RULE 2: Factor 2 - Conflict Check (System State/Virodhitā)
    if input_text == "Turn on lights":
        if factors.ctx_conflict_check == "lights_already_on":
            return "error_redundant_command", "turn_on_lights"
        elif factors.ctx_conflict_check == "no_conflict":
            return "turn_on_lights", "error_redundant_command"
        else:
            return "turn_on_lights", "error_conflict"
    
    # RULE 3: Factor 7 - Social Mode (Propriety/Aucitī) - Slang Handling
    slang_expressions = ["That's sick", "No cap", "That's lit", "No way"]
    is_slang = any(slang in input_text for slang in slang_expressions)
    
    if is_slang:
        if factors.ctx_social_mode == "Business":
            return "flagged_unprofessional", "sentiment_positive"
        elif factors.ctx_social_mode == "Casual":
            return "sentiment_positive", "flagged_unprofessional"
        else:
            return "sentiment_contextual", "flagged_unprofessional"
    
    # RULE 4: Factor 8 - Location (Place/Deśa) - The "Bank" Problem
    if input_text == "Go to the bank":
        if factors.ctx_location == "Nature/Wilderness":
            return "navigate_river_bank", "navigate_financial_bank"
        elif factors.ctx_location == "City_Center":
            return "navigate_financial_bank", "navigate_river_bank"
        elif factors.ctx_location == "Home":
            return "navigate_financial_bank", "navigate_river_bank"
        else:
            return "navigate_bank_ambiguous", "navigate_unknown"
    
    # RULE 5: Factor 9 - Time of Day (Time/Kāla)
    if input_text == "Good morning":
        if factors.ctx_time_of_day in ["23:00", "02:00"]:
            return "greeting_correction", "greeting_appropriate"
        elif factors.ctx_time_of_day in ["06:00", "08:00"]:
            return "greeting_appropriate", "greeting_correction"
        else:
            return "greeting_contextual", "greeting_correction"
    
    # RULE 6: Factor 11 - Intonation (Intonation/Svara)
    if input_text == "Right":
        if factors.ctx_intonation == "Rising":
            return "confirm_query", "affirmation"
        elif factors.ctx_intonation == "Flat":
            return "affirmation", "confirm_query"
        elif factors.ctx_intonation == "Questioning":
            return "confirm_query", "affirmation"
        else:
            return "affirmation_neutral", "confirm_query"
    
    # RULE 7: Factor 12 - Fidelity + User Profile (Distortion/Apabhraṃśa)
    slang_map = {
        "Wudder": "water_command",
        "Wader": "water_command",
        "Bet": "confirm_action",
        "Fax": "confirm_action",
        "Slay": "sentiment_positive",
        "Bussin": "sentiment_positive"
    }
    
    if factors.ctx_fidelity < 0.5 or factors.ctx_user_profile == "Gen_Z":
        for slang_input, corrected_intent in slang_map.items():
            if slang_input.lower() in input_text.lower():
                return corrected_intent, "unrecognized_command"
    
    # DEFAULT: Generic intent resolution based on frequency
    default_intents = {
        "Wake me up": ("set_alarm", "wake_device"),
        "Set an alarm for 7 AM": ("set_alarm", "schedule_reminder"),
        "Play music": ("play_music", "play_audio"),
        "Call mom": ("make_call", "send_message"),
        "Order pizza": ("order_food", "search_restaurant"),
        "What's the weather": ("get_weather", "open_weather_app"),
    }
    
    if input_text in default_intents:
        return default_intents[input_text]
    
    return "generic_intent", "fallback_intent"


def generate_random_factors() -> ContextFactors:
    """Generate random context factors (baseline case)."""
    return ContextFactors(
        ctx_association=random.choice(ASSOCIATIONS),
        ctx_conflict_check=random.choice(CONFLICT_CHECKS),
        ctx_active_goal=random.choice(ACTIVE_GOALS),
        ctx_screen_state=random.choice(SCREEN_STATES),
        ctx_syntax_flag=random.choice(SYNTAX_FLAGS),
        ctx_base_score=round(random.choice(BASE_SCORES), 2),
        ctx_social_mode=random.choice(SOCIAL_MODES),
        ctx_location=random.choice(LOCATIONS),
        ctx_time_of_day=random.choice(TIME_OF_DAY),
        ctx_user_profile=random.choice(USER_PROFILES),
        ctx_intonation=random.choice(INTONATIONS),
        ctx_fidelity=round(random.choice(FIDELITIES), 2),
    )


def generate_edge_case() -> Tuple[str, ContextFactors]:
    """
    Generate an edge case that triggers one of the scenario rules.
    These are the "hard" disambiguation cases that test real ambiguity resolution.
    """
    edge_case_type = random.choice([
        "book_it_travel",
        "book_it_dining",
        "turn_on_lights",
        "slang_business",
        "slang_casual",
        "go_bank_nature",
        "go_bank_city",
        "good_morning_night",
        "good_morning_morning",
        "right_rising",
        "right_flat",
        "distortion_low_fidelity",
        "distortion_gen_z",
    ])
    
    if edge_case_type == "book_it_travel":
        factors = ContextFactors(
            ctx_association="travel_history",
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal="book_travel",
            ctx_screen_state=random.choice(SCREEN_STATES),
            ctx_syntax_flag="command",
            ctx_base_score=0.95,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location=random.choice(LOCATIONS),
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation=random.choice(INTONATIONS),
            ctx_fidelity=0.95,
        )
        return "Book it", factors
    
    elif edge_case_type == "book_it_dining":
        factors = ContextFactors(
            ctx_association="dining_history",
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state="on_restaurant_app",
            ctx_syntax_flag="command",
            ctx_base_score=0.95,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location="Restaurant",
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation=random.choice(INTONATIONS),
            ctx_fidelity=0.95,
        )
        return "Book it", factors
    
    elif edge_case_type == "turn_on_lights":
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check="lights_already_on",
            ctx_active_goal="control_home",
            ctx_screen_state=random.choice(SCREEN_STATES),
            ctx_syntax_flag="command",
            ctx_base_score=0.8,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location="Home",
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation="Emphatic",
            ctx_fidelity=0.95,
        )
        return "Turn on lights", factors
    
    elif edge_case_type == "slang_business":
        slang = random.choice(["That's sick", "No cap"])
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state="on_home_screen",
            ctx_syntax_flag="statement",
            ctx_base_score=0.7,
            ctx_social_mode="Business",
            ctx_location="Office",
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation=random.choice(INTONATIONS),
            ctx_fidelity=0.85,
        )
        return slang, factors
    
    elif edge_case_type == "slang_casual":
        slang = random.choice(["That's sick", "No cap"])
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state=random.choice(SCREEN_STATES),
            ctx_syntax_flag="statement",
            ctx_base_score=0.7,
            ctx_social_mode="Casual",
            ctx_location=random.choice(["Home", "Car"]),
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation=random.choice(INTONATIONS),
            ctx_fidelity=0.85,
        )
        return slang, factors
    
    elif edge_case_type == "go_bank_nature":
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state="on_map_app",
            ctx_syntax_flag="command",
            ctx_base_score=0.8,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location="Nature/Wilderness",
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation="Flat",
            ctx_fidelity=0.95,
        )
        return "Go to the bank", factors
    
    elif edge_case_type == "go_bank_city":
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state="on_banking_app",
            ctx_syntax_flag="command",
            ctx_base_score=0.8,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location="City_Center",
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation="Flat",
            ctx_fidelity=0.95,
        )
        return "Go to the bank", factors
    
    elif edge_case_type == "good_morning_night":
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state=random.choice(SCREEN_STATES),
            ctx_syntax_flag="greeting",
            ctx_base_score=0.6,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location=random.choice(LOCATIONS),
            ctx_time_of_day="23:00",
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation=random.choice(INTONATIONS),
            ctx_fidelity=0.95,
        )
        return "Good morning", factors
    
    elif edge_case_type == "good_morning_morning":
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state=random.choice(SCREEN_STATES),
            ctx_syntax_flag="greeting",
            ctx_base_score=0.6,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location=random.choice(LOCATIONS),
            ctx_time_of_day="06:00",
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation=random.choice(INTONATIONS),
            ctx_fidelity=0.95,
        )
        return "Good morning", factors
    
    elif edge_case_type == "right_rising":
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state=random.choice(SCREEN_STATES),
            ctx_syntax_flag="question",
            ctx_base_score=0.8,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location=random.choice(LOCATIONS),
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation="Rising",
            ctx_fidelity=0.95,
        )
        return "Right", factors
    
    elif edge_case_type == "right_flat":
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state=random.choice(SCREEN_STATES),
            ctx_syntax_flag="statement",
            ctx_base_score=0.8,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location=random.choice(LOCATIONS),
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation="Flat",
            ctx_fidelity=0.95,
        )
        return "Right", factors
    
    elif edge_case_type == "distortion_low_fidelity":
        slang = random.choice(["Wudder", "Bet", "Slay"])
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state=random.choice(SCREEN_STATES),
            ctx_syntax_flag=random.choice(SYNTAX_FLAGS),
            ctx_base_score=0.3,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location=random.choice(LOCATIONS),
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile=random.choice(USER_PROFILES),
            ctx_intonation=random.choice(INTONATIONS),
            ctx_fidelity=0.3,
        )
        return slang, factors
    
    else:  # distortion_gen_z
        slang = random.choice(["Wudder", "Bet", "Slay"])
        factors = ContextFactors(
            ctx_association=random.choice(ASSOCIATIONS),
            ctx_conflict_check=random.choice(CONFLICT_CHECKS),
            ctx_active_goal=random.choice(ACTIVE_GOALS),
            ctx_screen_state=random.choice(SCREEN_STATES),
            ctx_syntax_flag=random.choice(SYNTAX_FLAGS),
            ctx_base_score=0.8,
            ctx_social_mode=random.choice(SOCIAL_MODES),
            ctx_location=random.choice(LOCATIONS),
            ctx_time_of_day=random.choice(TIME_OF_DAY),
            ctx_user_profile="Gen_Z",
            ctx_intonation=random.choice(INTONATIONS),
            ctx_fidelity=0.7,
        )
        return slang, factors


def generate_dataset(num_rows: int = 10000, edge_case_ratio: float = 0.2) -> pd.DataFrame:
    """
    Generate the full test dataset with logical consistency.
    
    Args:
        num_rows: Total number of test cases (default 10,000)
        edge_case_ratio: Fraction of rows that should be edge cases (default 0.2 = 20%)
    
    Returns:
        DataFrame ready to be saved as CSV
    """
    num_edge_cases = int(num_rows * edge_case_ratio)
    num_normal_cases = num_rows - num_edge_cases
    
    rows = []
    
    print(f"\n🧮 Generating {num_normal_cases:,} normal test cases...")
    for i in range(num_normal_cases):
        if (i + 1) % 2000 == 0:
            print(f"   ✓ {i + 1:,}/{num_normal_cases:,} cases generated")
        
        input_text = random.choice(list(TEST_INPUTS.values()))
        factors = generate_random_factors()
        expected_intent, conflicting_intent = apply_scenario_rules(input_text, factors)
        
        row = {
            "id": str(uuid.uuid4()),
            "input_text": input_text,
            "expected_intent": expected_intent,
            "conflicting_intent": conflicting_intent,
            "ctx_association": factors.ctx_association,
            "ctx_conflict_check": factors.ctx_conflict_check,
            "ctx_active_goal": factors.ctx_active_goal,
            "ctx_screen_state": factors.ctx_screen_state,
            "ctx_syntax_flag": factors.ctx_syntax_flag,
            "ctx_base_score": factors.ctx_base_score,
            "ctx_social_mode": factors.ctx_social_mode,
            "ctx_location": factors.ctx_location,
            "ctx_time_of_day": factors.ctx_time_of_day,
            "ctx_user_profile": factors.ctx_user_profile,
            "ctx_intonation": factors.ctx_intonation,
            "ctx_fidelity": factors.ctx_fidelity,
        }
        rows.append(row)
    
    print(f"\n🔥 Generating {num_edge_cases:,} hard edge case scenarios...")
    for i in range(num_edge_cases):
        if (i + 1) % 500 == 0:
            print(f"   ✓ {i + 1:,}/{num_edge_cases:,} edge cases generated")
        
        input_text, factors = generate_edge_case()
        expected_intent, conflicting_intent = apply_scenario_rules(input_text, factors)
        
        row = {
            "id": str(uuid.uuid4()),
            "input_text": input_text,
            "expected_intent": expected_intent,
            "conflicting_intent": conflicting_intent,
            "ctx_association": factors.ctx_association,
            "ctx_conflict_check": factors.ctx_conflict_check,
            "ctx_active_goal": factors.ctx_active_goal,
            "ctx_screen_state": factors.ctx_screen_state,
            "ctx_syntax_flag": factors.ctx_syntax_flag,
            "ctx_base_score": factors.ctx_base_score,
            "ctx_social_mode": factors.ctx_social_mode,
            "ctx_location": factors.ctx_location,
            "ctx_time_of_day": factors.ctx_time_of_day,
            "ctx_user_profile": factors.ctx_user_profile,
            "ctx_intonation": factors.ctx_intonation,
            "ctx_fidelity": factors.ctx_fidelity,
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    return df


def print_statistics(df: pd.DataFrame) -> None:
    """Print comprehensive dataset statistics."""
    print("\n" + "="*80)
    print("📊 DATASET STATISTICS")
    print("="*80)
    print(f"\n✓ Total rows: {len(df):,}")
    print(f"✓ Unique input texts: {df['input_text'].nunique()}")
    print(f"✓ Unique expected intents: {df['expected_intent'].nunique()}")
    print(f"✓ Unique conflicting intents: {df['conflicting_intent'].nunique()}")
    
    print(f"\n📝 Input Text Distribution (Top 10):")
    for text, count in df['input_text'].value_counts().head(10).items():
        print(f"   - '{text}': {count:,} rows ({100*count/len(df):.1f}%)")
    
    print(f"\n🎯 Expected Intent Distribution (Top 15):")
    for intent, count in df['expected_intent'].value_counts().head(15).items():
        print(f"   - {intent}: {count:,} rows ({100*count/len(df):.1f}%)")
    
    print(f"\n🔍 Context Factor Coverage:")
    print(f"   - Associations: {df['ctx_association'].nunique()} unique values")
    print(f"   - Conflict checks: {df['ctx_conflict_check'].nunique()} unique values")
    print(f"   - Active goals: {df['ctx_active_goal'].nunique()} unique values")
    print(f"   - Screen states: {df['ctx_screen_state'].nunique()} unique values")
    print(f"   - Syntax flags: {df['ctx_syntax_flag'].nunique()} unique values")
    print(f"   - Base scores: {df['ctx_base_score'].nunique()} unique values")
    print(f"   - Social modes: {df['ctx_social_mode'].nunique()} unique values")
    print(f"   - Locations: {df['ctx_location'].nunique()} unique values")
    print(f"   - Times of day: {df['ctx_time_of_day'].nunique()} unique values")
    print(f"   - User profiles: {df['ctx_user_profile'].nunique()} unique values")
    print(f"   - Intonations: {df['ctx_intonation'].nunique()} unique values")
    print(f"   - Fidelities: {df['ctx_fidelity'].nunique()} unique values")
    
    print(f"\n⚡ Edge Case Density:")
    hard_scenario_keywords = [
        "book_flight", "reserve_table", "error_redundant_command",
        "flagged_unprofessional", "sentiment_positive",
        "navigate_river_bank", "navigate_financial_bank",
        "greeting_correction", "confirm_query", "affirmation"
    ]
    hard_cases = df[df['expected_intent'].isin(hard_scenario_keywords)].shape[0]
    print(f"   - Hard scenarios: {hard_cases:,} rows ({100*hard_cases/len(df):.1f}%)")
    print("="*80 + "\n")


def main():
    """Main execution - generate and save the dataset."""
    print("\n" + "=" * 80)
    print("🚀 12-FACTOR CONTEXT ENGINE - TEST DATA GENERATOR")
    print("=" * 80)
    print()
    print("📋 Configuration:")
    print(f"   • Total rows: 10,000")
    print(f"   • Normal cases: 8,000 (80%)")
    print(f"   • Edge cases (hard scenarios): 2,000 (20%)")
    print(f"   • Output: data/context_test_data_large.csv")
    print()
    print("🎯 Deterministic Scenarios (If-Then Logic):")
    print("   1. 'Book it' - FACTOR 1: Association (travel → book_flight, dining → reserve_table)")
    print("   2. 'Turn on lights' - FACTOR 2: Conflict Check (already_on → error_redundant)")
    print("   3. Slang handling - FACTOR 7: Social Mode (Business → unprofessional, Casual → positive)")
    print("   4. 'Go to the bank' - FACTOR 8: Location (nature → river_bank, city → financial_bank)")
    print("   5. 'Good morning' - FACTOR 9: Time (night → correction, morning → appropriate)")
    print("   6. 'Right' - FACTOR 11: Intonation (rising → query, flat → affirmation)")
    print("   7. Slang mapping - FACTOR 12: Fidelity + FACTOR 10: User Profile (low_fidelity/Gen_Z → map)")
    print()
    print("=" * 80)
    
    # Generate dataset
    df = generate_dataset(num_rows=10000, edge_case_ratio=0.2)
    
    # Print statistics
    print_statistics(df)
    
    # Ensure output directory exists
    output_path = Path("data/context_test_data_large.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    print(f"💾 Saving dataset to {output_path}...")
    df.to_csv(output_path, index=False)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ SUCCESS!")
    print(f"   • File: {output_path.absolute()}")
    print(f"   • Rows: {len(df):,}")
    print(f"   • Size: {file_size_mb:.2f} MB")
    
    print(f"\n📝 Sample Rows (First 5 - Normal Cases):")
    sample_cols = ['input_text', 'expected_intent', 'ctx_location', 'ctx_intonation', 'ctx_user_profile']
    print()
    print(df[sample_cols].head(5).to_string(index=False))
    
    print(f"\n📝 Sample Rows (Last 5 - Edge Cases):")
    print()
    print(df[sample_cols].tail(5).to_string(index=False))
    
    print("\n" + "=" * 80)
    print("✨ Dataset ready for stress testing!")
    print("=" * 80 + "\n")
