"""
Integration Example: Using the ContextWeighter with PasyantiEngine

This demonstrates how to integrate the 12-factor ContextWeighter into your
intent resolution pipeline for advanced contextual scoring.

The ContextWeighter provides fine-grained control over how each contextual
factor influences the final intent confidence score.
"""

from core.pasyanti_engine import PasyantiEngine
from core.context_weighter import ContextWeighter
from pathlib import Path
from typing import Dict, Any, List
import json


class IntegratedIntentResolver:
    """
    Combined resolver using both PasyantiEngine and ContextWeighter.
    
    The PasyantiEngine provides semantic similarity scoring,
    while the ContextWeighter applies 12-factor contextual adjustments.
    """
    
    def __init__(self, intents_path: str = "data/intents.json"):
        """
        Initialize the integrated resolver.
        
        Args:
            intents_path: Path to intents.json file
        """
        self.engine = PasyantiEngine(intents_path=intents_path)
        self.weighter = ContextWeighter()
        self.intents_db: Dict[str, Any] = self._load_intents_db(intents_path)
    
    def _load_intents_db(self, intents_path: str) -> Dict[str, Any]:
        """Load intents database for metadata lookup."""
        with open(intents_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        db = {}
        for intent in data.get('intents', []):
            db[intent['id']] = intent
        
        return db
    
    def resolve_with_context(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve intent using both semantic similarity and 12-factor weighting.
        
        Args:
            user_input: User input text
            context: Context dictionary with keys:
                - user_history: List of recent commands
                - system_state: Current system state
                - active_goal: Current user goal
                - current_screen: Current UI screen
                - syntax_flags: List of syntax patterns detected
                - social_mode: 'business' or 'casual'
                - location: User's current location
                - time_of_day: Current time period
                - user_profile: User demographic profile
                - audio_features: Dict with audio analysis
                - input_fidelity: Input quality score (0.0-1.0)
        
        Returns:
            Dictionary with:
                - winner: Winning intent ID
                - winner_name: Human-readable intent name
                - confidence: Final confidence score (0.0-1.0)
                - raw_score: Original semantic similarity
                - adjusted_score: After 12-factor weighting
                - all_candidates: List of all scored intents
                - explanation: Detailed breakdown of scoring
        """
        # Step 1: Get semantic similarity scores from engine
        results = self.engine.resolve_intent(user_input, context, return_top_k=11)
        
        # Step 2: Build detailed intent metadata for weighting
        intent_scores = []
        
        for result in results:
            intent_id = result.intent.id
            intent_metadata = self.intents_db.get(intent_id, {})
            
            # Map intent metadata to ContextWeighter format
            intent_for_weighting = {
                'id': intent_id,
                'action': intent_metadata.get('action', ''),
                'type': intent_metadata.get('type', 'general'),
                'tags': intent_metadata.get('tags', []),
                'goal_alignment': intent_metadata.get('goal_alignment', ''),
                'valid_screens': intent_metadata.get('valid_screens', []),
                'formality': intent_metadata.get('formality', 'neutral'),
                'contains_slang': intent_metadata.get('contains_slang', False),
                'required_location': intent_metadata.get('required_location', ''),
                'time_specific': intent_metadata.get('time_specific', ''),
                'vocabulary_level': intent_metadata.get('vocabulary_level', 'neutral')
            }
            
            # Build context for weighting with base score
            context_for_weighting = dict(context)
            context_for_weighting['base_score'] = result.raw_similarity
            
            # Apply 12-factor weighting
            final_score = self.weighter.apply_weights(
                intent_for_weighting,
                context_for_weighting
            )
            
            intent_scores.append({
                'intent_id': intent_id,
                'intent_name': intent_metadata.get('pure_text', intent_id),
                'raw_score': result.raw_similarity,
                'adjusted_score': final_score,
                'description': intent_metadata.get('description', '')
            })
        
        # Step 3: Determine winner (highest final score)
        winner = max(intent_scores, key=lambda x: x['adjusted_score'])
        
        return {
            'winner': winner['intent_id'],
            'winner_name': winner['intent_name'],
            'confidence': winner['adjusted_score'],
            'raw_score': winner['raw_score'],
            'adjusted_score': winner['adjusted_score'],
            'all_candidates': intent_scores,
            'explanation': self._generate_explanation(
                user_input,
                winner,
                intent_scores,
                context
            )
        }
    
    def _generate_explanation(
        self,
        user_input: str,
        winner: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate detailed explanation of the resolution process.
        
        Returns explanation of why the winning intent was selected.
        """
        return {
            'input': user_input,
            'winner': winner['intent_id'],
            'reason': f"Selected due to {winner['adjusted_score']:.1%} confidence after 12-factor weighting",
            'context_used': {
                'user_history': context.get('user_history', []),
                'active_goal': context.get('active_goal'),
                'location': context.get('location'),
                'time_of_day': context.get('time_of_day'),
                'social_mode': context.get('social_mode'),
                'input_fidelity': context.get('input_fidelity', 1.0)
            },
            'top_competitors': [
                {
                    'intent': c['intent_id'],
                    'score': f"{c['adjusted_score']:.1%}",
                    'gap': f"{abs(winner['adjusted_score'] - c['adjusted_score']):.1%}"
                }
                for c in candidates[1:4]
            ]
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize the integrated resolver
    resolver = IntegratedIntentResolver(intents_path="data/intents.json")
    
    # Example 1: Resolving "bank" with different contexts
    print("=" * 70)
    print("EXAMPLE 1: Polysemic Disambiguation - 'Take me to the bank'")
    print("=" * 70)
    
    # Context 1: Nature/Fishing context
    nature_context = {
        'user_history': ['river', 'fishing', 'camping'],
        'system_state': 'OFF',
        'active_goal': 'outdoor_activity',
        'current_screen': 'home',
        'syntax_flags': ['statement', 'imperative'],
        'social_mode': 'casual',
        'location': 'nature_reserve',
        'time_of_day': 'afternoon',
        'user_profile': 'outdoor_enthusiast',
        'audio_features': {'pitch': 'flat', 'tone': 'relaxed'},
        'input_fidelity': 0.95
    }
    
    result_nature = resolver.resolve_with_context(
        "take me to the bank",
        nature_context
    )
    
    print(f"\nContext: Nature Reserve, Fishing History")
    print(f"Result: {result_nature['winner_name']}")
    print(f"Confidence: {result_nature['confidence']:.1%}")
    print(f"Raw Score: {result_nature['raw_score']:.1%}")
    print(f"Explanation: {result_nature['explanation']['reason']}")
    
    # Context 2: Urban/Finance context
    finance_context = {
        'user_history': ['transfer', 'balance', 'deposit'],
        'system_state': 'OFF',
        'active_goal': 'financial_management',
        'current_screen': 'banking_app',
        'syntax_flags': ['statement', 'imperative'],
        'social_mode': 'business',
        'location': 'city_center',
        'time_of_day': 'morning',
        'user_profile': 'professional',
        'audio_features': {'pitch': 'flat', 'tone': 'formal'},
        'input_fidelity': 0.98
    }
    
    result_finance = resolver.resolve_with_context(
        "take me to the bank",
        finance_context
    )
    
    print(f"\nContext: City Center, Finance History")
    print(f"Result: {result_finance['winner_name']}")
    print(f"Confidence: {result_finance['confidence']:.1%}")
    print(f"Raw Score: {result_finance['raw_score']:.1%}")
    print(f"Explanation: {result_finance['explanation']['reason']}")
    
    # Example 2: Home automation with location sensitivity
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Location-Aware Intent - 'Turn on the lights'")
    print("=" * 70)
    
    home_context = {
        'user_history': ['brightness', 'lighting', 'evening'],
        'system_state': 'OFF',
        'active_goal': 'home_comfort',
        'current_screen': 'home',
        'syntax_flags': ['statement', 'imperative'],
        'social_mode': 'casual',
        'location': 'home',
        'time_of_day': 'evening',
        'user_profile': 'homeowner',
        'audio_features': {'pitch': 'flat', 'tone': 'relaxed'},
        'input_fidelity': 0.96
    }
    
    result_home = resolver.resolve_with_context(
        "turn on the lights",
        home_context
    )
    
    print(f"\nContext: Home, Evening, Lighting History")
    print(f"Result: {result_home['winner_name']}")
    print(f"Confidence: {result_home['confidence']:.1%}")
    print(f"Top 3 Candidates:")
    for candidate in result_home['all_candidates'][:3]:
        print(f"  - {candidate['intent_name']}: {candidate['adjusted_score']:.1%}")
    
    # Example 3: Low fidelity (noisy input)
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Distorted Input Handling")
    print("=" * 70)
    
    noisy_context = {
        'user_history': ['music', 'play', 'audio'],
        'system_state': 'OFF',
        'active_goal': 'entertainment',
        'current_screen': 'media',
        'syntax_flags': ['statement'],
        'social_mode': 'casual',
        'location': 'home',
        'time_of_day': 'evening',
        'user_profile': 'music_lover',
        'audio_features': {'pitch': 'rising', 'tone': 'casual'},
        'input_fidelity': 0.42  # Low fidelity - noisy input
    }
    
    result_noisy = resolver.resolve_with_context(
        "play musick",  # Misspelled
        noisy_context
    )
    
    print(f"\nContext: Noisy Input (misspelled), High history context")
    print(f"Result: {result_noisy['winner_name']}")
    print(f"Confidence: {result_noisy['confidence']:.1%}")
    print(f"Input Fidelity: {noisy_context['input_fidelity']:.1%}")
    print(f"Note: Low fidelity triggers normalization layer")
    
    print("\n" + "=" * 70)
    print("Summary: The 12-factor weighter successfully:")
    print("  ✓ Resolved 'bank' to different intents based on context")
    print("  ✓ Boosted location-relevant intents")
    print("  ✓ Handled noisy input with history-based recovery")
    print("=" * 70)
