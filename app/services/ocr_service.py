"""
Akura AI - OCR Service

This module provides OCR (Optical Character Recognition) for Sinhala handwritten text.

Supports two modes:
1. External: Uses sinhala-ocr-service via API Gateway (Google Cloud Vision)
2. Internal: Uses Gemini Vision API directly (fallback)
"""

import base64
import uuid
import httpx
from typing import Optional, Tuple, Dict, Any
from loguru import logger

from app.core.config import get_settings
from app.services.external_services import external_services


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
        """Check if the OCR service is properly configured (internal or external)."""
        return bool(self.api_key) or external_services.is_ocr_configured()
    
    async def extract_text_from_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        filename: str = "image.jpg",
        image_id: Optional[str] = None
    ) -> Tuple[bool, str, float]:
        """
        Extract Sinhala text from an image.
        
        First tries external sinhala-ocr-service if configured,
        then falls back to internal Gemini Vision API.
        
        Args:
            image_bytes: Raw bytes of the image
            mime_type: MIME type of the image (e.g., "image/jpeg", "image/png")
            filename: Original filename (for external service)
            image_id: Optional image ID for tracking (auto-generated if not provided)
            
        Returns:
            Tuple of (success, extracted_text_or_error, confidence)
        """
        # Generate image_id if not provided
        if not image_id:
            image_id = str(uuid.uuid4())
        
        # Try external OCR service first if configured
        if external_services.is_ocr_configured():
            logger.info("Using external sinhala-ocr-service")
            success, result = await external_services.call_ocr(
                image_bytes=image_bytes,
                filename=filename,
                image_id=image_id
            )
            
            if success:
                cleaned_text = result.get("cleaned_text", "")
                if cleaned_text:
                    logger.info(f"External OCR extracted {len(cleaned_text)} characters")
                    return True, cleaned_text, 0.95  # Higher confidence for Cloud Vision
                else:
                    logger.warning("External OCR returned empty text, falling back to Gemini")
            else:
                logger.warning(f"External OCR failed: {result.get('error')}, falling back to Gemini")
        
        # Fallback to internal Gemini OCR
        return await self._internal_gemini_ocr(image_bytes, mime_type)
    
    async def _internal_gemini_ocr(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Tuple[bool, str, float]:
        """
        Internal OCR using Gemini Vision API.
        
        Args:
            image_bytes: Raw bytes of the image
            mime_type: MIME type of the image
            
        Returns:
            Tuple of (success, extracted_text_or_error, confidence)
        """
        if not self.api_key:
            logger.warning("Internal OCR not configured - missing GEMINI_API_KEY")
            return False, "OCR service not configured. Please set GEMINI_API_KEY or enable external OCR.", 0.0
        
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
        # Check external OCR first
        if external_services.is_ocr_configured():
            is_healthy, msg = await external_services.check_ocr_health()
            if is_healthy:
                return True, f"External OCR: {msg}"
            # Fall through to check internal
        
        # Check internal Gemini OCR
        if self.api_key:
            return True, f"Internal OCR configured with model: {self.model}"
        
        return False, "No OCR service configured (set GEMINI_API_KEY or enable external OCR)"


# Create singleton instance
ocr_service = OcrService()
