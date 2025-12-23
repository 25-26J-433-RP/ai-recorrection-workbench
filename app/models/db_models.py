"""
Akura AI - Database Models

SQLAlchemy models for storing correction sessions and actions.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class CorrectionSession(Base):
    """Model for a single correction session (one essay analysis)."""
    
    __tablename__ = "correction_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_text = Column(Text, nullable=False)
    final_text = Column(Text)
    model_used = Column(String(100))
    is_demo_mode = Column(String(10), default="false")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationship to actions
    actions = relationship("CorrectionAction", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "original_text": self.original_text,
            "final_text": self.final_text,
            "model_used": self.model_used,
            "is_demo_mode": self.is_demo_mode,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "actions": [a.to_dict() for a in self.actions] if self.actions else []
        }


class CorrectionAction(Base):
    """Model for a single correction action (accept/reject/edit)."""
    
    __tablename__ = "correction_actions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("correction_sessions.id"), nullable=False)
    original_word = Column(String(200), nullable=False)
    suggestion = Column(String(200))
    final_word = Column(String(200))
    action = Column(String(20))  # 'accept', 'reject', 'edit'
    pattern = Column(String(100))
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to session
    session = relationship("CorrectionSession", back_populates="actions")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "original_word": self.original_word,
            "suggestion": self.suggestion,
            "final_word": self.final_word,
            "action": self.action,
            "pattern": self.pattern,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
