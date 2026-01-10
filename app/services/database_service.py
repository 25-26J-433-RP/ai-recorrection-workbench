"""
Akura AI - Database Service

Service layer for database operations on correction sessions and actions.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.db_models import CorrectionSession, CorrectionAction


class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self._is_configured = bool(self.settings.database_url)
    
    @property
    def is_configured(self) -> bool:
        """Check if database is configured."""
        return self._is_configured
    
    def save_session(
        self,
        db: Session,
        original_text: str,
        final_text: Optional[str] = None,
        model_used: Optional[str] = None,
        is_demo_mode: bool = False,
        actions: Optional[List[dict]] = None,
        student_id: Optional[str] = None,
        student_name: Optional[str] = None,
        student_grade: Optional[str] = None
    ) -> CorrectionSession:
        """
        Save a correction session to database.
        
        Args:
            db: Database session
            original_text: Original input text
            final_text: Final corrected text
            model_used: Name of model used
            is_demo_mode: Whether demo mode was used
            actions: List of correction actions
            student_id: Student identifier (from frontend)
            student_name: Student name
            student_grade: Student grade level
            
        Returns:
            Created CorrectionSession
        """
        session = CorrectionSession(
            original_text=original_text,
            final_text=final_text,
            model_used=model_used,
            is_demo_mode="true" if is_demo_mode else "false",
            student_id=student_id,
            student_name=student_name,
            student_grade=student_grade,
            total_errors=len(actions) if actions else 0,  # Auto-calculate from actions
            completed_at=datetime.utcnow() if final_text else None
        )
        db.add(session)
        db.flush()  # Get the session ID
        
        # Add actions if provided
        if actions:
            for action_data in actions:
                action = CorrectionAction(
                    session_id=session.id,
                    original_word=action_data.get("original_word", ""),
                    suggestion=action_data.get("suggestion") or action_data.get("suggested_word"),
                    final_word=action_data.get("final_word"),
                    action=action_data.get("action"),
                    pattern=action_data.get("pattern"),
                    confidence=action_data.get("confidence")
                )
                db.add(action)
        
        db.commit()
        db.refresh(session)
        logger.info(f"Saved session {session.id} for student {student_id} with {len(actions) if actions else 0} actions")
        return session
    
    def add_action(
        self,
        db: Session,
        session_id: UUID,
        original_word: str,
        suggestion: Optional[str] = None,
        final_word: Optional[str] = None,
        action: Optional[str] = None,
        pattern: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> CorrectionAction:
        """Add a correction action to an existing session."""
        action_record = CorrectionAction(
            session_id=session_id,
            original_word=original_word,
            suggestion=suggestion,
            final_word=final_word,
            action=action,
            pattern=pattern,
            confidence=confidence
        )
        db.add(action_record)
        db.commit()
        db.refresh(action_record)
        return action_record
    
    def get_session(self, db: Session, session_id: UUID) -> Optional[CorrectionSession]:
        """Get a session by ID."""
        return db.query(CorrectionSession).filter(CorrectionSession.id == session_id).first()
    
    def get_all_sessions(
        self,
        db: Session,
        limit: int = 100,
        offset: int = 0
    ) -> List[CorrectionSession]:
        """Get all sessions with pagination."""
        return db.query(CorrectionSession)\
            .order_by(CorrectionSession.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    def get_session_count(self, db: Session) -> int:
        """Get total number of sessions."""
        return db.query(CorrectionSession).count()
    
    def export_for_training(self, db: Session) -> List[dict]:
        """
        Export all sessions and actions in training format.
        
        Returns:
            List of training examples
        """
        sessions = db.query(CorrectionSession).all()
        training_data = []
        
        for session in sessions:
            for action in session.actions:
                if action.action and action.action != "reject":
                    training_data.append({
                        "instruction": f"Correct the Sinhala dyslexia error. Pattern: {action.pattern}",
                        "input": action.original_word,
                        "output": action.final_word or action.suggestion,
                        "context": session.original_text,
                        "metadata": {
                            "session_id": str(session.id),
                            "action": action.action,
                            "confidence": action.confidence,
                            "model_used": session.model_used
                        }
                    })
        
        return training_data
    
    def delete_session(self, db: Session, session_id: UUID) -> bool:
        """Delete a session and its actions."""
        session = self.get_session(db, session_id)
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    
    # =========================================================================
    # STUDENT TRACKING METHODS
    # =========================================================================
    
    def get_all_students(self, db: Session) -> List[dict]:
        """
        Get summary info for all students with correction sessions.
        
        Returns:
            List of student info dictionaries
        """
        from sqlalchemy import func
        
        results = db.query(
            CorrectionSession.student_id,
            CorrectionSession.student_name,
            CorrectionSession.student_grade,
            func.count(CorrectionSession.id).label('total_sessions'),
            func.sum(CorrectionSession.total_errors).label('total_errors'),
            func.max(CorrectionSession.created_at).label('last_session_at')
        ).filter(
            CorrectionSession.student_id.isnot(None)
        ).group_by(
            CorrectionSession.student_id,
            CorrectionSession.student_name,
            CorrectionSession.student_grade
        ).all()
        
        return [
            {
                "studentId": r.student_id,
                "studentName": r.student_name,
                "studentGrade": r.student_grade,
                "totalSessions": r.total_sessions,
                "totalErrors": r.total_errors or 0,
                "lastSessionAt": r.last_session_at.isoformat() if r.last_session_at else None
            }
            for r in results
        ]
    
    def get_student_sessions(
        self,
        db: Session,
        student_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[CorrectionSession]:
        """Get all sessions for a specific student."""
        return db.query(CorrectionSession)\
            .filter(CorrectionSession.student_id == student_id)\
            .order_by(CorrectionSession.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    def get_student_progress(self, db: Session, student_id: str) -> dict:
        """
        Get progress metrics for a specific student.
        
        Returns:
            Dictionary with progress data
        """
        from sqlalchemy import func
        
        sessions = self.get_student_sessions(db, student_id, limit=100)
        
        if not sessions:
            return {
                "studentId": student_id,
                "sessions": [],
                "patternFrequency": {},
                "totalSessions": 0,
                "totalErrors": 0,
                "averageErrorsPerSession": 0.0
            }
        
        # Build session history
        session_history = [
            {
                "date": s.created_at.isoformat() if s.created_at else None,
                "errorCount": s.total_errors or 0,
                "sessionId": str(s.id)
            }
            for s in sessions
        ]
        
        # Count patterns across all sessions
        pattern_counts = {}
        for session in sessions:
            for action in session.actions:
                if action.pattern:
                    pattern_counts[action.pattern] = pattern_counts.get(action.pattern, 0) + 1
        
        total_errors = sum(s.total_errors or 0 for s in sessions)
        
        return {
            "studentId": student_id,
            "sessions": session_history,
            "patternFrequency": pattern_counts,
            "totalSessions": len(sessions),
            "totalErrors": total_errors,
            "averageErrorsPerSession": total_errors / len(sessions) if sessions else 0.0
        }


# Singleton instance
database_service = DatabaseService()
