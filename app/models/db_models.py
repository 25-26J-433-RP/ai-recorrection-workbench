"""
Akura AI - Database Models

SQLAlchemy models for correction sessions and actions.
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class CorrectionSession(Base):
    """
    Represents a single essay correction session.
    """
    __tablename__ = "correction_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_text = Column(Text, nullable=False)
    final_text = Column(Text, nullable=True)
    model_used = Column(String(255), nullable=True)
    is_demo_mode = Column(String(10), default="false")
    
    # Student tracking - links to frontend studentId
    student_id = Column(String(255), nullable=True, index=True)
    student_name = Column(String(255), nullable=True)
    student_grade = Column(String(50), nullable=True)
    
    # Statistics
    total_errors = Column(Integer, default=0)
    accepted_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)
    edited_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    actions = relationship("CorrectionAction", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "originalText": self.original_text,
            "finalText": self.final_text,
            "modelUsed": self.model_used,
            "isDemoMode": self.is_demo_mode == "true",
            "studentId": self.student_id,
            "studentName": self.student_name,
            "studentGrade": self.student_grade,
            "totalErrors": self.total_errors,
            "acceptedCount": self.accepted_count,
            "rejectedCount": self.rejected_count,
            "editedCount": self.edited_count,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "actions": [a.to_dict() for a in self.actions] if self.actions else []
        }


class CorrectionAction(Base):
    """
    Represents a single word correction action within a session.
    """
    __tablename__ = "correction_actions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("correction_sessions.id", ondelete="CASCADE"), nullable=False)
    
    # Word data
    original_word = Column(String(255), nullable=False)
    suggestion = Column(String(255), nullable=True)
    final_word = Column(String(255), nullable=True)
    
    # Action and pattern
    action = Column(String(20), nullable=True)  # accept, reject, edit
    pattern = Column(String(100), nullable=True)
    
    # Confidence score
    confidence = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("CorrectionSession", back_populates="actions")
    
    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "sessionId": str(self.session_id),
            "originalWord": self.original_word,
            "suggestion": self.suggestion,
            "finalWord": self.final_word,
            "action": self.action,
            "pattern": self.pattern,
            "confidence": self.confidence,
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }
