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
    
    def get_student_profile(self, db: Session, student_id: str) -> dict:
        """
        Generate a dyslexia profile (error fingerprint) for a student.
        
        This analyzes all historical patterns to identify:
        - Dominant error pattern
        - Pattern distribution percentages
        - Weakness areas (top 3 patterns)
        - Improvement trend over time
        - Recommended exercises
        
        Returns:
            Dictionary with complete dyslexia profile
        """
        # Get all sessions for the student
        sessions = self.get_student_sessions(db, student_id, limit=100)
        
        if not sessions:
            return {
                "studentId": student_id,
                "studentName": None,
                "studentGrade": None,
                "dominantPattern": None,
                "patternDistribution": {},
                "weaknessAreas": [],
                "totalSessions": 0,
                "totalErrors": 0,
                "averageErrorsPerSession": 0.0,
                "improvementTrend": "unknown",
                "recommendedExercises": []
            }
        
        # Get student info from first session
        student_name = sessions[0].student_name
        student_grade = sessions[0].student_grade
        
        # Count all patterns
        pattern_counts = {}
        for session in sessions:
            for action in session.actions:
                if action.pattern:
                    pattern_counts[action.pattern] = pattern_counts.get(action.pattern, 0) + 1
        
        total_patterns = sum(pattern_counts.values())
        total_errors = sum(s.total_errors or 0 for s in sessions)
        total_sessions = len(sessions)
        
        # Calculate pattern distribution (percentages)
        pattern_distribution = {}
        if total_patterns > 0:
            for pattern, count in pattern_counts.items():
                pattern_distribution[pattern] = round((count / total_patterns) * 100, 1)
        
        # Find dominant pattern and weakness areas
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        dominant_pattern = sorted_patterns[0][0] if sorted_patterns else None
        weakness_areas = [p[0] for p in sorted_patterns[:3]]
        
        # Calculate improvement trend (compare recent vs older sessions)
        improvement_trend = self._calculate_improvement_trend(sessions)
        
        # Get recommended exercises based on weakness areas
        recommended_exercises = self._get_recommended_exercises(weakness_areas)
        
        # Calculate severity score
        severity = self._calculate_severity_score(sessions, pattern_distribution, improvement_trend)
        
        return {
            "studentId": student_id,
            "studentName": student_name,
            "studentGrade": student_grade,
            "dominantPattern": dominant_pattern,
            "patternDistribution": pattern_distribution,
            "weaknessAreas": weakness_areas,
            "totalSessions": total_sessions,
            "totalErrors": total_errors,
            "averageErrorsPerSession": round(total_errors / total_sessions, 2) if total_sessions else 0.0,
            "improvementTrend": improvement_trend,
            "recommendedExercises": recommended_exercises,
            # Severity scoring
            "severityScore": severity["severityScore"],
            "severityLevel": severity["severityLevel"],
            "severityBreakdown": severity["severityBreakdown"]
        }
    
    def _calculate_improvement_trend(self, sessions: list) -> str:
        """
        Calculate if student is improving, stable, or declining.
        
        Compares average errors in recent sessions vs older sessions.
        """
        if len(sessions) < 4:
            return "unknown"
        
        # Sort by date (newest first - they're already sorted)
        recent = sessions[:len(sessions)//2]
        older = sessions[len(sessions)//2:]
        
        recent_avg = sum(s.total_errors or 0 for s in recent) / len(recent) if recent else 0
        older_avg = sum(s.total_errors or 0 for s in older) / len(older) if older else 0
        
        if older_avg == 0:
            return "stable"
        
        change = (recent_avg - older_avg) / older_avg
        
        if change < -0.15:  # 15% fewer errors
            return "improving"
        elif change > 0.15:  # 15% more errors
            return "declining"
        else:
            return "stable"
    
    def _get_recommended_exercises(self, weakness_areas: list) -> list:
        """
        Get recommended remedial exercises based on weakness patterns.
        """
        # Import remedial actions from sinhala_mappings
        from app.utils.sinhala_mappings import REMEDIAL_ACTIONS
        
        exercises = []
        for pattern in weakness_areas:
            if pattern in REMEDIAL_ACTIONS:
                exercises.append(REMEDIAL_ACTIONS[pattern])
            elif "Visual" in pattern and "Scrambling" in pattern:
                exercises.append(REMEDIAL_ACTIONS.get("Visual Sequencing (Scrambled)", ""))
            elif "Phonetic" in pattern:
                exercises.append(REMEDIAL_ACTIONS.get("Phonetic Confusion (Dental/Retroflex)", ""))
            elif "Visual" in pattern and "Reversal" in pattern:
                exercises.append(REMEDIAL_ACTIONS.get("Visual Reversal (Shape Confusion)", ""))
            elif "Grammar" in pattern:
                exercises.append(REMEDIAL_ACTIONS.get("Grammar (Spoken vs Written)", ""))
        
        return [e for e in exercises if e]  # Filter empty strings
    
    def _calculate_severity_score(
        self,
        sessions: list,
        pattern_distribution: dict,
        improvement_trend: str
    ) -> dict:
        """
        Calculate Dyslexia Severity Score (DSS) on a 0-100 scale.
        
        Formula: DSS = (errorRate × 0.4) + (patternDiversity × 0.3) + (consistency × 0.3)
        
        Components:
        - errorRate: Average errors per session, normalized to 0-100
        - patternDiversity: Number of different patterns (more = higher severity)
        - consistency: How consistent errors are across sessions
        
        Returns:
            Dict with score, level, and breakdown
        """
        if not sessions:
            return {
                "severityScore": 0.0,
                "severityLevel": "unknown",
                "severityBreakdown": {}
            }
        
        total_errors = sum(s.total_errors or 0 for s in sessions)
        total_sessions = len(sessions)
        avg_errors = total_errors / total_sessions if total_sessions else 0
        
        # Component 1: Error Rate (0-100)
        # Assume 10+ errors/session = maximum severity (100)
        error_rate_score = min(100, (avg_errors / 10) * 100)
        
        # Component 2: Pattern Diversity (0-100)
        # Having all 4 patterns = 100, 1 pattern = 25
        num_patterns = len(pattern_distribution)
        pattern_diversity_score = min(100, (num_patterns / 4) * 100)
        
        # Component 3: Consistency (0-100)
        # How consistent are errors across sessions? Higher variance = higher severity
        if total_sessions >= 2:
            error_counts = [s.total_errors or 0 for s in sessions]
            mean_errors = sum(error_counts) / len(error_counts)
            variance = sum((x - mean_errors) ** 2 for x in error_counts) / len(error_counts)
            std_dev = variance ** 0.5
            
            # High std_dev means inconsistent (could be random) - lower severity
            # Low std_dev means consistent errors - higher severity
            # Normalize: if std_dev is low relative to mean, consistency is high
            if mean_errors > 0:
                cv = std_dev / mean_errors  # Coefficient of variation
                consistency_score = max(0, min(100, (1 - cv) * 100))
            else:
                consistency_score = 0
        else:
            consistency_score = 50  # Unknown with only 1 session
        
        # Adjust for trend
        trend_modifier = 0
        if improvement_trend == "improving":
            trend_modifier = -10  # Reduce severity if improving
        elif improvement_trend == "declining":
            trend_modifier = 10  # Increase severity if declining
        
        # Calculate weighted score
        severity_score = (
            (error_rate_score * 0.4) +
            (pattern_diversity_score * 0.3) +
            (consistency_score * 0.3) +
            trend_modifier
        )
        
        # Clamp to 0-100
        severity_score = max(0, min(100, severity_score))
        severity_score = round(severity_score, 1)
        
        # Determine level
        if severity_score <= 30:
            severity_level = "mild"
        elif severity_score <= 60:
            severity_level = "moderate"
        else:
            severity_level = "severe"
        
        return {
            "severityScore": severity_score,
            "severityLevel": severity_level,
            "severityBreakdown": {
                "errorRate": round(error_rate_score, 1),
                "patternDiversity": round(pattern_diversity_score, 1),
                "consistency": round(consistency_score, 1),
                "trendModifier": trend_modifier
            }
        }


# Singleton instance
database_service = DatabaseService()


