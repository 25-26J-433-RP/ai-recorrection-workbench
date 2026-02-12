"""
Akura AI - LLM Service (HF Space / Hugging Face / Ollama)

Supports three backends:
- HF Space: free GGUF model server on HuggingFace Spaces
- Hugging Face Inference API: request-based (requires supported model)
- Ollama: local development with fine-tuned model
"""

import asyncio
import json
from typing import Tuple, List, Dict

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings


class LLMService:
    """
    LLM service for Sinhala text correction.
    
    Uses Hugging Face Inference API (request-based, cheap) by default.
    Falls back to Ollama for local development.
    
    The model expects text input and returns JSON:
    - Output: {"correction": "corrected text", "analysis": [...]}
    """
    
    def __init__(self):
        """Initialize the LLM service."""
        self.settings = get_settings()
        self._ollama_llm = None
        self._is_initialized = False
    
    def _get_ollama_llm(self):
        """Lazy initialization of Ollama LLM (for local dev)."""
        if self._ollama_llm is None:
            from langchain_community.llms import Ollama
            self._ollama_llm = Ollama(
                base_url=self.settings.ollama_base_url,
                model=self.settings.ollama_model,
                temperature=self.settings.model_temperature,
                timeout=self.settings.ollama_timeout,
            )
            logger.info(f"Initialized Ollama: {self.settings.ollama_model}")
        return self._ollama_llm
    
    def _invoke_hf_space(self, text: str) -> str:
        """Call our HuggingFace Space model server (sync, runs in thread)."""
        url = self.settings.hf_space_url.rstrip("/") + "/predict"
        payload = {
            "text": text,
            "max_tokens": self.settings.model_max_tokens,
            "temperature": self.settings.model_temperature,
        }
        with httpx.Client(timeout=self.settings.hf_api_timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
        return result.get("generated_text", "")
    
    def _invoke_huggingface(self, text: str) -> str:
        """Call Hugging Face Inference API (sync, runs in thread)."""
        url = f"https://api-inference.huggingface.co/models/{self.settings.hf_model_id}"
        headers = {"Authorization": f"Bearer {self.settings.hf_api_token}"}
        payload = {
            "inputs": text,
            "parameters": {
                "max_new_tokens": self.settings.model_max_tokens,
                "temperature": self.settings.model_temperature,
                "return_full_text": False,
                "do_sample": True,
            },
        }
        with httpx.Client(timeout=self.settings.hf_api_timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            result = response.json()
            
            # HF returns {"error": "Model is loading...", "estimated_time": N} when cold
            if isinstance(result, dict) and "error" in result:
                if "loading" in result.get("error", "").lower():
                    est = result.get("estimated_time", 30)
                    raise RuntimeError(f"Model loading, retry in ~{est}s")
                raise RuntimeError(result.get("error", "HF API error"))
            
            response.raise_for_status()
        
        # HF text-generation returns [{"generated_text": "..."}]
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "")
        if isinstance(result, dict):
            for key in ("generated_text", "output", "text", "response"):
                if key in result:
                    return result[key] or ""
        return str(result) if result else ""
    
    async def _invoke(self, text: str) -> str:
        """Invoke the configured LLM backend."""
        provider = self.settings.llm_provider
        
        if provider == "hf_space":
            if not self.settings.hf_space_url:
                raise ValueError("HF_SPACE_URL required when LLM_PROVIDER=hf_space")
            return await asyncio.to_thread(self._invoke_hf_space, text)
        elif provider == "huggingface":
            if not self.settings.hf_api_token:
                raise ValueError("HF_API_TOKEN required when LLM_PROVIDER=huggingface")
            return await asyncio.to_thread(self._invoke_huggingface, text)
        else:
            # Ollama (local)
            llm = self._get_ollama_llm()
            return await asyncio.to_thread(llm.invoke, text)
    
    async def initialize(self) -> bool:
        """
        Initialize the LLM service and verify connection.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            provider = self.settings.llm_provider
            if provider == "hf_space":
                if not self.settings.hf_space_url:
                    logger.warning("HF_SPACE_URL not set; set LLM_PROVIDER=ollama for local dev")
                    return False
                self._is_initialized = True
                logger.info(f"LLM: HF Space ({self.settings.hf_space_url}) - free")
            elif provider == "huggingface":
                if not self.settings.hf_api_token:
                    logger.warning("HF_API_TOKEN not set; set LLM_PROVIDER=ollama for local dev")
                    return False
                self._is_initialized = True
                logger.info(f"LLM: Hugging Face ({self.settings.hf_model_id}) - request-based")
            else:
                _ = self._get_ollama_llm()
                self._is_initialized = True
                logger.info(f"LLM: Ollama ({self.settings.ollama_model})")
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
            if self._is_initialized:
                provider = self.settings.llm_provider
                if provider == "hf_space":
                    return True, f"HF Space ({self.settings.hf_space_url}) ready"
                elif provider == "huggingface":
                    return True, f"Hugging Face ({self.settings.hf_model_id}) ready"
                return True, f"Ollama ({self.settings.ollama_model}) connected"
            
            # Try to initialize
            ok = await self.initialize()
            return ok, "initialized" if ok else "not initialized"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False, str(e)
    
    async def correct_word(self, word: str) -> Tuple[str, float, str]:
        """
        Correct a single Sinhala word using the configured LLM.
        
        Args:
            word: The single Sinhala word to correct
            
        Returns:
            Tuple of (corrected_word, confidence_score, error_type)
        """
        try:
            response = await self._invoke(word)
            
            if not response:
                logger.warning(f"Empty response for word: {word}")
                return word, 1.0, ""
            
            corrected, error_type = self._parse_word_response(response.strip(), word)
            
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
            if not word.strip():
                results.append((word, word, 1.0, ""))
                continue
            corrected, confidence, error_type = await self.correct_word(word)
            results.append((word, corrected, confidence, error_type))
        return results
    
    def _parse_word_response(self, response: str, original_word: str) -> Tuple[str, str]:
        """Parse the model response for a single word correction."""
        response = response.strip()
        error_type = ""
        
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
                    
                    corrected_words = correction.split()
                    if corrected_words:
                        return corrected_words[0], error_type
                    return correction, error_type
        except (json.JSONDecodeError, Exception):
            pass
        
        corrected = response.split()[0] if response.split() else original_word
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
        Correct Sinhala text using the configured LLM.
        
        Args:
            text: The Sinhala text to correct
            
        Returns:
            Tuple of (corrected_text, confidence_score)
        """
        try:
            response = await self._invoke(text)
            
            if not response:
                logger.warning("Empty response from LLM")
                return text, 0.0
            
            corrected, confidence, _ = self._parse_response(response.strip(), text)
            logger.debug(f"Corrected text with confidence {confidence}")
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
            response = await self._invoke(text)
            
            if not response:
                logger.warning("Empty response from LLM")
                return text, 0.0, []
            
            logger.debug(f"Raw model response (first 500 chars): {response[:500] if len(response) > 500 else response}")
            
            corrected, confidence, analysis = self._parse_response(response.strip(), text)
            
            logger.info(f"Parsed analysis: {len(analysis)} errors found")
            for i, err in enumerate(analysis):
                logger.info(f"  Error {i+1}: word='{err.get('word', '')}', type='{err.get('type', '')}', suggestion='{err.get('suggestion', '')}'")
            
            return corrected, confidence, analysis
            
        except Exception as e:
            logger.error(f"Error correcting text with analysis: {e}")
            return text, 0.0, []
    
    def _parse_response(self, response: str, original_text: str) -> Tuple[str, float, List[Dict]]:
        """Parse the model response, handling both JSON and plain text formats."""
        response = response.strip()
        
        try:
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
            
            if "{" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    data = json.loads(json_str)
                    
                    correction = data.get("correction", original_text)
                    analysis = data.get("analysis", [])
                    
                    if analysis:
                        confidence = 0.9
                    elif correction != original_text:
                        confidence = 0.8
                    else:
                        confidence = 1.0
                    
                    return correction, confidence, analysis
        except (json.JSONDecodeError, Exception):
            pass
        
        corrected = response
        prefixes_to_remove = ["Corrected output:", "Output:", "Correction:", "corrected:"]
        for prefix in prefixes_to_remove:
            if corrected.lower().startswith(prefix.lower()):
                corrected = corrected[len(prefix):].strip()
        
        if corrected.startswith('"') and corrected.endswith('"'):
            corrected = corrected[1:-1]
        if corrected.startswith("'") and corrected.endswith("'"):
            corrected = corrected[1:-1]
        
        confidence = 0.75 if corrected != original_text else 1.0
        return corrected, confidence, []
    
    def get_model_name(self) -> str:
        """Get the name of the currently configured model."""
        provider = self.settings.llm_provider
        if provider == "hf_space":
            return f"hf-space ({self.settings.hf_space_url})"
        elif provider == "huggingface":
            return self.settings.hf_model_id
        return self.settings.ollama_model


# Create singleton instance
llm_service = LLMService()
