"""
Automated refactoring script to replace Sanskrit terminology with English DDD terms.
"""

import re
from pathlib import Path

# Define replacement mappings
REPLACEMENTS = {
    # Class/Module names
    'PasyantiEngine': 'IntentEngine',
    'ApabhramsaLayer': 'NormalizationLayer',
    
    # Context object fields (as dict keys or attributes)
    "'sahacarya'": "'history'",
    '"sahacarya"': '"history"',
    'sahacarya=': 'history=',
    '.sahacarya': '.history',
    
    "'virodhita'": "'conflict'",
    '"virodhita"': '"conflict"',
    'virodhita=': 'conflict=',
    '.virodhita': '.conflict',
    
    "'artha'": "'purpose'",
    '"artha"': '"purpose"',
    'artha=': 'purpose=',
    '.artha': '.purpose',
    
    "'prakarana'": "'situation'",
    '"prakarana"': '"situation"',
    'prakarana=': 'situation=',
    '.prakarana': '.situation',
    
    "'linga'": "'indicator'",
    '"linga"': '"indicator"',
    'linga=': 'indicator=',
    '.linga': '.indicator',
    
    "'shabda_samarthya'": "'word_power'",
    '"shabda_samarthya"': '"word_power"',
    'shabda_samarthya=': 'word_power=',
    '.shabda_samarthya': '.word_power',
    
    "'auciti'": "'propriety'",
    '"auciti"': '"propriety"',
    'auciti=': 'propriety=',
    '.auciti': '.propriety',
    
    "'desa'": "'location'",
    '"desa"': '"location"',
    'desa=': 'location=',
    '.desa': '.location',
    
    "'kala'": "'time'",
    '"kala"': '"time"',
    'kala=': 'time=',
    '.kala': '.time',
    
    "'vyakti'": "'user_profile'",
    '"vyakti"': '"user_profile"',
    'vyakti=': 'user_profile=',
    '.vyakti': '.user_profile',
    
    "'svara'": "'intonation'",
    '"svara"': '"intonation"',
    'svara=': 'intonation=',
    '.svara': '.intonation',
    
    "'apabhramsa'": "'distortion'",
    '"apabhramsa"': '"distortion"',
    'apabhramsa=': 'distortion=',
    '.apabhramsa': '.distortion',
    
    # Variable names (bare words)
    'kala_obj': 'time_obj',
    'sahacarya_data': 'history_data',
}

# Comments and docstrings
COMMENT_REPLACEMENTS = {
    'Sahacarya': 'Association',
    'Virodhitā': 'Conflict',
    'Virodhita': 'Conflict',
    'Artha': 'Purpose',
    'Prakaraṇa': 'Situation',
    'Prakarana': 'Situation',
    'Liṅga': 'Indicator',
    'Linga': 'Indicator',
    'Śabda-sāmarthya': 'WordPower',
    'Shabda-samarthya': 'WordPower',
    'Aucitī': 'Propriety',
    'Auciti': 'Propriety',
    'Deśa': 'Location',
    'Desa': 'Location',
    'Kāla': 'Time',
    'Kala': 'Time',
    'Vyakti': 'UserProfile',
    'Svara': 'Intonation',
    'Apabhraṃśa': 'Distortion',
    'Apabhramsa': 'Distortion',
}

def refactor_file(file_path: Path):
    """Apply refactoring to a single file."""
    print(f"Processing: {file_path}")
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Apply code replacements
        for old, new in REPLACEMENTS.items():
            content = content.replace(old, new)
        
        # Apply comment/docstring replacements
        for old, new in COMMENT_REPLACEMENTS.items():
            content = content.replace(old, new)
        
        # Only write if content changed
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✓ Updated {file_path.name}")
        else:
            print(f"  - No changes needed for {file_path.name}")
            
    except Exception as e:
        print(f"  ✗ Error processing {file_path}: {e}")

def main():
    """Run refactoring on all relevant files."""
    base_path = Path(__file__).parent
    
    # Files to refactor
    files_to_process = [
        base_path / 'core' / 'context_matrix.py',
        base_path / 'core' / 'context_manager.py',
        base_path / 'core' / 'intent_engine.py',
        base_path / 'app.py',
    ]
    
    print("=" * 60)
    print("ENGLISH-ONLY REFACTORING")
    print("=" * 60)
    
    for file_path in files_to_process:
        if file_path.exists():
            refactor_file(file_path)
        else:
            print(f"⚠ File not found: {file_path}")
    
    print("=" * 60)
    print("✓ Refactoring complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
