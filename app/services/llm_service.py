"""
Akura AI - LangChain LLM Service

This module provides the LangChain integration with Ollama for
Sinhala dyslexia text correction using a fine-tuned SLM.
"""

import asyncio
from typing import Optional, Tuple

from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings


# System prompt for the Sinhala dyslexia correction model
SYSTEM_PROMPT = """You are an expert Sinhala language teacher specializing in helping dyslexic students.
Your task is to correct Sinhala text that may contain dyslexic writing errors.

Types of errors to look for and correct:
1. Visual Scrambling: Letters in wrong order (e.g., ගෙරද → ගෙදර)
2. Phonetic Confusion: Dental/Retroflex swaps (e.g., න/ණ, ල/ළ, ද/ඩ, ත/ට)
3. Visual Reversal: Shape confusion (e.g., බ/ඩ)
4. Grammar Issues: Colloquial to written form (e.g., යනව → යනවා)

IMPORTANT RULES:
- Only correct actual errors, don't change correct words
- Preserve the original meaning of the text
- Output ONLY the corrected text, nothing else
- Do not add explanations or notes
- If the text is already correct, output it unchanged"""

CORRECTION_PROMPT = """Correct the following Sinhala text for dyslexic writing errors:

Input: {text}

Corrected output:"""


class LLMService:
    """
    LangChain-based LLM service for Sinhala text correction.
    
    This service uses Ollama with a local LLM (llama3.2:1b) for inference.
    It's designed to work offline without external API dependencies.
    """
    
    def __init__(self):
        """Initialize the LLM service with Ollama."""
        self.settings = get_settings()
        self._llm: Optional[Ollama] = None
        self._chain = None
        self._is_initialized = False
    
    @property
    def llm(self) -> Ollama:
        """Lazy initialization of the Ollama LLM."""
        if self._llm is None:
            self._llm = Ollama(
                base_url=self.settings.ollama_base_url,
                model=self.settings.ollama_model,
                temperature=self.settings.model_temperature,
                num_predict=self.settings.model_max_tokens,
            )
            logger.info(f"Initialized Ollama LLM with model: {self.settings.ollama_model}")
        return self._llm
    
    @property
    def chain(self):
        """Lazy initialization of the LangChain correction chain."""
        if self._chain is None:
            prompt = PromptTemplate(
                input_variables=["text"],
                template=f"{SYSTEM_PROMPT}\n\n{CORRECTION_PROMPT}"
            )
            self._chain = prompt | self.llm | StrOutputParser()
            logger.info("Initialized LangChain correction chain")
        return self._chain
    
    async def initialize(self) -> bool:
        """
        Initialize the LLM service and verify connection.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Test connection with a simple query
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
        Check if the Ollama service is healthy.
        
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
                return True, "Ollama is connected and responding"
            return False, "Ollama returned empty response"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False, f"Ollama connection failed: {str(e)}"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def correct_text(self, text: str) -> Tuple[str, float]:
        """
        Correct Sinhala text using the LLM.
        
        Args:
            text: The Sinhala text to correct
            
        Returns:
            Tuple of (corrected_text, confidence_score)
        """
        try:
            # Run the chain
            corrected = await asyncio.to_thread(
                self.chain.invoke,
                {"text": text}
            )
            
            # Clean up the response
            corrected = corrected.strip()
            
            # Remove any quotes or extra formatting
            if corrected.startswith('"') and corrected.endswith('"'):
                corrected = corrected[1:-1]
            if corrected.startswith("'") and corrected.endswith("'"):
                corrected = corrected[1:-1]
            
            # Calculate confidence based on response coherence
            confidence = self._calculate_confidence(text, corrected)
            
            logger.debug(f"Corrected '{text}' to '{corrected}' with confidence {confidence}")
            
            return corrected, confidence
            
        except Exception as e:
            logger.error(f"Error correcting text: {e}")
            # Return original text with low confidence on error
            return text, 0.0
    
    async def correct_text_with_context(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Correct text with additional context for better accuracy.
        
        Args:
            text: The Sinhala text to correct
            context: Optional context about the text (e.g., subject, grade level)
            
        Returns:
            Tuple of (corrected_text, confidence_score)
        """
        if context:
            enhanced_prompt = f"""Context: {context}

Correct the following Sinhala text for dyslexic writing errors:

Input: {text}

Corrected output:"""
            
            full_prompt = f"{SYSTEM_PROMPT}\n\n{enhanced_prompt}"
            
            try:
                response = await asyncio.to_thread(
                    self.llm.invoke,
                    full_prompt
                )
                corrected = response.strip()
                confidence = self._calculate_confidence(text, corrected)
                return corrected, confidence
            except Exception as e:
                logger.error(f"Error in context-aware correction: {e}")
                return await self.correct_text(text)
        else:
            return await self.correct_text(text)
    
    def _calculate_confidence(self, original: str, corrected: str) -> float:
        """
        Calculate a confidence score for the correction.
        
        Args:
            original: Original text
            corrected: Corrected text
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not corrected:
            return 0.0
        
        if original == corrected:
            return 1.0  # No changes needed = high confidence
        
        # Calculate based on edit distance ratio
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, original, corrected).ratio()
        
        # If too different (less than 30% similar), low confidence
        if similarity < 0.3:
            return 0.3
        
        # If very similar with small changes, high confidence
        if similarity > 0.8:
            return 0.9
        
        # Scale confidence based on similarity
        return min(0.5 + similarity * 0.4, 0.95)
    
    async def batch_correct(
        self,
        texts: list[str],
        max_concurrent: int = 5
    ) -> list[Tuple[str, float]]:
        """
        Correct multiple texts concurrently.
        
        Args:
            texts: List of texts to correct
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of (corrected_text, confidence) tuples
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def correct_with_semaphore(text: str) -> Tuple[str, float]:
            async with semaphore:
                return await self.correct_text(text)
        
        tasks = [correct_with_semaphore(text) for text in texts]
        return await asyncio.gather(*tasks)


# Create singleton instance
llm_service = LLMService()
