"""
Akura AI - External Services Client

This module provides HTTP clients for calling external microservices
through the API Gateway or directly.

Services:
- sinhala-ocr-service: Handwritten essay OCR
- dyslexic-pattern-detection-service: Binary dyslexia detection + pattern classification
"""

import httpx
from typing import Optional, Tuple, Dict, Any
from loguru import logger

from app.core.config import get_settings


class ExternalServicesClient:
    """
    Client for calling external microservices via API Gateway.
    
    Supports both gateway-based routing and direct service calls.
    """
    
    def __init__(self):
        """Initialize the external services client."""
        self.settings = get_settings()
        self._ocr_timeout = 60.0  # OCR can take time for large images
        self._pattern_timeout = 30.0  # Pattern detection is faster
    
    @property
    def gateway_url(self) -> str:
        """Get the API gateway URL (without trailing slash)."""
        return self.settings.api_gateway_url.rstrip("/") if self.settings.api_gateway_url else ""
    
    @property
    def ocr_service_url(self) -> str:
        """Get the OCR service URL (direct or via gateway)."""
        if self.settings.ocr_service_url:
            return self.settings.ocr_service_url.rstrip("/")
        if self.gateway_url:
            return f"{self.gateway_url}/sinhala-ocr-service"
        return ""
    
    @property
    def pattern_service_url(self) -> str:
        """Get the pattern detection service URL (direct or via gateway)."""
        if self.settings.pattern_service_url:
            return self.settings.pattern_service_url.rstrip("/")
        if self.gateway_url:
            return f"{self.gateway_url}/dyslexic-pattern-detection-service"
        return ""
    
    def is_ocr_configured(self) -> bool:
        """Check if external OCR service is configured and enabled."""
        return self.settings.use_external_ocr and bool(self.ocr_service_url)
    
    def is_patterns_configured(self) -> bool:
        """Check if external pattern service is configured and enabled."""
        return self.settings.use_external_patterns and bool(self.pattern_service_url)
    
    # =========================================================================
    # OCR Service Methods
    # =========================================================================
    
    async def call_ocr(
        self,
        image_bytes: bytes,
        filename: str,
        image_id: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Call sinhala-ocr-service for handwritten text extraction.
        
        Args:
            image_bytes: Raw image bytes
            filename: Original filename
            image_id: Unique image identifier for tracking
            
        Returns:
            Tuple of (success, result_dict)
            On success: {image_id, cleaned_text, raw_text, image_url, filename}
            On failure: {error: str}
        """
        if not self.ocr_service_url:
            return False, {"error": "OCR service not configured"}
        
        url = f"{self.ocr_service_url}/ocr"
        logger.info(f"Calling external OCR service: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self._ocr_timeout) as client:
                # Prepare multipart form data
                files = {"file": (filename, image_bytes, "image/jpeg")}
                data = {"image_id": image_id}
                
                response = await client.post(url, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"OCR successful: {len(result.get('cleaned_text', ''))} chars extracted")
                    return True, result
                else:
                    error_msg = f"OCR service returned {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", error_msg)
                    except:
                        pass
                    logger.error(f"OCR failed: {error_msg}")
                    return False, {"error": error_msg}
                    
        except httpx.TimeoutException:
            logger.error("OCR service request timed out")
            return False, {"error": "OCR request timed out"}
        except httpx.RequestError as e:
            logger.error(f"OCR service request failed: {e}")
            return False, {"error": f"OCR service unavailable: {e}"}
        except Exception as e:
            logger.error(f"OCR service call failed: {e}")
            return False, {"error": str(e)}
    
    async def check_ocr_health(self) -> Tuple[bool, str]:
        """
        Check if the OCR service is healthy.
        
        Returns:
            Tuple of (is_healthy, status_message)
        """
        if not self.ocr_service_url:
            return False, "OCR service not configured"
        
        url = f"{self.ocr_service_url}/health"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return True, "OCR service is healthy"
                return False, f"OCR service returned {response.status_code}"
        except Exception as e:
            return False, f"OCR service unavailable: {e}"
    
    # =========================================================================
    # Pattern Detection Service Methods
    # =========================================================================
    
    async def predict_dyslexia_binary(self, text: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Call dyslexic-pattern-detection-service for binary dyslexia classification.
        
        Args:
            text: Sinhala essay text to classify
            
        Returns:
            Tuple of (success, result_dict)
            On success: {is_dyslexic: bool, confidence: float, label: str}
            On failure: {error: str}
        """
        if not self.pattern_service_url:
            return False, {"error": "Pattern detection service not configured"}
        
        url = f"{self.pattern_service_url}/predict/binary"
        logger.info(f"Calling binary dyslexia prediction: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self._pattern_timeout) as client:
                response = await client.post(url, json={"text": text})
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Binary prediction: {result.get('label')} (confidence: {result.get('confidence', 0):.2f})")
                    return True, result
                else:
                    error_msg = f"Pattern service returned {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", error_msg)
                    except:
                        pass
                    logger.error(f"Binary prediction failed: {error_msg}")
                    return False, {"error": error_msg}
                    
        except httpx.TimeoutException:
            logger.error("Pattern detection request timed out")
            return False, {"error": "Pattern detection request timed out"}
        except httpx.RequestError as e:
            logger.error(f"Pattern detection request failed: {e}")
            return False, {"error": f"Pattern service unavailable: {e}"}
        except Exception as e:
            logger.error(f"Pattern detection call failed: {e}")
            return False, {"error": str(e)}
    
    async def predict_dyslexia_patterns(self, text: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Call dyslexic-pattern-detection-service for multi-label pattern classification.
        
        Args:
            text: Sinhala essay text to analyze
            
        Returns:
            Tuple of (success, result_dict)
            On success: {patterns: list[str], confidences: dict[str, float]}
            On failure: {error: str}
        """
        if not self.pattern_service_url:
            return False, {"error": "Pattern detection service not configured"}
        
        url = f"{self.pattern_service_url}/predict/patterns"
        logger.info(f"Calling multi-label pattern prediction: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self._pattern_timeout) as client:
                response = await client.post(url, json={"text": text})
                
                if response.status_code == 200:
                    result = response.json()
                    patterns = result.get("patterns", [])
                    logger.info(f"Pattern prediction: {len(patterns)} patterns detected")
                    return True, result
                else:
                    error_msg = f"Pattern service returned {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", error_msg)
                    except:
                        pass
                    logger.error(f"Pattern prediction failed: {error_msg}")
                    return False, {"error": error_msg}
                    
        except httpx.TimeoutException:
            logger.error("Pattern detection request timed out")
            return False, {"error": "Pattern detection request timed out"}
        except httpx.RequestError as e:
            logger.error(f"Pattern detection request failed: {e}")
            return False, {"error": f"Pattern service unavailable: {e}"}
        except Exception as e:
            logger.error(f"Pattern detection call failed: {e}")
            return False, {"error": str(e)}
    
    async def check_pattern_health(self) -> Tuple[bool, str]:
        """
        Check if the pattern detection service is healthy.
        
        Returns:
            Tuple of (is_healthy, status_message)
        """
        if not self.pattern_service_url:
            return False, "Pattern detection service not configured"
        
        url = f"{self.pattern_service_url}/health"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return True, "Pattern detection service is healthy"
                return False, f"Pattern detection service returned {response.status_code}"
        except Exception as e:
            return False, f"Pattern detection service unavailable: {e}"
    
    # =========================================================================
    # Combined Health Check
    # =========================================================================
    
    async def check_all_services(self) -> Dict[str, Any]:
        """
        Check health of all configured external services.
        
        Returns:
            Dict with service status information
        """
        result = {
            "gateway_configured": bool(self.gateway_url),
            "gateway_url": self.gateway_url or None,
            "services": {}
        }
        
        # Check OCR service
        if self.is_ocr_configured():
            ocr_healthy, ocr_msg = await self.check_ocr_health()
            result["services"]["ocr"] = {
                "enabled": True,
                "url": self.ocr_service_url,
                "healthy": ocr_healthy,
                "message": ocr_msg
            }
        else:
            result["services"]["ocr"] = {
                "enabled": False,
                "message": "External OCR disabled (using internal Gemini OCR)"
            }
        
        # Check pattern detection service
        if self.is_patterns_configured():
            pattern_healthy, pattern_msg = await self.check_pattern_health()
            result["services"]["pattern_detection"] = {
                "enabled": True,
                "url": self.pattern_service_url,
                "healthy": pattern_healthy,
                "message": pattern_msg
            }
        else:
            result["services"]["pattern_detection"] = {
                "enabled": False,
                "message": "External pattern detection disabled (using internal detection)"
            }
        
        return result


# Singleton instance
external_services = ExternalServicesClient()
