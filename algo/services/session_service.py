# Service for managing allocation sessions and their lifecycle.
# Handles session creation, status transitions, finalization, and statistical updates.
import logging
import uuid
import datetime
from typing import Dict, List, Optional, Tuple
from algo.database.queries.session_queries import SessionQueries
from algo.database.queries.allocation_queries import AllocationQueries
from algo.database.queries.student_queries import StudentQueries

logger = logging.getLogger(__name__)

class SessionService:
    @staticmethod
    def create_session(name: Optional[str], user_id: int) -> Dict:
        """Create a new session, returning the session object."""
        plan_id = str(uuid.uuid4())
        session_id = SessionQueries.create_session(plan_id, user_id, name)
        logger.info(f"Created session {session_id} with plan_id {plan_id}")
        return {
            'session_id': session_id,
            'plan_id': plan_id,
            'user_id': user_id,
            'name': name
        }

    @staticmethod
    def get_session(session_id: int) -> Optional[Dict]:
        """Get session by ID"""
        return SessionQueries.get_session_by_id(session_id)

    @staticmethod
    def get_user_sessions(user_id: int) -> List[Dict]:
        """Get all active/completed sessions for a user"""
        return SessionQueries.get_active_sessions(user_id)

    @staticmethod
    def finalize_session(session_id: int):
        """Finalize a session (mark as completed)"""
        SessionQueries.mark_session_completed(session_id)
        # TODO: clean up temp files or prune cache via pdf_service/cache_manager if needed

    @staticmethod
    def delete_session(session_id: int):
        """Delete/Expire session"""
        SessionQueries.expire_session(session_id)

    @staticmethod
    def check_expiry(session_id: int) -> Tuple[bool, str]:
        """Check if session should be expired logic"""
        # Logic copied from original app.py
        session = SessionQueries.get_session_by_id(session_id)
        if not session:
            return True, "Session not found"
        
        if session['status'] in ['completed', 'archived']:
            return False, "Session is completed/archived"
            
        # Check last activity
        # This part requires access to user_activity or session last_activity
        # Assuming last_activity on session is updated
        last_activity_str = session.get('last_activity')
        if last_activity_str:
            last_activity = datetime.datetime.fromisoformat(last_activity_str)
            inactive_duration = datetime.datetime.now() - last_activity
            if inactive_duration > datetime.timedelta(minutes=30):
                return True, f"Inactive for {int(inactive_duration.total_seconds() / 60)} minutes"
        
        return False, "Active"

    @staticmethod
    def update_stats(session_id: int):
        """Update student counts and allocation counts in session stats"""
        student_counts = StudentQueries.get_batch_counts(session_id)
        total_students = sum(s['count'] for s in student_counts)
        allocated_ids = AllocationQueries.get_allocated_student_ids(session_id)
        allocated_count = len(allocated_ids)
        
        SessionQueries.update_session_stats(session_id, total_students, allocated_count)
