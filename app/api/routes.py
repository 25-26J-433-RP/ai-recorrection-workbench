"""
Akura AI - API Routes

This module defines all API endpoints for the Akura AI backend.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from loguru import logger
from sqlalchemy.orm import Session

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
from app.services.ocr_service import ocr_service
from app.services.external_services import external_services


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


@router.post(
    "/ocr",
    summary="Extract Text from Image",
    description="Extract Sinhala handwritten text from an uploaded image using OCR",
    tags=["OCR"]
)
async def extract_text_from_image(
    image: UploadFile = File(..., description="Image file containing Sinhala handwritten text")
) -> dict:
    """
    Extract Sinhala text from an uploaded image.
    
    This endpoint:
    1. Accepts an image file upload
    2. Uses Gemini Vision API to extract handwritten Sinhala text
    3. Returns the raw extracted text (without corrections)
    
    The extracted text can then be sent to /analyze for dyslexia correction.
    
    Args:
        image: Uploaded image file (JPEG, PNG, WebP, or GIF)
        
    Returns:
        Dict with extracted text and metadata
    """
    # Validate file type
    valid_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if image.content_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {image.content_type}. Supported types: {', '.join(valid_types)}"
        )
    
    # Validate file size (max 20MB)
    max_size = 20 * 1024 * 1024
    contents = await image.read()
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 20MB."
        )
    
    logger.info(f"OCR request: {image.filename}, size={len(contents)} bytes, type={image.content_type}")
    
    # Extract text using OCR service
    success, result, confidence = await ocr_service.extract_text_from_image(
        image_bytes=contents,
        mime_type=image.content_type,
        filename=image.filename or "image.jpg"
    )
    
    if not success:
        logger.error(f"OCR extraction failed: {result}")
        return {
            "success": False,
            "error": result,
            "text": "",
            "confidence": 0.0
        }
    
    logger.info(f"OCR extraction successful: {len(result)} characters extracted")
    
    return {
        "success": True,
        "text": result,
        "confidence": confidence,
        "source": "gemini-vision",
        "filename": image.filename
    }


@router.get(
    "/ocr/status",
    summary="OCR Service Status",
    description="Check if OCR service is configured and available",
    tags=["OCR"]
)
async def ocr_status() -> dict:
    """
    Check OCR service configuration status.
    
    Returns:
        Dict with OCR service status
    """
    is_healthy, status_msg = await ocr_service.check_health()
    
    return {
        "success": True,
        "configured": is_healthy,
        "status": status_msg,
        "model": settings.gemini_model,
        "use_external": settings.use_external_ocr
    }


@router.get(
    "/external-services",
    summary="External Services Status",
    description="Check status of all external microservices (OCR, Pattern Detection)",
    tags=["System"]
)
async def external_services_status() -> dict:
    """
    Check health of all configured external services.
    
    Returns:
        Dict with service health information
    """
    status = await external_services.check_all_services()
    return {
        "success": True,
        **status
    }


# =============================================================================
# DATABASE / SESSION ENDPOINTS
# =============================================================================

# Import database dependencies
try:
    from app.core.database import get_db, init_db
    from app.services.database_service import database_service
    DB_AVAILABLE = database_service.is_configured
except ImportError:
    DB_AVAILABLE = False
    get_db = None


@router.post(
    "/sessions",
    summary="Save Correction Session",
    description="Save a complete correction session to the database",
    tags=["Sessions"]
)
async def save_session(session_data: dict, db: Session = Depends(get_db)) -> dict:
    """
    Save a correction session to the database.
    
    Args:
        session_data: Dict containing original_text, final_text, model_used, actions
        
    Returns:
        Dict with saved session details
    """
    if not DB_AVAILABLE:
        return {
            "success": False,
            "error": "Database not configured. Set DATABASE_URL in .env"
        }
    
    try:
        session = database_service.save_session(
            db=db,
            original_text=session_data.get("original_text", ""),
            final_text=session_data.get("final_text"),
            model_used=session_data.get("model_used"),
            is_demo_mode=session_data.get("is_demo_mode", False),
            actions=session_data.get("actions", [])
        )
        
        logger.info(f"Saved session {session.id} to database")
        
        return {
            "success": True,
            "session_id": str(session.id),
            "message": "Session saved to database"
        }
        
    except Exception as e:
        logger.error(f"Failed to save session: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get(
    "/sessions",
    summary="List Saved Sessions",
    description="Get all saved correction sessions",
    tags=["Sessions"]
)
async def list_sessions(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> dict:
    """
    List all saved correction sessions.
    
    Args:
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip
        
    Returns:
        Dict with list of sessions
    """
    if not DB_AVAILABLE:
        return {
            "success": False,
            "error": "Database not configured. Set DATABASE_URL in .env"
        }
    
    try:
        sessions = database_service.get_all_sessions(db, limit=limit, offset=offset)
        total = database_service.get_session_count(db)
        
        return {
            "success": True,
            "sessions": [s.to_dict() for s in sessions],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get(
    "/sessions/{session_id}",
    summary="Get Session Details",
    description="Get details of a specific correction session",
    tags=["Sessions"]
)
async def get_session(session_id: UUID, db: Session = Depends(get_db)) -> dict:
    """
    Get a specific session by ID.
    
    Args:
        session_id: UUID of the session
        
    Returns:
        Dict with session details
    """
    if not DB_AVAILABLE:
        return {
            "success": False,
            "error": "Database not configured. Set DATABASE_URL in .env"
        }
    
    try:
        session = database_service.get_session(db, session_id)
        
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        return {
            "success": True,
            "session": session.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get(
    "/sessions/export/training",
    summary="Export Training Data",
    description="Export all sessions as training data for fine-tuning",
    tags=["Sessions"]
)
async def export_training_data(db: Session = Depends(get_db)) -> dict:
    """
    Export all sessions in training format.
    
    Returns:
        Dict with training examples
    """
    if not DB_AVAILABLE:
        return {
            "success": False,
            "error": "Database not configured. Set DATABASE_URL in .env"
        }
    
    try:
        training_data = database_service.export_for_training(db)
        
        return {
            "success": True,
            "total_examples": len(training_data),
            "data": training_data
        }
        
    except Exception as e:
        logger.error(f"Failed to export training data: {e}")
        return {
            "success": False,
            "error": str(e)
        }
