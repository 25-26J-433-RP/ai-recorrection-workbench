"""
Akura AI - API Routes

This module defines all API endpoints for the Akura AI backend.
"""

from typing import List

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.core.config import get_settings
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    ErrorResponse,
    HealthResponse,
)
from app.services.analysis_service import analysis_service
from app.services.llm_service import llm_service


# Create router
router = APIRouter()
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API and LLM connection",
    tags=["System"]
)
async def health_check() -> HealthResponse:
    """
    Perform a health check on the API and Ollama connection.
    
    Returns:
        HealthResponse with status information
    """
    ollama_healthy, ollama_status = await llm_service.check_health()
    
    return HealthResponse(
        status="healthy" if ollama_healthy else "degraded",
        version="1.0.0",
        model_status=ollama_status,
        ollama_connected=ollama_healthy
    )


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze Sinhala Text",
    description="Analyze Sinhala text for dyslexic writing errors and provide corrections",
    tags=["Analysis"],
    responses={
        200: {
            "description": "Successful analysis",
            "model": AnalyzeResponse
        },
        400: {
            "description": "Invalid input",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze Sinhala text for dyslexic writing errors.
    
    This endpoint:
    1. Takes Sinhala text input
    2. Uses AI + rule-based hybrid approach for correction
    3. Detects specific dyslexia patterns
    4. Returns detailed word-by-word analysis
    
    Args:
        request: AnalyzeRequest with text to analyze
        
    Returns:
        AnalyzeResponse with analysis results
    """
    try:
        logger.info(f"Analyzing text: {request.text[:50]}...")
        
        response = await analysis_service.analyze(
            text=request.text,
            include_correct_words=request.include_correct_words
        )
        
        logger.info(
            f"Analysis complete. Found {len([w for w in response.data if w.type == 'error'])} errors"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post(
    "/analyze/batch",
    response_model=BatchAnalyzeResponse,
    summary="Batch Analyze Multiple Texts",
    description="Analyze multiple Sinhala texts in a single request",
    tags=["Analysis"]
)
async def batch_analyze(request: BatchAnalyzeRequest) -> BatchAnalyzeResponse:
    """
    Analyze multiple Sinhala texts in batch.
    
    Args:
        request: BatchAnalyzeRequest with list of texts
        
    Returns:
        BatchAnalyzeResponse with all analysis results
    """
    try:
        logger.info(f"Batch analyzing {len(request.texts)} texts")
        
        results = await analysis_service.analyze_batch(request.texts)
        
        return BatchAnalyzeResponse(
            success=True,
            results=results,
            total_processed=len(results)
        )
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )


@router.post(
    "/check",
    summary="Quick Error Check",
    description="Quickly check if text contains any errors",
    tags=["Analysis"]
)
async def quick_check(request: AnalyzeRequest) -> dict:
    """
    Perform a quick check to see if text contains errors.
    
    This is faster than full analysis and useful for
    real-time validation.
    
    Args:
        request: AnalyzeRequest with text to check
        
    Returns:
        Dict with has_errors boolean
    """
    try:
        has_errors = await analysis_service.quick_check(request.text)
        return {
            "success": True,
            "has_errors": has_errors,
            "text": request.text
        }
    except Exception as e:
        logger.error(f"Quick check failed: {e}")
        return {
            "success": False,
            "has_errors": None,
            "error": str(e)
        }


@router.get(
    "/patterns",
    summary="List Dyslexia Patterns",
    description="Get list of all detectable dyslexia patterns",
    tags=["Reference"]
)
async def list_patterns() -> dict:
    """
    Get information about all detectable dyslexia patterns.
    
    Returns:
        Dict with pattern information
    """
    from app.utils.sinhala_mappings import PATTERN_EXPLANATIONS
    
    patterns = [
        {
            "name": name,
            "description": description
        }
        for name, description in PATTERN_EXPLANATIONS.items()
    ]
    
    return {
        "success": True,
        "patterns": patterns,
        "total": len(patterns)
    }


@router.get(
    "/corrections",
    summary="List Known Corrections",
    description="Get list of all known word corrections",
    tags=["Reference"]
)
async def list_corrections() -> dict:
    """
    Get all known word corrections in the rule-based system.
    
    Returns:
        Dict with correction mappings
    """
    from app.services.rule_corrector import rule_corrector
    
    corrections = rule_corrector.get_known_corrections()
    
    return {
        "success": True,
        "corrections": corrections,
        "total": len(corrections)
    }


@router.get(
    "/config",
    summary="Get Configuration",
    description="Get current API configuration (non-sensitive)",
    tags=["System"]
)
async def get_config() -> dict:
    """
    Get current API configuration.
    
    Returns non-sensitive configuration values.
    
    Returns:
        Dict with configuration
    """
    return {
        "success": True,
        "config": {
            "model": settings.ollama_model,
            "temperature": settings.model_temperature,
            "max_tokens": settings.model_max_tokens,
            "confidence_threshold": settings.ai_confidence_threshold,
            "environment": settings.environment
        }
    }


@router.post(
    "/feedback",
    summary="Submit Teacher Feedback",
    description="Submit teacher correction feedback for model fine-tuning",
    tags=["Feedback"]
)
async def submit_feedback(feedback_data: dict) -> dict:
    """
    Receive teacher correction feedback for future model fine-tuning.
    
    This endpoint collects:
    - Accept/Reject/Edit decisions
    - Original words and corrections
    - Dyslexia patterns detected
    - Teacher's manual corrections (most valuable)
    
    Args:
        feedback_data: Dict containing feedback items and timestamp
        
    Returns:
        Dict with success status
    """
    import json
    import os
    from datetime import datetime
    
    try:
        # Create feedback directory if it doesn't exist
        feedback_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "feedback")
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"feedback_{timestamp}.json"
        filepath = os.path.join(feedback_dir, filename)
        
        # Save feedback data
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(feedback_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved feedback to {filepath}")
        
        # Also append to cumulative JSONL file for easy training
        jsonl_path = os.path.join(feedback_dir, "training_data.jsonl")
        with open(jsonl_path, "a", encoding="utf-8") as f:
            for item in feedback_data.get("feedback", []):
                if item.get("type") == "correction_action":
                    data = item.get("data", {})
                    if data.get("action") in ["accept", "edit"]:
                        training_example = {
                            "instruction": f"Correct the Sinhala dyslexia error. Pattern: {data.get('pattern', 'Unknown')}",
                            "input": data.get("originalWord", ""),
                            "output": data.get("finalWord", ""),
                            "timestamp": data.get("timestamp", ""),
                            "action": data.get("action", ""),
                        }
                        f.write(json.dumps(training_example, ensure_ascii=False) + "\n")
        
        return {
            "success": True,
            "message": "Feedback saved successfully",
            "file": filename,
            "items_received": len(feedback_data.get("feedback", []))
        }
        
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get(
    "/feedback/stats",
    summary="Get Feedback Statistics",
    description="Get statistics about collected feedback data",
    tags=["Feedback"]
)
async def get_feedback_stats() -> dict:
    """
    Get statistics about collected teacher feedback.
    
    Returns:
        Dict with feedback statistics
    """
    import os
    import json
    
    try:
        feedback_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "feedback")
        
        if not os.path.exists(feedback_dir):
            return {
                "success": True,
                "total_files": 0,
                "total_training_examples": 0,
                "message": "No feedback data collected yet"
            }
        
        # Count feedback files
        feedback_files = [f for f in os.listdir(feedback_dir) if f.startswith("feedback_") and f.endswith(".json")]
        
        # Count training examples
        jsonl_path = os.path.join(feedback_dir, "training_data.jsonl")
        training_count = 0
        if os.path.exists(jsonl_path):
            with open(jsonl_path, "r", encoding="utf-8") as f:
                training_count = sum(1 for _ in f)
        
        return {
            "success": True,
            "total_files": len(feedback_files),
            "total_training_examples": training_count,
            "feedback_directory": feedback_dir
        }
        
    except Exception as e:
        logger.error(f"Failed to get feedback stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }

