"""
Akura AI - Pydantic Models

This module defines all data models for the API request/response handling.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DyslexiaPatternType(str, Enum):
    """Enumeration of dyslexia pattern types."""
    
    VISUAL_SCRAMBLING = "Visual Sequencing (Scrambled)"
    PHONETIC_CONFUSION = "Phonetic Confusion (Dental/Retroflex)"
    VISUAL_REVERSAL = "Visual Reversal (Shape Confusion)"
    GRAMMAR_SPOKEN = "Grammar (Spoken vs Written)"
    UNKNOWN = "Unknown Pattern"


class WordType(str, Enum):
    """Type of word analysis result."""
    
    ERROR = "error"
    CORRECT = "correct"


class AnalyzeRequest(BaseModel):
    """Request model for the /analyze endpoint."""
    
    text: str = Field(
        ...,
        description="The Sinhala text to analyze for dyslexic errors",
        min_length=1,
        max_length=5000,
        examples=["මම ගෙරද යනව"]
    )
    
    include_correct_words: bool = Field(
        default=False,
        description="Whether to include correctly spelled words in the response"
    )


class WordAnalysis(BaseModel):
    """Analysis result for a single word."""
    
    word: str = Field(
        ...,
        description="The original word from the input text"
    )
    
    type: WordType = Field(
        ...,
        description="Whether the word is an error or correct"
    )
    
    dyslexia_pattern: Optional[str] = Field(
        default=None,
        alias="dyslexiaPattern",
        description="The detected dyslexia pattern type"
    )
    
    suggestion: Optional[str] = Field(
        default=None,
        description="The suggested correction for the word"
    )
    
    explanation: Optional[str] = Field(
        default=None,
        description="Human-readable explanation of the error and correction"
    )
    
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score of the correction (0.0 to 1.0)"
    )
    
    source: Optional[str] = Field(
        default=None,
        description="Source of the correction (ai, rule-based, or hybrid)"
    )
    
    class Config:
        populate_by_name = True


class AnalyzeResponse(BaseModel):
    """Response model for the /analyze endpoint."""
    
    success: bool = Field(
        ...,
        description="Whether the analysis was successful"
    )
    
    data: List[WordAnalysis] = Field(
        default=[],
        description="List of word analysis results"
    )
    
    corrected_text: Optional[str] = Field(
        default=None,
        alias="correctedText",
        description="The fully corrected version of the input text"
    )
    
    original_text: Optional[str] = Field(
        default=None,
        alias="originalText",
        description="The original input text"
    )
    
    processing_time_ms: Optional[float] = Field(
        default=None,
        alias="processingTimeMs",
        description="Time taken to process the request in milliseconds"
    )
    
    model_used: Optional[str] = Field(
        default=None,
        alias="modelUsed",
        description="The model used for inference"
    )
    
    class Config:
        populate_by_name = True


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    model_status: str = Field(
        ...,
        alias="modelStatus",
        description="Status of the LLM connection"
    )
    ollama_connected: bool = Field(
        ...,
        alias="ollamaConnected",
        description="Whether Ollama is connected and responding"
    )
    
    class Config:
        populate_by_name = True


class BatchAnalyzeRequest(BaseModel):
    """Request model for batch analysis."""
    
    texts: List[str] = Field(
        ...,
        description="List of Sinhala texts to analyze",
        min_length=1,
        max_length=50
    )


class BatchAnalyzeResponse(BaseModel):
    """Response model for batch analysis."""
    
    success: bool = Field(...)
    results: List[AnalyzeResponse] = Field(default=[])
    total_processed: int = Field(default=0, alias="totalProcessed")
    
    class Config:
        populate_by_name = True
