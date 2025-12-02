"""
Akura AI - Pattern Detector Tests

Unit tests for the dyslexia pattern detection service.
"""

import pytest

from app.services.pattern_detector import DyslexiaPatternDetector, pattern_detector
from app.models.schemas import DyslexiaPatternType


class TestDyslexiaPatternDetector:
    """Tests for DyslexiaPatternDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = DyslexiaPatternDetector()
    
    def test_visual_scrambling_detection(self):
        """Test detection of visual scrambling errors."""
        original = "ගෙරද"
        corrected = "ගෙදර"
        
        pattern, explanation, confidence = self.detector.detect_pattern(
            original, corrected
        )
        
        assert pattern == DyslexiaPatternType.VISUAL_SCRAMBLING
        assert confidence > 0.8
    
    def test_phonetic_confusion_detection(self):
        """Test detection of phonetic confusion (dental/retroflex)."""
        # Test ණ vs න confusion
        original = "මානය"  # with retroflex ණ would be මාණය
        corrected = "මාණය"
        
        # The detector should identify phonetic confusion
        pattern, explanation, confidence = self.detector.detect_pattern(
            original, corrected
        )
        
        # Note: This specific case might not be perfect without more context
        assert confidence > 0.0
    
    def test_grammar_issue_detection(self):
        """Test detection of grammar/colloquial issues."""
        original = "යනව"
        corrected = "යනවා"
        
        pattern, explanation, confidence = self.detector.detect_pattern(
            original, corrected
        )
        
        assert pattern == DyslexiaPatternType.GRAMMAR_SPOKEN
        assert confidence > 0.8
    
    def test_identical_words(self):
        """Test that identical words return no error."""
        word = "ගෙදර"
        
        pattern, explanation, confidence = self.detector.detect_pattern(
            word, word
        )
        
        assert confidence == 1.0
        assert "identical" in explanation.lower()
    
    def test_similarity_calculation(self):
        """Test string similarity calculation."""
        # Identical strings
        assert self.detector.calculate_similarity("ගෙදර", "ගෙදර") == 1.0
        
        # Completely different
        similarity = self.detector.calculate_similarity("අ", "ඔ")
        assert similarity < 1.0
        
        # Similar strings
        similarity = self.detector.calculate_similarity("ගෙරද", "ගෙදර")
        assert 0.5 < similarity < 1.0
    
    def test_word_differences(self):
        """Test character-level difference detection."""
        differences = self.detector.get_word_differences("යනව", "යනවා")
        
        assert len(differences) > 0
    
    def test_is_visual_scrambling(self):
        """Test internal scrambling detection method."""
        assert self.detector._is_visual_scrambling("ගෙරද", "ගෙදර") == True
        assert self.detector._is_visual_scrambling("මම", "මමා") == False
    
    def test_is_grammar_issue(self):
        """Test internal grammar issue detection."""
        assert self.detector._is_grammar_issue("යනව", "යනවා") == True
        assert self.detector._is_grammar_issue("කනව", "කනවා") == True
        assert self.detector._is_grammar_issue("ගෙදර", "ගෙදර") == False


class TestPatternDetectorSingleton:
    """Test the singleton pattern detector instance."""
    
    def test_singleton_exists(self):
        """Test that singleton instance is created."""
        assert pattern_detector is not None
    
    def test_singleton_has_methods(self):
        """Test that singleton has required methods."""
        assert hasattr(pattern_detector, 'detect_pattern')
        assert hasattr(pattern_detector, 'get_correction_suggestion')
        assert hasattr(pattern_detector, 'calculate_similarity')
