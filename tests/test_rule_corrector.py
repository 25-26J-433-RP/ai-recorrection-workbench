"""
Akura AI - Rule Corrector Tests

Unit tests for the rule-based correction service.
"""

import pytest

from app.services.rule_corrector import RuleBasedCorrector, rule_corrector


class TestRuleBasedCorrector:
    """Tests for RuleBasedCorrector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.corrector = RuleBasedCorrector()
    
    def test_known_correction(self):
        """Test correction of known misspelled word."""
        corrected, pattern, confidence = self.corrector.correct_word("ගෙරද")
        
        assert corrected == "ගෙදර"
        assert confidence > 0.9
    
    def test_verb_ending_correction(self):
        """Test verb ending pattern correction."""
        corrected, pattern, confidence = self.corrector.correct_word("යනව")
        
        assert corrected == "යනවා"
        assert pattern == "Grammar (Spoken vs Written)"
    
    def test_unknown_word(self):
        """Test behavior with unknown word."""
        corrected, pattern, confidence = self.corrector.correct_word("නොදන්නවචනය")
        
        # Should return None for unknown words
        assert corrected is None or confidence == 0.0
    
    def test_text_correction(self):
        """Test full text correction."""
        text = "මම ගෙරද යනව"
        corrected_text, corrections = self.corrector.correct_text(text)
        
        assert "ගෙදර" in corrected_text
        assert "යනවා" in corrected_text
        assert len(corrections) >= 2
    
    def test_ai_validation_high_confidence(self):
        """Test AI validation with high confidence."""
        result, source, conf = self.corrector.validate_ai_correction(
            original="ගෙරද",
            ai_correction="ගෙදර",
            ai_confidence=0.95
        )
        
        assert result == "ගෙදර"
        assert conf >= 0.9
    
    def test_ai_validation_low_confidence(self):
        """Test AI validation with low confidence, rule override."""
        result, source, conf = self.corrector.validate_ai_correction(
            original="යනව",
            ai_correction="යනවි",  # Wrong AI correction
            ai_confidence=0.3
        )
        
        # Rule should override
        assert result == "යනවා"
        assert source == "rule-based"
    
    def test_ai_validation_agreement(self):
        """Test when AI and rules agree."""
        result, source, conf = self.corrector.validate_ai_correction(
            original="ගෙරද",
            ai_correction="ගෙදර",
            ai_confidence=0.85
        )
        
        assert result == "ගෙදර"
        assert source in ["ai", "hybrid"]
    
    def test_grammar_patterns(self):
        """Test grammar pattern corrections."""
        # Test common colloquial to written conversions
        test_cases = [
            ("මං", "මම"),
            ("උඹ", "ඔබ"),
        ]
        
        for incorrect, expected in test_cases:
            corrected, pattern, conf = self.corrector.correct_word(incorrect)
            assert corrected == expected, f"Expected '{expected}' for '{incorrect}'"
    
    def test_add_correction(self):
        """Test adding new correction rule."""
        self.corrector.add_correction("පැරණි", "පරණ")
        
        corrected, pattern, conf = self.corrector.correct_word("පැරණි")
        assert corrected == "පරණ"
    
    def test_get_known_corrections(self):
        """Test retrieving all known corrections."""
        corrections = self.corrector.get_known_corrections()
        
        assert isinstance(corrections, dict)
        assert len(corrections) > 0
        assert "ගෙරද" in corrections


class TestRuleCorrectorSingleton:
    """Test the singleton rule corrector instance."""
    
    def test_singleton_exists(self):
        """Test that singleton instance is created."""
        assert rule_corrector is not None
    
    def test_singleton_has_methods(self):
        """Test that singleton has required methods."""
        assert hasattr(rule_corrector, 'correct_word')
        assert hasattr(rule_corrector, 'correct_text')
        assert hasattr(rule_corrector, 'validate_ai_correction')
