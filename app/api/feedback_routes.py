"""
Akura AI - Feedback API Routes

API endpoints for managing teacher correction sessions and feedback.
Used for collecting training data and model fine-tuning.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.models.feedback_models import CorrectionSession, WordCorrection


# Pydantic schemas for request/response
class WordCorrectionCreate(BaseModel):
    """Schema for creating a word correction."""
    original_word: str
    suggested_word: Optional[str] = None
    pattern: Optional[str] = None
    confidence: Optional[float] = None
    position: Optional[int] = None


class WordCorrectionUpdate(BaseModel):
    """Schema for updating a word correction."""
    action: str  # 'accept', 'reject', 'edit'
    final_word: Optional[str] = None


class SessionCreate(BaseModel):
    """Schema for creating a correction session."""
    original_text: str
    model_used: Optional[str] = None
    corrections: List[WordCorrectionCreate] = []


class SessionUpdate(BaseModel):
    """Schema for updating a correction session."""
    corrected_text: Optional[str] = None
    status: Optional[str] = None


class SessionResponse(BaseModel):
    """Response schema for a session."""
    id: str
    original_text: str
    corrected_text: Optional[str] = None
    model_used: Optional[str] = None
    total_errors: int
    accepted_count: int
    rejected_count: int
    edited_count: int
    status: str
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    class Config:
        from_attributes = True


# Create router
router = APIRouter(prefix="/sessions", tags=["Feedback Sessions"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new correction session.
    
    Called when teacher starts analyzing an essay.
    """
    try:
        # Create session
        session = CorrectionSession(
            original_text=session_data.original_text,
            model_used=session_data.model_used,
            total_errors=len(session_data.corrections),
            status="in_progress"
        )
        db.add(session)
        db.flush()  # Get the session ID
        
        # Create word corrections
        for i, correction in enumerate(session_data.corrections):
            word_correction = WordCorrection(
                session_id=session.id,
                original_word=correction.original_word,
                suggested_word=correction.suggested_word,
                pattern=correction.pattern,
                confidence=correction.confidence,
                position=correction.position or i
            )
            db.add(word_correction)
        
        db.commit()
        db.refresh(session)
        
        logger.info(f"Created correction session: {session.id}")
        return session.to_dict()
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=List[dict])
async def list_sessions(
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all correction sessions.
    
    Useful for exporting training data.
    """
    try:
        query = db.query(CorrectionSession)
        
        if status_filter:
            query = query.filter(CorrectionSession.status == status_filter)
        
        sessions = query.order_by(CorrectionSession.created_at.desc()).offset(offset).limit(limit).all()
        
        return [s.to_dict() for s in sessions]
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{session_id}", response_model=dict)
async def get_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a single session with all corrections.
    """
    try:
        session = db.query(CorrectionSession).filter(
            CorrectionSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return session.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{session_id}", response_model=dict)
async def update_session(
    session_id: UUID,
    update_data: SessionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a correction session (e.g., save final corrected text).
    """
    try:
        session = db.query(CorrectionSession).filter(
            CorrectionSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if update_data.corrected_text is not None:
            session.corrected_text = update_data.corrected_text
        
        if update_data.status is not None:
            session.status = update_data.status
            if update_data.status == "completed":
                session.completed_at = datetime.utcnow()
        
        # Update counts from corrections
        corrections = session.corrections
        session.accepted_count = len([c for c in corrections if c.action == "accept"])
        session.rejected_count = len([c for c in corrections if c.action == "reject"])
        session.edited_count = len([c for c in corrections if c.action == "edit"])
        
        db.commit()
        db.refresh(session)
        
        logger.info(f"Updated session: {session.id}")
        return session.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/{session_id}/corrections/{correction_id}", response_model=dict)
async def update_correction(
    session_id: UUID,
    correction_id: UUID,
    update_data: WordCorrectionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a word correction (teacher's action).
    
    Allows accept, reject, edit, and RE-CORRECTION (changing previous decision).
    """
    try:
        correction = db.query(WordCorrection).filter(
            WordCorrection.id == correction_id,
            WordCorrection.session_id == session_id
        ).first()
        
        if not correction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Correction not found"
            )
        
        correction.action = update_data.action
        correction.action_timestamp = datetime.utcnow()
        
        if update_data.action == "accept":
            correction.final_word = correction.suggested_word
        elif update_data.action == "reject":
            correction.final_word = correction.original_word
        elif update_data.action == "edit":
            correction.final_word = update_data.final_word
        
        db.commit()
        db.refresh(correction)
        
        logger.info(f"Updated correction: {correction.id} - action: {update_data.action}")
        return correction.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating correction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a correction session.
    """
    try:
        session = db.query(CorrectionSession).filter(
            CorrectionSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        db.delete(session)
        db.commit()
        
        logger.info(f"Deleted session: {session_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Export endpoint
@router.get("/export/training-data", response_model=dict, tags=["Export"])
async def export_training_data(
    db: Session = Depends(get_db)
):
    """
    Export all completed sessions as training data for model fine-tuning.
    
    Returns data in a format suitable for fine-tuning.
    """
    try:
        sessions = db.query(CorrectionSession).filter(
            CorrectionSession.status == "completed"
        ).all()
        
        training_data = []
        
        for session in sessions:
            for correction in session.corrections:
                if correction.action in ["accept", "edit"]:
                    training_data.append({
                        "instruction": f"Correct the Sinhala dyslexia error. Pattern: {correction.pattern}",
                        "input": correction.original_word,
                        "output": correction.final_word,
                        "context": session.original_text,
                        "metadata": {
                            "sessionId": str(session.id),
                            "action": correction.action,
                            "confidence": correction.confidence,
                            "timestamp": correction.action_timestamp.isoformat() if correction.action_timestamp else None
                        }
                    })
        
        return {
            "exportedAt": datetime.utcnow().isoformat(),
            "totalSessions": len(sessions),
            "totalExamples": len(training_data),
            "data": training_data
        }
        
    except Exception as e:
        logger.error(f"Error exporting training data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
