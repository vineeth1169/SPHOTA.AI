"""
Apabhraṃśa Mapping (Vaikharī Layer)

Handles slang, accents, and corrupted forms by mapping them to canonical meanings.
This module normalizes non-standard input before semantic processing.
"""

from typing import Dict, List, Optional, Set
import re


class ApabhramsaMapper:
    """
    Maps slang, dialectical variations, and errors to canonical forms.
    
    Bhartrhari's concept: The meaning (Sphota) is invariant even if
    the surface form (Dhvani) is corrupted or non-standard.
    """
    
    def __init__(self) -> None:
        """Initialize the Apabhramsa mapper with default mappings."""
        # Common slang/colloquial to formal mappings
        self.slang_map: Dict[str, str] = {
            # English casual → formal
            "gonna": "going to",
            "wanna": "want to",
            "gotta": "got to",
            "kinda": "kind of",
            "sorta": "sort of",
            "dunno": "don't know",
            "lemme": "let me",
            "gimme": "give me",
            "wont": "won't",
            "cant": "can't",
            "dont": "don't",
            "didnt": "didn't",
            "wasnt": "wasn't",
            "werent": "weren't",
            "shouldnt": "shouldn't",
            "wouldnt": "wouldn't",
            "couldnt": "couldn't",
            
            # Common abbreviations
            "u": "you",
            "ur": "your",
            "r": "are",
            "y": "why",
            "pls": "please",
            "plz": "please",
            "thx": "thanks",
            "thnx": "thanks",
            "np": "no problem",
            "nvm": "never mind",
            "idk": "i don't know",
            "imo": "in my opinion",
            "btw": "by the way",
            "omw": "on my way",
            
            # Typos and phonetic spellings
            "bcoz": "because",
            "coz": "because",
            "cuz": "because",
            "tho": "though",
            "thru": "through",
            "prolly": "probably",
            "def": "definitely",
            "srsly": "seriously",
        }
        
        # Accent-based phonetic variations
        self.phonetic_variations: Dict[str, List[str]] = {
            "what": ["wut", "wat", "wot"],
            "because": ["bcoz", "coz", "cuz", "bcuz"],
            "yes": ["yea", "yeah", "yep", "yup"],
            "no": ["nah", "nope"],
            "okay": ["ok", "k", "kay", "kk"],
            "thanks": ["thx", "thnx", "thanx"],
            "please": ["pls", "plz", "plox"],
        }
        
        # Build reverse lookup for phonetic variations
        self.phonetic_reverse: Dict[str, str] = {}
        for canonical, variations in self.phonetic_variations.items():
            for variation in variations:
                self.phonetic_reverse[variation] = canonical
        
        # Common repetition patterns (emphasis through repetition)
        self.repetition_pattern = re.compile(r'(.)\1{2,}')
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by applying all Apabhramsa corrections.
        
        Args:
            text: Raw input text (potentially with slang/errors)
            
        Returns:
            Normalized text closer to canonical form
        """
        # Convert to lowercase for consistent processing
        normalized = text.lower().strip()
        
        # Remove excessive punctuation
        normalized = re.sub(r'([!?.]){2,}', r'\1', normalized)
        
        # Reduce character repetitions (e.g., "hellooo" → "hello")
        normalized = self.repetition_pattern.sub(r'\1\1', normalized)
        
        # Apply slang mappings (word boundaries to avoid partial matches)
        words = normalized.split()
        normalized_words: List[str] = []
        
        for word in words:
            # Remove trailing punctuation for mapping
            punctuation = ''
            clean_word = word.rstrip('.,!?;:')
            if len(clean_word) < len(word):
                punctuation = word[len(clean_word):]
            
            # Check slang map
            if clean_word in self.slang_map:
                normalized_words.append(self.slang_map[clean_word] + punctuation)
            # Check phonetic variations
            elif clean_word in self.phonetic_reverse:
                normalized_words.append(self.phonetic_reverse[clean_word] + punctuation)
            else:
                normalized_words.append(word)
        
        normalized = ' '.join(normalized_words)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def add_slang_mapping(self, slang: str, canonical: str) -> None:
        """
        Add a custom slang to canonical mapping.
        
        Args:
            slang: Non-standard form
            canonical: Standard/canonical form
        """
        self.slang_map[slang.lower()] = canonical.lower()
    
    def add_phonetic_variation(self, canonical: str, variations: List[str]) -> None:
        """
        Add phonetic variations for a canonical word.
        
        Args:
            canonical: Standard form
            variations: List of phonetic/accent variations
        """
        if canonical in self.phonetic_variations:
            self.phonetic_variations[canonical].extend(variations)
        else:
            self.phonetic_variations[canonical] = variations
        
        # Update reverse lookup
        for variation in variations:
            self.phonetic_reverse[variation.lower()] = canonical.lower()
    
    def get_variations(self, canonical: str) -> List[str]:
        """
        Get all known variations of a canonical word.
        
        Args:
            canonical: Standard form word
            
        Returns:
            List of known variations
        """
        variations: Set[str] = set()
        
        canonical_lower = canonical.lower()
        
        # Check phonetic variations
        if canonical_lower in self.phonetic_variations:
            variations.update(self.phonetic_variations[canonical_lower])
        
        # Check slang map (reverse lookup)
        for slang, standard in self.slang_map.items():
            if standard == canonical_lower:
                variations.add(slang)
        
        return list(variations)
    
    def is_variation(self, word: str, canonical: str) -> bool:
        """
        Check if a word is a known variation of a canonical form.
        
        Args:
            word: Word to check
            canonical: Canonical form to compare against
            
        Returns:
            True if word is a variation of canonical
        """
        word_lower = word.lower()
        canonical_lower = canonical.lower()
        
        if word_lower == canonical_lower:
            return True
        
        # Check if word maps to canonical through slang
        if word_lower in self.slang_map:
            return self.slang_map[word_lower] == canonical_lower
        
        # Check if word is in phonetic variations
        if word_lower in self.phonetic_reverse:
            return self.phonetic_reverse[word_lower] == canonical_lower
        
        return False
    
    def get_mapping_stats(self) -> Dict[str, int]:
        """
        Get statistics about loaded mappings.
        
        Returns:
            Dictionary with counts of different mapping types
        """
        return {
            "slang_mappings": len(self.slang_map),
            "phonetic_canonical_words": len(self.phonetic_variations),
            "total_phonetic_variations": sum(
                len(vars) for vars in self.phonetic_variations.values()
            ),
            "reverse_phonetic_mappings": len(self.phonetic_reverse)
        }
