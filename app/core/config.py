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
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "production"
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M"
    ollama_timeout: int = 300  # 5 minutes for large essays
    
    # Model Configuration
    model_temperature: float = 0.3
    model_max_tokens: int = 2048  # Increased for large essays
    ai_confidence_threshold: float = 0.7
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:8080"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    # Gemini Configuration (used for OCR and as fallback LLM)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    
    # LLM Provider: "ollama" or "gemini"
    llm_provider: str = "ollama"  # Using fine-tuned Ollama model for text correction
    
    # Database Configuration (Supabase PostgreSQL)
    database_url: str = ""
    
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
