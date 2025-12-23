"""
Akura AI - Feedback Models

Database models for storing teacher correction feedback for model fine-tuning.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class SessionStatus(str, enum.Enum):
    """Status of a correction session."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CorrectionAction(str, enum.Enum):
    """Teacher's action on a word correction."""
    ACCEPT = "accept"
    REJECT = "reject"
    EDIT = "edit"


class CorrectionSession(Base):
    """
    Represents a single essay correction session by a teacher.
    
    Stores the original text, final corrected text, and statistics.
    """
    __tablename__ = "correction_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=True)
    model_used = Column(String(255), nullable=True)
    
    # Statistics
    total_errors = Column(Integer, default=0)
    accepted_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)
    edited_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), default=SessionStatus.IN_PROGRESS.value)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    corrections = relationship("WordCorrection", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "originalText": self.original_text,
            "correctedText": self.corrected_text,
            "modelUsed": self.model_used,
            "totalErrors": self.total_errors,
            "acceptedCount": self.accepted_count,
            "rejectedCount": self.rejected_count,
            "editedCount": self.edited_count,
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "corrections": [c.to_dict() for c in self.corrections] if self.corrections else []
        }


class WordCorrection(Base):
    """
    Represents a single word correction decision by a teacher.
    
    Tracks the original word, AI suggestion, teacher's final decision,
    and the action taken (accept/reject/edit).
    """
    __tablename__ = "word_corrections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("correction_sessions.id", ondelete="CASCADE"), nullable=False)
    
    # Word data
    original_word = Column(String(255), nullable=False)
    suggested_word = Column(String(255), nullable=True)
    final_word = Column(String(255), nullable=True)
    
    # Error pattern (e.g., "Spelling", "Phonetic", "Visual")
    pattern = Column(String(100), nullable=True)
    
    # Teacher's action
    action = Column(String(20), nullable=True)  # 'accept', 'reject', 'edit', None
    
    # AI confidence score
    confidence = Column(Float, nullable=True)
    
    # Position in text (for ordering)
    position = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    action_timestamp = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("CorrectionSession", back_populates="corrections")
    
    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "sessionId": str(self.session_id),
            "originalWord": self.original_word,
            "suggestedWord": self.suggested_word,
            "finalWord": self.final_word,
            "pattern": self.pattern,
            "action": self.action,
            "confidence": self.confidence,
            "position": self.position,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "actionTimestamp": self.action_timestamp.isoformat() if self.action_timestamp else None
        }
