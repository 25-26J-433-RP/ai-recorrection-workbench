"""
Akura AI - Dyslexia Pattern Detector

This module implements the "Intelligent Diff" logic that detects
specific dyslexia patterns in Sinhala text by comparing original
and corrected words.
"""

from difflib import SequenceMatcher
from typing import List, Optional, Tuple

from app.models.schemas import DyslexiaPatternType
from app.utils.sinhala_mappings import (
    COMMON_CORRECTIONS,
    DENTAL_RETROFLEX_PAIRS,
    PATTERN_EXPLANATIONS,
    PHONETIC_CONFUSABLE_CHARS,
    PHONETIC_CONFUSION_MAP,
    VISUAL_CONFUSABLE_CHARS,
    VISUAL_CONFUSION_MAP,
    get_sinhala_chars,
    is_sinhala_char,
)


class DyslexiaPatternDetector:
    """
    Detects and categorizes dyslexia-related writing errors in Sinhala text.
    
    This class implements the "Intelligent Diff" logic that compares input
    and corrected text to determine the type of error made.
    """
    
    def __init__(self):
        """Initialize the pattern detector with mappings."""
        self.phonetic_pairs = DENTAL_RETROFLEX_PAIRS
        self.phonetic_map = PHONETIC_CONFUSION_MAP
        self.visual_map = VISUAL_CONFUSION_MAP
        self.common_corrections = COMMON_CORRECTIONS
    
    def detect_pattern(
        self,
        original: str,
        corrected: str
    ) -> Tuple[DyslexiaPatternType, str, float]:
        """
        Detect the dyslexia pattern between original and corrected word.
        
        Args:
            original: The original (potentially incorrect) word
            corrected: The corrected version of the word
            
        Returns:
            Tuple of (pattern_type, explanation, confidence)
        """
        if original == corrected:
            return (
                DyslexiaPatternType.UNKNOWN,
                "No error detected - words are identical.",
                1.0
            )
        
        # Check for visual scrambling first (letter order)
        if self._is_visual_scrambling(original, corrected):
            return (
                DyslexiaPatternType.VISUAL_SCRAMBLING,
                PATTERN_EXPLANATIONS[DyslexiaPatternType.VISUAL_SCRAMBLING.value],
                0.95
            )
        
        # Check for phonetic confusion (dental/retroflex swaps)
        if self._is_phonetic_confusion(original, corrected):
            return (
                DyslexiaPatternType.PHONETIC_CONFUSION,
                PATTERN_EXPLANATIONS[DyslexiaPatternType.PHONETIC_CONFUSION.value],
                0.90
            )
        
        # Check for visual reversal (shape confusion)
        if self._is_visual_reversal(original, corrected):
            return (
                DyslexiaPatternType.VISUAL_REVERSAL,
                PATTERN_EXPLANATIONS[DyslexiaPatternType.VISUAL_REVERSAL.value],
                0.85
            )
        
        # Check for grammar/colloquial issues
        if self._is_grammar_issue(original, corrected):
            return (
                DyslexiaPatternType.GRAMMAR_SPOKEN,
                PATTERN_EXPLANATIONS[DyslexiaPatternType.GRAMMAR_SPOKEN.value],
                0.88
            )
        
        # Default to unknown pattern
        return (
            DyslexiaPatternType.UNKNOWN,
            PATTERN_EXPLANATIONS[DyslexiaPatternType.UNKNOWN.value],
            0.5
        )
    
    def _is_visual_scrambling(self, original: str, corrected: str) -> bool:
        """
        Check if the error is due to visual scrambling (letter reordering).
        
        Visual scrambling occurs when letters are in the wrong order but
        all the same letters are present.
        
        Example: ගෙරද → ගෙදර (letters scrambled)
        """
        # Get only Sinhala characters for comparison
        orig_chars = get_sinhala_chars(original)
        corr_chars = get_sinhala_chars(corrected)
        
        # If sorted characters match, it's a scrambling issue
        if sorted(orig_chars) == sorted(corr_chars) and orig_chars != corr_chars:
            return True
        
        # Also check with full strings for words with vowel signs
        if sorted(original) == sorted(corrected) and original != corrected:
            return True
        
        return False
    
    def _is_phonetic_confusion(self, original: str, corrected: str) -> bool:
        """
        Check if the error is due to phonetic confusion.
        
        Phonetic confusion occurs when similar-sounding consonants
        are swapped, particularly dental/retroflex pairs.
        
        Example: න → ණ or ල → ළ
        """
        if len(original) != len(corrected):
            return False
        
        differences = []
        for i, (o, c) in enumerate(zip(original, corrected)):
            if o != c:
                differences.append((o, c))
        
        # Check if all differences are phonetic confusion pairs
        if not differences:
            return False
        
        for orig_char, corr_char in differences:
            # Check if this is a known phonetic confusion pair
            if orig_char in self.phonetic_map:
                if self.phonetic_map[orig_char] == corr_char:
                    continue
            # If any difference is not a phonetic pair, return False
            if not self._is_phonetic_pair(orig_char, corr_char):
                return False
        
        return True
    
    def _is_phonetic_pair(self, char1: str, char2: str) -> bool:
        """Check if two characters form a phonetic confusion pair."""
        for dental, retroflex in self.phonetic_pairs:
            if (char1 == dental and char2 == retroflex) or \
               (char1 == retroflex and char2 == dental):
                return True
        return False
    
    def _is_visual_reversal(self, original: str, corrected: str) -> bool:
        """
        Check if the error is due to visual reversal (shape confusion).
        
        Visual reversal occurs when visually similar characters are confused.
        
        Example: බ → ඩ (similar shapes)
        """
        if len(original) != len(corrected):
            return False
        
        differences = []
        for o, c in zip(original, corrected):
            if o != c:
                differences.append((o, c))
        
        if not differences:
            return False
        
        # Check if all differences are visual confusion pairs
        for orig_char, corr_char in differences:
            if orig_char in self.visual_map:
                if self.visual_map[orig_char] == corr_char:
                    continue
            # Not a visual reversal
            if orig_char not in VISUAL_CONFUSABLE_CHARS:
                return False
        
        return True
    
    def _is_grammar_issue(self, original: str, corrected: str) -> bool:
        """
        Check if the error is due to grammar/colloquial usage.
        
        Grammar issues occur when colloquial/spoken forms are used
        instead of proper written forms.
        
        Example: යනව → යනවා (missing vowel ending)
        """
        # Check common patterns
        # Pattern 1: Missing final 'ා' vowel sign in verbs
        if corrected.endswith("වා") and original.endswith("ව"):
            if corrected[:-1] == original[:-1] + "ා":
                return True
            if corrected[:-2] == original[:-1]:
                return True
        
        # Pattern 2: Check against known corrections
        if original in self.common_corrections:
            if self.common_corrections[original] == corrected:
                return True
        
        # Pattern 3: Length difference of 1 at the end (usually vowel sign)
        if len(corrected) - len(original) == 1:
            if corrected.startswith(original) or original.startswith(corrected[:-1]):
                return True
        
        return False
    
    def get_correction_suggestion(self, word: str) -> Optional[str]:
        """
        Get a rule-based correction suggestion for a word.
        
        Args:
            word: The word to check for corrections
            
        Returns:
            Corrected word if found, None otherwise
        """
        # Check direct mappings
        if word in self.common_corrections:
            return self.common_corrections[word]
        
        # Check for common verb ending patterns
        if word.endswith("ව") and not word.endswith("වා"):
            # Try adding the vowel sign
            return word[:-1] + "වා"
        
        return None
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity ratio between 0.0 and 1.0
        """
        return SequenceMatcher(None, str1, str2).ratio()
    
    def get_word_differences(
        self,
        original: str,
        corrected: str
    ) -> List[Tuple[int, str, str]]:
        """
        Get character-level differences between two words.
        
        Args:
            original: Original word
            corrected: Corrected word
            
        Returns:
            List of (position, original_char, corrected_char) tuples
        """
        differences = []
        matcher = SequenceMatcher(None, original, corrected)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                for i, (o, c) in enumerate(zip(
                    original[i1:i2], corrected[j1:j2]
                )):
                    differences.append((i1 + i, o, c))
            elif tag == 'delete':
                for i, o in enumerate(original[i1:i2]):
                    differences.append((i1 + i, o, ''))
            elif tag == 'insert':
                for i, c in enumerate(corrected[j1:j2]):
                    differences.append((i1, '', c))
        
        return differences


# Create a singleton instance
pattern_detector = DyslexiaPatternDetector()
