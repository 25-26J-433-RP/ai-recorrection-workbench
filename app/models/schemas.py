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
        description="Source of the correction (ai or rule-based)"
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
        protected_namespaces = ()


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
        description="Status of the Akura LLM connection"
    )
    ollama_connected: bool = Field(
        ...,
        alias="ollamaConnected",
        description="Whether the Akura model is connected and responding"
    )
    
    class Config:
        populate_by_name = True
        protected_namespaces = ()


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
        protected_namespaces = ()


# =============================================================================
# STUDENT TRACKING SCHEMAS
# =============================================================================

class StudentInfo(BaseModel):
    """Summary info for a student with correction history."""
    
    student_id: str = Field(..., alias="studentId", description="Student identifier")
    student_name: Optional[str] = Field(default=None, alias="studentName")
    student_grade: Optional[str] = Field(default=None, alias="studentGrade")
    total_sessions: int = Field(default=0, alias="totalSessions")
    total_errors: int = Field(default=0, alias="totalErrors")
    last_session_at: Optional[str] = Field(default=None, alias="lastSessionAt")
    
    class Config:
        populate_by_name = True


class StudentProgress(BaseModel):
    """Progress metrics for a student over time."""
    
    student_id: str = Field(..., alias="studentId")
    sessions: List[dict] = Field(default=[], description="Session history with dates and error counts")
    pattern_frequency: dict = Field(default={}, alias="patternFrequency", description="Count of each dyslexia pattern")
    total_sessions: int = Field(default=0, alias="totalSessions")
    total_errors: int = Field(default=0, alias="totalErrors")
    average_errors_per_session: float = Field(default=0.0, alias="averageErrorsPerSession")
    
    class Config:
        populate_by_name = True


class SessionCreateWithStudent(BaseModel):
    """Request model for creating a session with student info."""
    
    original_text: str = Field(..., alias="originalText", min_length=1)
    model_used: Optional[str] = Field(default=None, alias="modelUsed")
    student_id: Optional[str] = Field(default=None, alias="studentId")
    student_name: Optional[str] = Field(default=None, alias="studentName")
    student_grade: Optional[str] = Field(default=None, alias="studentGrade")
    corrections: List[dict] = Field(default=[])
    
    class Config:
        populate_by_name = True


class DyslexiaProfile(BaseModel):
    """
    Unique dyslexia error fingerprint for a student.
    
    Generated from historical correction patterns to identify
    dominant error types and recommend targeted interventions.
    """
    
    student_id: str = Field(..., alias="studentId")
    student_name: Optional[str] = Field(default=None, alias="studentName")
    student_grade: Optional[str] = Field(default=None, alias="studentGrade")
    
    # Pattern analysis
    dominant_pattern: Optional[str] = Field(
        default=None, 
        alias="dominantPattern",
        description="Most frequent error type"
    )
    pattern_distribution: dict = Field(
        default={}, 
        alias="patternDistribution",
        description="Percentage breakdown: {pattern: percentage}"
    )
    weakness_areas: List[str] = Field(
        default=[], 
        alias="weaknessAreas",
        description="Top 3 problem patterns"
    )
    
    # Metrics
    total_sessions: int = Field(default=0, alias="totalSessions")
    total_errors: int = Field(default=0, alias="totalErrors")
    average_errors_per_session: float = Field(default=0.0, alias="averageErrorsPerSession")
    
    # Trend analysis
    improvement_trend: str = Field(
        default="unknown", 
        alias="improvementTrend",
        description="improving, stable, or declining"
    )
    
    # Remediation
    recommended_exercises: List[str] = Field(
        default=[], 
        alias="recommendedExercises",
        description="Targeted exercises based on weakness areas"
    )
    
    # Severity scoring (0-100)
    severity_score: float = Field(
        default=0.0, 
        alias="severityScore",
        description="Overall dyslexia severity (0-100)"
    )
    severity_level: str = Field(
        default="unknown",
        alias="severityLevel",
        description="mild (0-30), moderate (31-60), severe (61-100)"
    )
    severity_breakdown: dict = Field(
        default={},
        alias="severityBreakdown",
        description="Component scores: errorRate, patternDiversity, consistency"
    )
    
    class Config:
        populate_by_name = True
