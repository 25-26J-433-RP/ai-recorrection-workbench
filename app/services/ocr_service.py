"""
Akura AI - OCR Service

This module provides OCR (Optical Character Recognition) for Sinhala handwritten text
using Google Gemini Vision API. All OCR processing is done server-side.
"""

import base64
import httpx
from typing import Optional, Tuple
from loguru import logger

from app.core.config import get_settings


# OCR prompt optimized for Sinhala handwritten text extraction
OCR_PROMPT = """You are an expert OCR system specialized in reading Sinhala (සිංහල) handwritten text from student essays. 

Your task:
1. Carefully examine this image of a student's handwritten essay
2. Extract ALL the Sinhala text exactly as written (including any spelling mistakes or errors)
3. Preserve the original writing - do NOT correct any mistakes
4. If there are multiple lines, preserve line breaks
5. If you cannot read certain characters, use [?] to indicate unclear text

Important: Extract the EXACT text as written by the student, including any dyslexia-related errors like:
- Scrambled letters (e.g., "ගෙරද" instead of "ගෙදර")
- Missing vowel signs
- Phonetic confusions
- Grammar errors

Respond ONLY with the extracted Sinhala text, nothing else. No explanations, no translations, just the raw text."""


class OcrService:
    """
    OCR service for extracting Sinhala text from images using Gemini Vision API.
    
    This service runs entirely on the backend, keeping API keys secure
    and providing consistent OCR results.
    """
    
    def __init__(self):
        """Initialize the OCR service."""
        self.settings = get_settings()
        self._api_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    @property
    def api_key(self) -> str:
        """Get the Gemini API key."""
        return self.settings.gemini_api_key
    
    @property
    def model(self) -> str:
        """Get the Gemini model name."""
        return self.settings.gemini_model
    
    def is_configured(self) -> bool:
        """Check if the OCR service is properly configured."""
        return bool(self.api_key)
    
    async def extract_text_from_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Tuple[bool, str, float]:
        """
        Extract Sinhala text from an image using Gemini Vision API.
        
        Args:
            image_bytes: Raw bytes of the image
            mime_type: MIME type of the image (e.g., "image/jpeg", "image/png")
            
        Returns:
            Tuple of (success, extracted_text_or_error, confidence)
        """
        if not self.is_configured():
            logger.warning("OCR service not configured - missing GEMINI_API_KEY")
            return False, "OCR service not configured. Please set GEMINI_API_KEY.", 0.0
        
        try:
            # Convert image to base64
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            
            # Build request payload
            request_body = {
                "contents": [
                    {
                        "parts": [
                            {"text": OCR_PROMPT},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,  # Low temperature for accurate extraction
                    "topK": 1,
                    "topP": 1,
                    "maxOutputTokens": 2048
                }
            }
            
            # Make API request
            url = f"{self._api_url}/{self.model}:generateContent?key={self.api_key}"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    json=request_body,
                    headers={"Content-Type": "application/json"}
                )
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", f"API error: {response.status_code}")
                logger.error(f"Gemini API error: {error_msg}")
                return False, error_msg, 0.0
            
            data = response.json()
            
            # Extract text from response
            extracted_text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            
            if not extracted_text.strip():
                return False, "No text could be extracted from the image", 0.0
            
            logger.info(f"OCR extracted {len(extracted_text)} characters")
            return True, extracted_text.strip(), 0.9
            
        except httpx.TimeoutException:
            logger.error("OCR request timed out")
            return False, "OCR request timed out. Please try again.", 0.0
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return False, str(e), 0.0
    
    async def check_health(self) -> Tuple[bool, str]:
        """
        Check if the OCR service is healthy and configured.
        
        Returns:
            Tuple of (is_healthy, status_message)
        """
        if not self.is_configured():
            return False, "GEMINI_API_KEY not configured"
        
        return True, f"OCR service configured with model: {self.model}"


# Create singleton instance
ocr_service = OcrService()
