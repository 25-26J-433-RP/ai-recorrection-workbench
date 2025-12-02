"""
Akura AI - Rule-Based Correction Service

This module implements the rule-based fallback system that ensures
critical spelling rules are never missed, even when AI confidence is low.
"""

import re
from typing import Dict, List, Optional, Tuple

from loguru import logger

from app.models.schemas import DyslexiaPatternType
from app.utils.sinhala_mappings import (
    COMMON_CORRECTIONS,
    DENTAL_RETROFLEX_PAIRS,
    PHONETIC_CONFUSION_MAP,
    VISUAL_CONFUSION_MAP,
    get_sinhala_chars,
    is_sinhala_char,
)


class RuleBasedCorrector:
    """
    Rule-based correction system for Sinhala dyslexic writing errors.
    
    This system provides deterministic corrections for known patterns,
    serving as a fallback when AI confidence is low or as a validation
    layer for AI corrections.
    """
    
    def __init__(self):
        """Initialize the rule-based corrector."""
        self.corrections = COMMON_CORRECTIONS
        self.phonetic_map = PHONETIC_CONFUSION_MAP
        self.visual_map = VISUAL_CONFUSION_MAP
        
        # Build reverse lookup for faster processing
        self._build_pattern_rules()
    
    def _build_pattern_rules(self):
        """Build pattern matching rules from mappings."""
        # Verb ending patterns (colloquial to written)
        self.verb_patterns = [
            # Pattern: word ending in ව without ා
            (r'(.+)ව$', r'\1වා'),
            # Pattern: word ending in ව් 
            (r'(.+)ව්$', r'\1වා'),
        ]
        
        # Grammar correction patterns
        self.grammar_patterns = {
            "මං": "මම",
            "උඹ": "ඔබ",
            "එයා": "ඔහු",
            "ඕනා": "ඕනෑ",
            "ඕන": "ඕනෑ",
        }
    
    def correct_word(self, word: str) -> Tuple[Optional[str], str, float]:
        """
        Apply rule-based correction to a single word.
        
        Args:
            word: The word to correct
            
        Returns:
            Tuple of (corrected_word or None, pattern_type, confidence)
        """
        # Check direct dictionary lookup first
        if word in self.corrections:
            corrected = self.corrections[word]
            pattern = self._detect_pattern_type(word, corrected)
            return corrected, pattern, 1.0
        
        # Check grammar patterns
        if word in self.grammar_patterns:
            return self.grammar_patterns[word], "Grammar (Spoken vs Written)", 1.0
        
        # Check verb ending patterns
        corrected = self._apply_verb_rules(word)
        if corrected and corrected != word:
            return corrected, "Grammar (Spoken vs Written)", 0.9
        
        # Check for visual scrambling
        corrected = self._check_scrambling(word)
        if corrected and corrected != word:
            return corrected, "Visual Sequencing (Scrambled)", 0.85
        
        # No rule-based correction found
        return None, "", 0.0
    
    def _apply_verb_rules(self, word: str) -> Optional[str]:
        """
        Apply verb ending correction rules.
        
        Args:
            word: The word to check
            
        Returns:
            Corrected word if pattern matches, None otherwise
        """
        for pattern, replacement in self.verb_patterns:
            if re.match(pattern, word):
                corrected = re.sub(pattern, replacement, word)
                # Validate it's a reasonable correction
                if corrected != word:
                    return corrected
        return None
    
    def _check_scrambling(self, word: str) -> Optional[str]:
        """
        Check for visual scrambling against known correct forms.
        
        Args:
            word: The word to check
            
        Returns:
            Correct form if found, None otherwise
        """
        word_chars = sorted(word)
        
        # Check against known corrections
        for incorrect, correct in self.corrections.items():
            if sorted(incorrect) == word_chars:
                # The word might be a scrambled form
                if sorted(correct) == word_chars:
                    return correct
        
        return None
    
    def _detect_pattern_type(
        self,
        original: str,
        corrected: str
    ) -> str:
        """
        Detect the type of error pattern between original and corrected.
        
        Args:
            original: Original word
            corrected: Corrected word
            
        Returns:
            Pattern type string
        """
        # Check for visual scrambling
        if sorted(original) == sorted(corrected):
            return "Visual Sequencing (Scrambled)"
        
        # Check for phonetic confusion
        if self._has_phonetic_swap(original, corrected):
            return "Phonetic Confusion (Dental/Retroflex)"
        
        # Check for grammar issue (length difference at end)
        if len(corrected) > len(original):
            if corrected.startswith(original[:-1]):
                return "Grammar (Spoken vs Written)"
        
        return "Unknown Pattern"
    
    def _has_phonetic_swap(self, original: str, corrected: str) -> bool:
        """Check if the difference is a phonetic swap."""
        if len(original) != len(corrected):
            return False
        
        for o, c in zip(original, corrected):
            if o != c:
                if o in self.phonetic_map and self.phonetic_map[o] == c:
                    return True
        return False
    
    def correct_text(
        self,
        text: str
    ) -> Tuple[str, List[Dict]]:
        """
        Apply rule-based corrections to entire text.
        
        Args:
            text: The text to correct
            
        Returns:
            Tuple of (corrected_text, list of corrections made)
        """
        words = text.split()
        corrected_words = []
        corrections = []
        
        for word in words:
            corrected, pattern, confidence = self.correct_word(word)
            
            if corrected and corrected != word:
                corrected_words.append(corrected)
                corrections.append({
                    "original": word,
                    "corrected": corrected,
                    "pattern": pattern,
                    "confidence": confidence,
                    "source": "rule-based"
                })
            else:
                corrected_words.append(word)
        
        return " ".join(corrected_words), corrections
    
    def validate_ai_correction(
        self,
        original: str,
        ai_correction: str,
        ai_confidence: float
    ) -> Tuple[str, str, float]:
        """
        Validate and potentially override AI correction with rules.
        
        This implements the hybrid approach where rule-based corrections
        can override low-confidence AI corrections.
        
        Args:
            original: Original word
            ai_correction: AI-suggested correction
            ai_confidence: AI confidence score
            
        Returns:
            Tuple of (final_correction, source, confidence)
        """
        # Get rule-based correction
        rule_correction, pattern, rule_confidence = self.correct_word(original)
        
        # If AI confidence is high and rule agrees or has no opinion
        if ai_confidence >= 0.8:
            if rule_correction is None or rule_correction == ai_correction:
                return ai_correction, "ai", ai_confidence
        
        # If rule-based has a strong correction
        if rule_correction and rule_confidence > 0.9:
            if ai_correction == rule_correction:
                return rule_correction, "hybrid", max(ai_confidence, rule_confidence)
            else:
                # Rule overrides AI for known patterns
                logger.info(
                    f"Rule-based override: '{original}' -> '{rule_correction}' "
                    f"(AI suggested: '{ai_correction}')"
                )
                return rule_correction, "rule-based", rule_confidence
        
        # If AI confidence is low and rule has something
        if ai_confidence < 0.6 and rule_correction:
            return rule_correction, "rule-based", rule_confidence
        
        # Default to AI correction
        return ai_correction, "ai", ai_confidence
    
    def get_known_corrections(self) -> Dict[str, str]:
        """Get all known word corrections."""
        return dict(self.corrections)
    
    def add_correction(self, incorrect: str, correct: str) -> None:
        """
        Add a new correction rule.
        
        Args:
            incorrect: The incorrect form
            correct: The correct form
        """
        self.corrections[incorrect] = correct
        logger.info(f"Added new correction rule: '{incorrect}' -> '{correct}'")


# Create singleton instance
rule_corrector = RuleBasedCorrector()
