"""
Akura AI - Configuration Module

This module handles all application configuration using Pydantic Settings.
Configuration can be loaded from environment variables or .env file.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    class Config:
        protected_namespaces = ()

    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "production"
    
    # Ollama Configuration (local development)
    ollama_base_url: str = "http://20.212.24.114:11434"
    ollama_model: str = "hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M"
    ollama_timeout: int = 300  # 5 minutes for large essays
    
    # Dual Model Configuration (Akura primary + secondary model via Ollama)
    enable_dual_model: bool = True  # Enable dual-model pipeline
    secondary_ollama_model: str = "gemini-3-flash-preview:latest"  # Secondary model in Ollama
    secondary_ollama_timeout: int = 300  # Timeout for secondary model
    secondary_ollama_temperature: float = 0.3  # Temperature for secondary corrections
    
    # Hugging Face Inference API (request-based)
    hf_api_token: str = ""  # Get from https://huggingface.co/settings/tokens
    hf_model_id: str = "hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit"
    hf_api_timeout: int = 120  # seconds per request
    
    # HuggingFace Space (free GGUF model server)
    hf_space_url: str = ""  # e.g. https://hasinduOnline-akura-ai-model.hf.space
    
    # Model Configuration
    model_temperature: float = 0.3
    model_max_tokens: int = 2048  # Increased for large essays
    ai_confidence_threshold: float = 0.7
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # CORS Configuration - Include Expo dev server ports
    allowed_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:8080,http://localhost:8081,http://localhost:19000,http://localhost:19001,http://localhost:19006,http://127.0.0.1:8081,http://127.0.0.1:19006"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    # Gemini Configuration (used for OCR and as fallback LLM)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    
    # LLM Provider: "hf_space" (free), "huggingface", "ollama" (local), or "gemini"
    llm_provider: str = "hf_space"  # HF Space = free GGUF model server
    
    # Database Configuration (Supabase PostgreSQL)
    database_url: str = ""
    
    # API Gateway / External Microservices Configuration
    api_gateway_url: str = ""                    # e.g., "http://localhost:8000" (gateway URL)
    use_external_ocr: bool = False               # Use sinhala-ocr-service via gateway
    use_external_patterns: bool = False          # Use dyslexic-pattern-detection-service via gateway
    
    # Direct service URLs (fallback if not using gateway)
    ocr_service_url: str = ""                    # Direct OCR service URL  
    pattern_service_url: str = ""                # Direct pattern detection URL
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: The application settings instance.
    """
    return Settings()
