"""
Normalization Layer (Input Processing)

Handles distorted input (slang, accents, typos) by mapping to pure semantic vectors.
This is NOT error correction - it's a bridge to meaning that treats distortion
as a valid linguistic phenomenon, per Bhartṛhari's philosophy.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import re
import numpy as np
from numpy.typing import NDArray


class NormalizationLayer:
    """
    distortion normalization and semantic bridge.
    
    The core insight: meaning remains invariant even when the surface form is distorted. This layer doesn't "fix" errors -
    it recognizes that slang and accent are alternative paths to the same meaning.
    """
    
    def __init__(self) -> None:
        """Initialize the normalization layer with normalization rules."""
        # Slang to formal mapping (meaning-preserving transformations)
        self.slang_to_formal: Dict[str, str] = {
            # Contractions
            "gonna": "going to",
            "wanna": "want to",
            "gotta": "got to",
            "hafta": "have to",
            "kinda": "kind of",
            "sorta": "sort of",
            "dunno": "don't know",
            "lemme": "let me",
            "gimme": "give me",
            "gotcha": "got you",
            
            # Missing apostrophes
            "wont": "won't",
            "cant": "can't",
            "dont": "don't",
            "didnt": "didn't",
            "wasnt": "wasn't",
            "werent": "weren't",
            "shouldnt": "shouldn't",
            "wouldnt": "wouldn't",
            "couldnt": "couldn't",
            "hasnt": "hasn't",
            "hadnt": "hadn't",
            "isnt": "isn't",
            "arent": "aren't",
            
            # Abbreviations
            "u": "you",
            "ur": "your",
            "r": "are",
            "y": "why",
            "pls": "please",
            "plz": "please",
            "thx": "thanks",
            "thnx": "thanks",
            "ty": "thank you",
            "np": "no problem",
            "nvm": "never mind",
            "idk": "i don't know",
            "imo": "in my opinion",
            "btw": "by the way",
            "omw": "on my way",
            "brb": "be right back",
            "afk": "away from keyboard",
            
            # Phonetic variations
            "bcoz": "because",
            "coz": "because",
            "cuz": "because",
            "tho": "though",
            "thru": "through",
            "prolly": "probably",
            "def": "definitely",
            "srsly": "seriously",
            "obvi": "obviously",
            "whatcha": "what are you",
            "whatchu": "what are you",
            "lemme": "let me",
            
            # Common misspellings (meaning-preserving)
            "alot": "a lot",
            "shoulda": "should have",
            "woulda": "would have",
            "coulda": "could have",
        }
        
        # Phonetic variation clusters (different spellings, same meaning)
        self.phonetic_clusters: Dict[str, List[str]] = {
            "what": ["wut", "wat", "wot", "whut"],
            "yes": ["yea", "yeah", "yep", "yup", "ye"],
            "no": ["nah", "nope", "naw"],
            "okay": ["ok", "k", "kay", "kk", "mkay"],
            "because": ["bcoz", "coz", "cuz", "bcuz", "cus"],
            "with": ["wit", "wif", "wiv"],
            "you": ["u", "ya", "yah"],
            "your": ["ur", "yer"],
            "are": ["r"],
            "to": ["2", "too"],
            "for": ["4", "fer"],
            "thanks": ["thx", "thnx", "thanx", "ty"],
            "please": ["pls", "plz", "plox"],
        }
        
        # Build reverse lookup for phonetic clusters
        self.phonetic_reverse: Dict[str, str] = {}
        for canonical, variations in self.phonetic_clusters.items():
            for variation in variations:
                self.phonetic_reverse[variation] = canonical
        
        # Repetition pattern for emphasis (e.g., "soooo" -> "so")
        self.repetition_pattern = re.compile(r'(.)\1{2,}')
        
        # Capitalization pattern for emphasis (e.g., "HELLO")
        self.caps_pattern = re.compile(r'^[A-Z]{2,}$')
    
    def normalize_to_pure_form(self, text: str) -> Tuple[str, float]:
        """
        Normalize distortion input to pure semantic form.
        
        Returns both the normalized text and a distortion score that can be
        used as a confidence penalty in the Context Resolution Matrix.
        
        Args:
            text: Raw input text (potentially with slang/distortion)
            
        Returns:
            Tuple of (normalized_text, distortion_score)
            distortion_score: 0.0 = clean, 1.0 = heavily distorted
        """
        original = text
        normalized = text.lower().strip()
        transformation_count = 0
        
        # Remove excessive punctuation
        if re.search(r'([!?.]){2,}', normalized):
            normalized = re.sub(r'([!?.]){2,}', r'\1', normalized)
            transformation_count += 1
        
        # Reduce character repetitions (emphasis pattern)
        repetition_matches = self.repetition_pattern.findall(normalized)
        if repetition_matches:
            normalized = self.repetition_pattern.sub(r'\1\1', normalized)
            transformation_count += len(repetition_matches)
        
        # Process word by word
        words = normalized.split()
        normalized_words: List[str] = []
        
        for word in words:
            # Preserve punctuation
            punctuation = ''
            clean_word = word.rstrip('.,!?;:\'\"')
            if len(clean_word) < len(word):
                punctuation = word[len(clean_word):]
            
            # Check slang mapping
            if clean_word in self.slang_to_formal:
                normalized_words.append(self.slang_to_formal[clean_word] + punctuation)
                transformation_count += 1
            # Check phonetic variations
            elif clean_word in self.phonetic_reverse:
                normalized_words.append(self.phonetic_reverse[clean_word] + punctuation)
                transformation_count += 1
            else:
                normalized_words.append(word)
        
        normalized = ' '.join(normalized_words)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Calculate distortion score
        # Based on: number of transformations / word count
        word_count = max(len(words), 1)
        distortion_score = min(1.0, transformation_count / (word_count * 0.5))
        
        return normalized, distortion_score
    
    def bridge_to_semantic_vector(
        self,
        text: str,
        encoder_fn: Callable
    ) -> Tuple[NDArray[np.float32], float]:
        """
        Bridge distorted text to semantic vector space.
        
        This is the key distortion operation: regardless of surface distortion,
        we extract the underlying Sphota (meaning-bearing unit).
        
        Args:
            text: Input text (potentially distorted)
            encoder_fn: Function that encodes text to vector (e.g., SBERT.encode)
            
        Returns:
            Tuple of (semantic_vector, distortion_score)
        """
        # Normalize the text
        normalized_text, distortion_score = self.normalize_to_pure_form(text)
        
        # Encode to semantic space
        semantic_vector = encoder_fn(normalized_text)
        
        return semantic_vector, distortion_score
    
    def detect_emphasis_patterns(self, text: str) -> Dict[str, Any]:
        """
        Detect emphasis patterns in text (repetition, caps, punctuation).
        
        These are NOT errors - they carry prosodic/emotional information
        that can be used by the Svara (intonation) factor in CRM.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with emphasis indicators
        """
        emphasis = {
            "has_repetition": bool(self.repetition_pattern.search(text)),
            "has_caps": bool(self.caps_pattern.search(text)),
            "exclamation_count": text.count('!'),
            "question_marks": text.count('?'),
            "intensity_score": 0.0
        }
        
        # Calculate overall intensity
        intensity = 0.0
        if emphasis["has_repetition"]:
            intensity += 0.3
        if emphasis["has_caps"]:
            intensity += 0.3
        if emphasis["exclamation_count"] > 0:
            intensity += min(0.4, emphasis["exclamation_count"] * 0.1)
        
        emphasis["intensity_score"] = min(1.0, intensity)
        
        return emphasis
    
    def add_slang_mapping(self, slang: str, formal: str) -> None:
        """
        Add custom slang-to-formal mapping.
        
        Args:
            slang: Slang/distorted form
            formal: Formal/canonical form
        """
        self.slang_to_formal[slang.lower()] = formal.lower()
    
    def add_phonetic_cluster(self, canonical: str, variations: List[str]) -> None:
        """
        Add phonetic variation cluster.
        
        Args:
            canonical: Standard form
            variations: List of phonetic variations
        """
        if canonical in self.phonetic_clusters:
            self.phonetic_clusters[canonical].extend(variations)
        else:
            self.phonetic_clusters[canonical] = variations
        
        # Update reverse lookup
        for variation in variations:
            self.phonetic_reverse[variation.lower()] = canonical.lower()
    
    def get_distortion_explanation(
        self,
        original: str,
        normalized: str
    ) -> List[str]:
        """
        Explain what transformations were applied.
        
        Useful for debugging and user transparency.
        
        Args:
            original: Original input text
            normalized: Normalized output text
            
        Returns:
            List of transformation descriptions
        """
        explanations = []
        
        if original.lower() != normalized:
            # Word-level comparison
            orig_words = original.lower().split()
            norm_words = normalized.split()
            
            for i, (orig, norm) in enumerate(zip(orig_words, norm_words)):
                orig_clean = orig.rstrip('.,!?;:\'\"')
                norm_clean = norm.rstrip('.,!?;:\'\"')
                
                if orig_clean != norm_clean:
                    if orig_clean in self.slang_to_formal:
                        explanations.append(
                            f"Slang: '{orig_clean}' → '{self.slang_to_formal[orig_clean]}'"
                        )
                    elif orig_clean in self.phonetic_reverse:
                        explanations.append(
                            f"Phonetic: '{orig_clean}' → '{self.phonetic_reverse[orig_clean]}'"
                        )
            
            # Check for repetitions
            if self.repetition_pattern.search(original):
                explanations.append("Reduced character repetition (emphasis)")
            
            # Check for excessive punctuation
            if re.search(r'([!?.]){2,}', original):
                explanations.append("Normalized excessive punctuation")
        
        return explanations if explanations else ["No transformations needed"]
    
    def calculate_semantic_distance(
        self,
        original_vec: NDArray[np.float32],
        normalized_vec: NDArray[np.float32]
    ) -> float:
        """
        Calculate semantic distance between original and normalized vectors.
        
        Low distance = distortion preserved meaning well
        High distance = significant semantic shift (may indicate true error)
        
        Args:
            original_vec: Vector from original text
            normalized_vec: Vector from normalized text
            
        Returns:
            Cosine distance (0 = identical, 2 = opposite)
        """
        # Cosine similarity
        dot_product = np.dot(original_vec, normalized_vec)
        norm_orig = np.linalg.norm(original_vec)
        norm_norm = np.linalg.norm(normalized_vec)
        
        if norm_orig == 0 or norm_norm == 0:
            return 2.0
        
        similarity = dot_product / (norm_orig * norm_norm)
        
        # Convert to distance (0 to 2)
        distance = 1.0 - similarity
        
        return float(distance)
    
    def get_normalization_stats(self) -> Dict[str, int]:
        """
        Get statistics about loaded normalization rules.
        
        Returns:
            Dictionary with counts of different rule types
        """
        return {
            "slang_mappings": len(self.slang_to_formal),
            "phonetic_canonical_words": len(self.phonetic_clusters),
            "total_phonetic_variations": sum(
                len(vars) for vars in self.phonetic_clusters.values()
            ),
            "reverse_phonetic_mappings": len(self.phonetic_reverse)
        }

