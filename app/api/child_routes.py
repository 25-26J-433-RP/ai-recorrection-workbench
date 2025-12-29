"""
Akura AI - Child Essay API Routes

API endpoints for managing corrected essays per child.
Allows external systems to retrieve a child's corrected work.
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.services.analysis_service import analysis_service


# Pydantic schemas
class EssaySubmit(BaseModel):
    """Schema for submitting an essay for correction."""
    original_text: str
    title: Optional[str] = None


class CorrectionDetail(BaseModel):
    """Schema for a single word correction."""
    word: str
    suggestion: str
    pattern: Optional[str] = None
    confidence: Optional[float] = None


class EssayResponse(BaseModel):
    """Response schema for an essay."""
    essay_id: str
    child_id: str
    title: Optional[str] = None
    original_text: str
    corrected_text: str
    error_count: int
    corrections: List[CorrectionDetail] = []
    model_used: Optional[str] = None
    processing_time_ms: Optional[float] = None
    created_at: str


class EssayListItem(BaseModel):
    """Brief schema for essay list."""
    essay_id: str
    title: Optional[str] = None
    original_text: str
    corrected_text: str
    error_count: int
    created_at: str


# In-memory storage (since database may not be configured)
# In production, this would use the database
_essays_store: dict = {}


# Create router
router = APIRouter(prefix="/children", tags=["Child Essays"])


@router.post("/{child_id}/essays", response_model=EssayResponse, status_code=status.HTTP_201_CREATED)
async def submit_essay(
    child_id: str,
    essay_data: EssaySubmit
):
    """
    Submit an essay for a child and get the corrected version.
    
    The essay will be analyzed by the AI model and corrections will be applied.
    """
    try:
        # Analyze the text using the analysis service
        result = await analysis_service.analyze(essay_data.original_text)
        
        # Extract corrections from the analysis result
        corrections = []
        for item in result.data:
            if item.type == "error":
                corrections.append(CorrectionDetail(
                    word=item.word,
                    suggestion=item.suggestion or item.word,
                    pattern=item.dyslexia_pattern,
                    confidence=item.confidence
                ))
        
        # Generate essay ID and timestamp
        essay_id = str(uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        # Create essay response
        essay = EssayResponse(
            essay_id=essay_id,
            child_id=child_id,
            title=essay_data.title,
            original_text=result.original_text,
            corrected_text=result.corrected_text,
            error_count=len(corrections),
            corrections=corrections,
            model_used=result.model_used,
            processing_time_ms=result.processing_time_ms,
            created_at=created_at
        )
        
        # Store in memory (keyed by child_id)
        if child_id not in _essays_store:
            _essays_store[child_id] = []
        _essays_store[child_id].append(essay.model_dump())
        
        logger.info(f"Created essay {essay_id} for child {child_id}")
        return essay
        
    except Exception as e:
        logger.error(f"Error processing essay for child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{child_id}/essays", response_model=List[EssayListItem])
async def get_child_essays(
    child_id: str,
    limit: int = 50,
    offset: int = 0
):
    """
    Get all corrected essays for a specific child.
    
    Returns a list of essays ordered by creation date (newest first).
    """
    try:
        essays = _essays_store.get(child_id, [])
        
        # Sort by created_at descending
        sorted_essays = sorted(essays, key=lambda x: x['created_at'], reverse=True)
        
        # Apply pagination
        paginated = sorted_essays[offset:offset + limit]
        
        # Convert to list items
        return [
            EssayListItem(
                essay_id=e['essay_id'],
                title=e.get('title'),
                original_text=e['original_text'],
                corrected_text=e['corrected_text'],
                error_count=e['error_count'],
                created_at=e['created_at']
            )
            for e in paginated
        ]
        
    except Exception as e:
        logger.error(f"Error getting essays for child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{child_id}/essays/latest", response_model=EssayResponse)
async def get_latest_essay(child_id: str):
    """
    Get the most recent corrected essay for a child.
    """
    try:
        essays = _essays_store.get(child_id, [])
        
        if not essays:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No essays found for child {child_id}"
            )
        
        # Get the most recent essay
        sorted_essays = sorted(essays, key=lambda x: x['created_at'], reverse=True)
        latest = sorted_essays[0]
        
        return EssayResponse(**latest)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest essay for child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{child_id}/essays/{essay_id}", response_model=EssayResponse)
async def get_essay(child_id: str, essay_id: str):
    """
    Get a specific essay by ID for a child.
    """
    try:
        essays = _essays_store.get(child_id, [])
        
        for essay in essays:
            if essay['essay_id'] == essay_id:
                return EssayResponse(**essay)
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Essay {essay_id} not found for child {child_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting essay {essay_id} for child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{child_id}/essays/{essay_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_essay(child_id: str, essay_id: str):
    """
    Delete a specific essay for a child.
    """
    try:
        essays = _essays_store.get(child_id, [])
        
        for i, essay in enumerate(essays):
            if essay['essay_id'] == essay_id:
                del essays[i]
                logger.info(f"Deleted essay {essay_id} for child {child_id}")
                return
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Essay {essay_id} not found for child {child_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting essay {essay_id} for child {child_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=dict)
async def list_all_children():
    """
    List all children who have submitted essays.
    """
    try:
        children = []
        for child_id, essays in _essays_store.items():
            children.append({
                "child_id": child_id,
                "essay_count": len(essays),
                "latest_essay_at": max(e['created_at'] for e in essays) if essays else None
            })
        
        return {
            "total_children": len(children),
            "children": sorted(children, key=lambda x: x.get('latest_essay_at') or '', reverse=True)
        }
        
    except Exception as e:
        logger.error(f"Error listing children: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
