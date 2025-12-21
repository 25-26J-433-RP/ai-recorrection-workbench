"""
Akura AI - LLM Service (Ollama Only)

This module provides direct integration with the fine-tuned Ollama model
for Sinhala dyslexia text correction.
"""

import asyncio
import json
from typing import Optional, Tuple, List, Dict

from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings


class LLMService:
    """
    LLM service for Sinhala text correction using fine-tuned Ollama model.
    
    The model expects JSON input and returns JSON output:
    - Input: {"text": "dyslexic text here"}
    - Output: {"correction": "corrected text", "analysis": [...]}
    """
    
    def __init__(self):
        """Initialize the LLM service."""
        self.settings = get_settings()
        self._llm = None
        self._is_initialized = False
    
    @property
    def llm(self):
        """Lazy initialization of the Ollama LLM."""
        if self._llm is None:
            self._init_ollama()
        return self._llm
    
    def _init_ollama(self):
        """Initialize Ollama LLM with the fine-tuned model."""
        from langchain_community.llms import Ollama
        
        self._llm = Ollama(
            base_url=self.settings.ollama_base_url,
            model=self.settings.ollama_model,
            temperature=self.settings.model_temperature,
            num_predict=self.settings.model_max_tokens,
        )
        logger.info(f"Initialized Ollama LLM with model: {self.settings.ollama_model}")
    
    async def initialize(self) -> bool:
        """
        Initialize the LLM service and verify connection.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Test connection by accessing the llm property
            _ = self.llm
            self._is_initialized = True
            logger.info("LLM service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            self._is_initialized = False
            return False
    
    async def check_health(self) -> Tuple[bool, str]:
        """
        Check if the LLM service is healthy.
        
        Returns:
            Tuple of (is_healthy, status_message)
        """
        try:
            # Try a simple generation to verify the model is working
            response = await asyncio.to_thread(
                self.llm.invoke,
                "Hello"
            )
            if response:
                return True, f"Ollama ({self.settings.ollama_model}) is connected"
            return False, "LLM returned empty response"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False, f"Ollama connection failed: {str(e)}"
    
    async def correct_word(self, word: str) -> Tuple[str, float, str]:
        """
        Correct a single Sinhala word using the fine-tuned Ollama model.
        
        Args:
            word: The single Sinhala word to correct
            
        Returns:
            Tuple of (corrected_word, confidence_score, error_type)
        """
        try:
            response = await asyncio.to_thread(
                self.llm.invoke,
                word
            )
            
            if not response:
                logger.warning(f"Empty response for word: {word}")
                return word, 1.0, ""
            
            # Parse the response for a single word
            corrected, error_type = self._parse_word_response(response.strip(), word)
            
            # Calculate confidence
            if corrected != word:
                confidence = 0.9
            else:
                confidence = 1.0
            
            logger.debug(f"Word '{word}' -> '{corrected}' (type: {error_type})")
            
            return corrected, confidence, error_type
            
        except Exception as e:
            logger.error(f"Error correcting word '{word}': {e}")
            return word, 0.5, ""
    
    async def correct_words_batch(self, words: List[str]) -> List[Tuple[str, str, float, str]]:
        """
        Correct multiple words by processing each through the LLM.
        
        Args:
            words: List of words to correct
            
        Returns:
            List of tuples: (original_word, corrected_word, confidence, error_type)
        """
        results = []
        
        for word in words:
            # Skip empty or whitespace-only words
            if not word.strip():
                results.append((word, word, 1.0, ""))
                continue
            
            corrected, confidence, error_type = await self.correct_word(word)
            results.append((word, corrected, confidence, error_type))
        
        return results
    
    def _parse_word_response(self, response: str, original_word: str) -> Tuple[str, str]:
        """
        Parse the model response for a single word correction.
        
        Args:
            response: Raw response from the model
            original_word: Original input word
            
        Returns:
            Tuple of (corrected_word, error_type)
        """
        response = response.strip()
        error_type = ""
        
        # Try to parse as JSON first
        try:
            if "{" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    data = json.loads(json_str)
                    
                    correction = data.get("correction", original_word)
                    analysis = data.get("analysis", [])
                    
                    if analysis and len(analysis) > 0:
                        error_type = analysis[0].get("type", "")
                    
                    # Extract just the first word from correction
                    corrected_words = correction.split()
                    if corrected_words:
                        return corrected_words[0], error_type
                    return correction, error_type
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.debug(f"Error parsing JSON response: {e}")
        
        # Treat as plain text - get first word
        corrected = response.split()[0] if response.split() else original_word
        
        # Remove quotes
        if corrected.startswith('"') and corrected.endswith('"'):
            corrected = corrected[1:-1]
        if corrected.startswith("'") and corrected.endswith("'"):
            corrected = corrected[1:-1]
        
        return corrected, error_type
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def correct_text(self, text: str) -> Tuple[str, float]:
        """
        Correct Sinhala text using the fine-tuned Ollama model.
        
        The model expects input in the format that matches the training data.
        
        Args:
            text: The Sinhala text to correct
            
        Returns:
            Tuple of (corrected_text, confidence_score)
        """
        try:
            # Send text directly to the model (it was trained on the dataset format)
            response = await asyncio.to_thread(
                self.llm.invoke,
                text
            )
            
            if not response:
                logger.warning("Empty response from Ollama")
                return text, 0.0
            
            # Try to parse JSON response
            corrected, confidence, analysis = self._parse_response(response.strip(), text)
            
            logger.debug(f"Corrected '{text}' to '{corrected}' with confidence {confidence}")
            
            return corrected, confidence
            
        except Exception as e:
            logger.error(f"Error correcting text: {e}")
            return text, 0.0
    
    async def correct_text_with_analysis(self, text: str) -> Tuple[str, float, List[Dict]]:
        """
        Correct Sinhala text and return full analysis.
        
        Args:
            text: The Sinhala text to correct
            
        Returns:
            Tuple of (corrected_text, confidence_score, analysis_list)
        """
        try:
            response = await asyncio.to_thread(
                self.llm.invoke,
                text
            )
            
            if not response:
                logger.warning("Empty response from Ollama")
                return text, 0.0, []
            
            corrected, confidence, analysis = self._parse_response(response.strip(), text)
            
            return corrected, confidence, analysis
            
        except Exception as e:
            logger.error(f"Error correcting text with analysis: {e}")
            return text, 0.0, []
    
    def _parse_response(self, response: str, original_text: str) -> Tuple[str, float, List[Dict]]:
        """
        Parse the model response, handling both JSON and plain text formats.
        
        Args:
            response: Raw response from the model
            original_text: Original input text
            
        Returns:
            Tuple of (corrected_text, confidence, analysis_list)
        """
        # Clean up response
        response = response.strip()
        
        # Try to parse as JSON first
        try:
            # Handle case where response might be wrapped in markdown code blocks
            if response.startswith("```"):
                lines = response.split("\n")
                json_lines = []
                in_block = False
                for line in lines:
                    if line.startswith("```"):
                        in_block = not in_block
                        continue
                    if in_block or not line.startswith("```"):
                        json_lines.append(line)
                response = "\n".join(json_lines).strip()
            
            # Try to find JSON in the response
            if "{" in response:
                # Find the JSON part
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    data = json.loads(json_str)
                    
                    correction = data.get("correction", original_text)
                    analysis = data.get("analysis", [])
                    
                    # Calculate confidence based on analysis
                    if analysis:
                        confidence = 0.9  # High confidence if model provided analysis
                    elif correction != original_text:
                        confidence = 0.8  # Good confidence if there was a correction
                    else:
                        confidence = 1.0  # Original text returned (no errors found)
                    
                    return correction, confidence, analysis
        except json.JSONDecodeError:
            logger.debug("Response is not valid JSON, treating as plain text")
        except Exception as e:
            logger.debug(f"Error parsing JSON: {e}")
        
        # If not JSON, treat as plain text correction
        corrected = response
        
        # Remove common prefixes the model might add
        prefixes_to_remove = [
            "Corrected output:",
            "Output:",
            "Correction:",
            "corrected:",
        ]
        for prefix in prefixes_to_remove:
            if corrected.lower().startswith(prefix.lower()):
                corrected = corrected[len(prefix):].strip()
        
        # Remove quotes if present
        if corrected.startswith('"') and corrected.endswith('"'):
            corrected = corrected[1:-1]
        if corrected.startswith("'") and corrected.endswith("'"):
            corrected = corrected[1:-1]
        
        # Calculate confidence
        if corrected != original_text:
            confidence = 0.75  # Moderate confidence for plain text response
        else:
            confidence = 1.0
        
        return corrected, confidence, []
    
    def get_model_name(self) -> str:
        """Get the name of the currently configured model."""
        return self.settings.ollama_model


# Create singleton instance
llm_service = LLMService()
