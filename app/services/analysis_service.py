"""
Akura AI - Analysis Service

This module provides the main analysis service that combines
AI-based and rule-based correction with intelligent pattern detection.
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple

from loguru import logger

from app.core.config import get_settings
from app.models.schemas import (
    AnalyzeResponse,
    DyslexiaPatternType,
    WordAnalysis,
    WordType,
)
from app.services.llm_service import llm_service
from app.services.pattern_detector import pattern_detector
from app.services.rule_corrector import rule_corrector


class AnalysisService:
    """
    Main analysis service that orchestrates the hybrid correction pipeline.
    
    This service:
    1. Takes input text
    2. Gets AI-based corrections
    3. Applies rule-based validation/override
    4. Detects dyslexia patterns
    5. Returns structured analysis results
    """
    
    def __init__(self):
        """Initialize the analysis service."""
        self.settings = get_settings()
        self.llm = llm_service
        self.rules = rule_corrector
        self.detector = pattern_detector
    
    async def analyze(
        self,
        text: str,
        include_correct_words: bool = False
    ) -> AnalyzeResponse:
        """
        Perform full analysis on Sinhala text using the fine-tuned LLM.
        
        Model Input: Full sentence (e.g., "මම ගෙරද යනව")
        Model Output: JSON {"correction": "...", "analysis": [{"word": "...", "type": "...", "suggestion": "..."}]}
        
        Args:
            text: The Sinhala text to analyze
            include_correct_words: Whether to include correct words in response
            
        Returns:
            AnalyzeResponse with analysis results
        """
        start_time = time.time()
        
        try:
            # Send full sentence to LLM and get JSON response
            corrected_text, confidence, model_analysis = await self.llm.correct_text_with_analysis(text)
            
            # Build full word analyses (forcing include_correct=True to get complete sentence structure)
            full_analyses = self._build_word_analyses_from_model(
                original_text=text,
                corrected_text=corrected_text,
                model_analysis=model_analysis,
                include_correct=True
            )
            
            # Reconstruct corrected_text from tokens to ensure strict consistency
            # This handles duplicate words correctly by preserving order
            final_corrected_text = self._reconstruct_text_from_tokens(full_analyses)
            
            # Filter for response data if user didn't request correct words
            response_data = full_analyses
            if not include_correct_words:
                response_data = [w for w in full_analyses if w.type == WordType.ERROR]
            
            processing_time = (time.time() - start_time) * 1000
            
            return AnalyzeResponse(
                success=True,
                data=response_data,
                corrected_text=final_corrected_text,
                original_text=text,
                processing_time_ms=round(processing_time, 2),
                model_used=self.llm.get_model_name()
            )
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            # Fallback to rule-based only
            return await self._fallback_analysis(
                text,
                include_correct_words,
                processing_time
            )
    
    async def _analyze_words(
        self,
        original_words: List[str],
        ai_corrected_words: List[str],
        ai_confidence: float,
        include_correct: bool
    ) -> List[WordAnalysis]:
        """
        Analyze each word with hybrid AI + rule-based approach.
        
        Args:
            original_words: List of original words
            ai_corrected_words: List of AI-corrected words
            ai_confidence: Overall AI confidence
            include_correct: Whether to include correct words
            
        Returns:
            List of WordAnalysis objects
        """
        analyses = []
        
        # Handle length mismatch between original and corrected
        max_len = max(len(original_words), len(ai_corrected_words))
        
        for i in range(len(original_words)):
            original = original_words[i]
            
            # Get AI correction for this position
            ai_correction = (
                ai_corrected_words[i] 
                if i < len(ai_corrected_words) 
                else original
            )
            
            # Apply hybrid validation
            final_correction, source, confidence = self.rules.validate_ai_correction(
                original,
                ai_correction,
                ai_confidence
            )
            
            # Detect pattern if there's a correction
            if original != final_correction:
                pattern_type, explanation, pattern_conf = self.detector.detect_pattern(
                    original,
                    final_correction
                )
                
                # Adjust confidence based on pattern detection
                final_confidence = min(confidence, pattern_conf)
                
                analyses.append(WordAnalysis(
                    word=original,
                    type=WordType.ERROR,
                    dyslexia_pattern=pattern_type.value,
                    suggestion=final_correction,
                    explanation=explanation,
                    confidence=round(final_confidence, 2),
                    source=source
                ))
            elif include_correct:
                analyses.append(WordAnalysis(
                    word=original,
                    type=WordType.CORRECT,
                    dyslexia_pattern=None,
                    suggestion=None,
                    explanation=None,
                    confidence=1.0,
                    source=None
                ))
        
        return analyses
    
    def _build_word_analyses_from_model(
        self,
        original_text: str,
        corrected_text: str,
        model_analysis: List[Dict],
        include_correct: bool
    ) -> List[WordAnalysis]:
        """
        Build WordAnalysis list from model's analysis output.
        
        Args:
            original_text: Original input text
            corrected_text: Corrected text from model
            model_analysis: Analysis list from model
            include_correct: Whether to include correct words
            
        Returns:
            List of WordAnalysis objects
        """
        analyses = []
        original_words = original_text.split()
        
        # Create a set of words that have errors
        error_words = {item.get("word", "") for item in model_analysis}
        
        for word in original_words:
            # Check if this word has an error
            error_item = next(
                (item for item in model_analysis if item.get("word") == word),
                None
            )
            
            if error_item:
                analyses.append(WordAnalysis(
                    word=word,
                    type=WordType.ERROR,
                    dyslexia_pattern=error_item.get("type", "Unknown"),
                    suggestion=error_item.get("suggestion", word),
                    explanation=f"Detected: {error_item.get('type', 'Unknown')}",
                    confidence=0.9,
                    source="ai"
                ))
            elif include_correct:
                analyses.append(WordAnalysis(
                    word=word,
                    type=WordType.CORRECT,
                    dyslexia_pattern=None,
                    suggestion=None,
                    explanation=None,
                    confidence=1.0,
                    source=None
                ))
        
        return analyses
    
    def _reconstruct_text_from_tokens(self, analyses: List[WordAnalysis]) -> str:
        """
        Reconstruct the full corrected text string from the ordered list of tokens.
        
        Args:
            analyses: List of WordAnalysis objects (must cover full sentence)
            
        Returns:
            The reconstructed corrected text string
        """
        words = []
        for analysis in analyses:
            if analysis.type == WordType.ERROR and analysis.suggestion:
                words.append(analysis.suggestion)
            else:
                words.append(analysis.word)
        return " ".join(words)

    def _build_corrected_text(
        self,
        original_words: List[str],
        analyses: List[WordAnalysis]
    ) -> str:
        """
        Deprecated: Use _reconstruct_text_from_tokens instead.
        Build the final corrected text from word analyses.
        """
        # Create a map of original word to correction
        correction_map = {}
        for analysis in analyses:
            if analysis.type == WordType.ERROR and analysis.suggestion:
                correction_map[analysis.word] = analysis.suggestion
        
        # Build corrected text
        corrected = []
        for word in original_words:
            if word in correction_map:
                corrected.append(correction_map[word])
            else:
                corrected.append(word)
        
        return " ".join(corrected)
    
    async def _fallback_analysis(
        self,
        text: str,
        include_correct: bool,
        elapsed_time: float
    ) -> AnalyzeResponse:
        """
        Fallback to pure rule-based analysis when AI fails.
        
        Args:
            text: Original text
            include_correct: Whether to include correct words
            elapsed_time: Time already spent
            
        Returns:
            AnalyzeResponse from rule-based analysis
        """
        logger.warning("Falling back to rule-based analysis only")
        
        corrected_text, corrections = self.rules.correct_text(text)
        
        analyses = []
        original_words = text.split()
        corrected_words = corrected_text.split()
        
        for i, original in enumerate(original_words):
            # Check if this word was corrected
            correction_info = next(
                (c for c in corrections if c["original"] == original),
                None
            )
            
            if correction_info:
                analyses.append(WordAnalysis(
                    word=original,
                    type=WordType.ERROR,
                    dyslexia_pattern=correction_info["pattern"],
                    suggestion=correction_info["corrected"],
                    explanation=f"Rule-based correction applied.",
                    confidence=correction_info["confidence"],
                    source="rule-based"
                ))
            elif include_correct:
                analyses.append(WordAnalysis(
                    word=original,
                    type=WordType.CORRECT,
                    dyslexia_pattern=None,
                    suggestion=None,
                    explanation=None,
                    confidence=1.0,
                    source=None
                ))
        
        return AnalyzeResponse(
            success=True,
            data=analyses,
            corrected_text=corrected_text,
            original_text=text,
            processing_time_ms=round(elapsed_time, 2),
            model_used="rule-based (fallback)"
        )
    
    async def analyze_batch(
        self,
        texts: List[str],
        include_correct: bool = False
    ) -> List[AnalyzeResponse]:
        """
        Analyze multiple texts concurrently.
        
        Args:
            texts: List of texts to analyze
            include_correct: Whether to include correct words
            
        Returns:
            List of AnalyzeResponse objects
        """
        tasks = [
            self.analyze(text, include_correct)
            for text in texts
        ]
        return await asyncio.gather(*tasks)
    
    async def quick_check(self, text: str) -> bool:
        """
        Quick check if text contains any errors.
        
        Args:
            text: The text to check
            
        Returns:
            True if errors detected, False otherwise
        """
        # Use rule-based check first (faster)
        _, corrections = self.rules.correct_text(text)
        
        if corrections:
            return True
        
        # Fall back to AI check
        try:
            corrected, confidence = await self.llm.correct_text(text)
            return corrected != text and confidence > 0.5
        except Exception:
            return False


# Create singleton instance
analysis_service = AnalysisService()
