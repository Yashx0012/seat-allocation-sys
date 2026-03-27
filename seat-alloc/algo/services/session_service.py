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
    """
    Session management service.
    
    Handles all session-related business logic including:
    - Session CRUD operations
    - Session state management (active, completed, archived)
    - Session statistics and expiry checks
    
    Usage:
        from algo.services import SessionService
        
        # Create a new session
        result = SessionService.create_session("Midterm Exam", user_id=1)
        
        # Get session details
        session = SessionService.get_session(session_id=5)
        
        # Get all sessions for a user
        sessions = SessionService.get_user_sessions(user_id=1)
        
        # Finalize a session
        SessionService.finalize_session(session_id=5)
    """

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
    def delete_session(session_id: int, hard_delete: bool = False) -> Dict:
        """
        Delete or expire a session.
        
        Args:
            session_id: ID of session to delete
            hard_delete: If True, permanently delete with CASCADE. If False, soft delete (expire).
        
        Returns:
            Dict with 'success', 'message' or 'error'
        """
        try:
            session = SessionQueries.get_session_by_id(session_id)
            if not session:
                return {'success': False, 'error': 'Session not found'}
            
            SessionQueries.expire_session(session_id, hard_delete=hard_delete)
            
            action = 'permanently deleted' if hard_delete else 'expired'
            logger.info(f"Session {session_id} {action}")
            
            return {'success': True, 'message': f'Session {session_id} {action}'}
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return {'success': False, 'error': str(e)}

    # Session timeout configuration
    SESSION_INACTIVE_TIMEOUT_MINUTES = 120  # 2 hours - sessions inactive longer than this are considered stale
    SESSION_ABANDONED_TIMEOUT_MINUTES = 30   # 30 minutes - for auto-expiring during session resume

    @staticmethod
    def check_expiry(session_id: int) -> Tuple[bool, str]:
        """Check if session should be expired based on inactivity"""
        session = SessionQueries.get_session_by_id(session_id)
        if not session:
            return True, "Session not found"
        
        if session['status'] in ['completed', 'archived', 'expired']:
            return False, f"Session is {session['status']}"
            
        # Check last activity
        last_activity_str = session.get('last_activity')
        if last_activity_str:
            try:
                last_activity = datetime.datetime.fromisoformat(str(last_activity_str).replace('Z', '+00:00'))
                last_activity = last_activity.replace(tzinfo=None)  # Make timezone naive
                inactive_duration = datetime.datetime.now() - last_activity
                inactive_minutes = int(inactive_duration.total_seconds() / 60)
                
                if inactive_minutes > SessionService.SESSION_INACTIVE_TIMEOUT_MINUTES:
                    return True, f"Inactive for {inactive_minutes} minutes (threshold: {SessionService.SESSION_INACTIVE_TIMEOUT_MINUTES})"
            except Exception as e:
                logger.warning(f"Error parsing last_activity: {e}")
        
        return False, "Active"

    @staticmethod
    def update_stats(session_id: int) -> Dict:
        """
        Recalculate and update student counts and allocation counts for a session.
        
        Returns:
            Dict with success status and updated counts
        """
        try:
            student_counts = StudentQueries.get_batch_counts(session_id)
            total_students = sum(s['count'] for s in student_counts)
            allocated_ids = AllocationQueries.get_allocated_student_ids(session_id)
            allocated_count = len(allocated_ids)
            pending_count = max(0, total_students - allocated_count)
            
            SessionQueries.update_session_stats(session_id, total_students, allocated_count)
            
            logger.info(f"Refreshed session {session_id}: total={total_students}, allocated={allocated_count}")
            
            return {
                'success': True,
                'total_students': total_students,
                'allocated_count': allocated_count,
                'pending_count': pending_count
            }
        except Exception as e:
            logger.error(f"Error updating stats for session {session_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_active_session(user_id: int) -> Optional[Dict]:
        """
        Get the current active session for a user.
        
        Returns:
            Dict with session data including allocated_rooms, or None if no active session
        """
        try:
            session = SessionQueries.get_active_session_for_user(user_id)
            if not session:
                return None
            
            # Get allocated rooms
            allocated_rooms = AllocationQueries.get_allocated_rooms(session['session_id'])
            
            total = session.get('total_students') or 0
            allocated = session.get('allocated_count') or 0
            
            return {
                'session_id': session['session_id'],
                'plan_id': session.get('plan_id'),
                'total_students': total,
                'allocated_count': allocated,
                'pending_count': max(0, total - allocated),
                'status': session.get('status'),
                'created_at': session.get('created_at'),
                'last_activity': session.get('last_activity'),
                'user_id': session.get('user_id'),
                'allocated_rooms': allocated_rooms
            }
        except Exception as e:
            logger.error(f"Error getting active session for user {user_id}: {e}")
            return None

    @staticmethod
    def get_session_with_rooms(session_id: int) -> Optional[Dict]:
        """
        Get session by ID with allocated rooms included.
        
        Returns:
            Dict with session data and allocated_rooms list
        """
        try:
            session = SessionQueries.get_session_by_id(session_id)
            if not session:
                return None
            
            allocated_rooms = AllocationQueries.get_allocated_rooms(session_id)
            session['allocated_rooms'] = allocated_rooms
            
            return session
        except Exception as e:
            logger.error(f"Error getting session {session_id} with rooms: {e}")
            return None

    @staticmethod
    def expire_all_active(user_id: Optional[int] = None) -> Dict:
        """
        Expire all active sessions, optionally filtered by user.
        
        Args:
            user_id: If provided, only expire sessions for this user
        
        Returns:
            Dict with success status and count of expired sessions
        """
        try:
            expired_count = SessionQueries.expire_all_active_sessions(user_id)
            logger.info(f"Force-expired {expired_count} active session(s)" + (f" for user {user_id}" if user_id else ""))
            
            return {
                'success': True,
                'message': f'Expired {expired_count} active sessions',
                'expired_count': expired_count
            }
        except Exception as e:
            logger.error(f"Error expiring all active sessions: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def auto_expire_stale_sessions() -> Dict:
        """
        Automatically expire sessions that have been inactive longer than the timeout.
        
        This should be called periodically (e.g., on app startup or via cron).
        
        Returns:
            Dict with success status and count of expired sessions
        """
        try:
            from algo.database.db import get_db
            db = get_db()
            
            # Calculate threshold time
            threshold_minutes = SessionService.SESSION_INACTIVE_TIMEOUT_MINUTES
            
            # Expire sessions inactive longer than threshold
            cursor = db.execute("""
                UPDATE allocation_sessions 
                SET status = 'expired', last_activity = CURRENT_TIMESTAMP
                WHERE status = 'active' 
                AND last_activity IS NOT NULL
                AND datetime(last_activity) < datetime('now', ? || ' minutes')
            """, (f'-{threshold_minutes}',))
            
            expired_count = cursor.rowcount
            db.commit()
            
            if expired_count > 0:
                logger.info(f"⏰ Auto-expired {expired_count} stale session(s) (inactive > {threshold_minutes} min)")
            
            return {
                'success': True,
                'expired_count': expired_count,
                'threshold_minutes': threshold_minutes
            }
        except Exception as e:
            logger.error(f"Error auto-expiring stale sessions: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def claim_orphaned_sessions(user_id: int) -> Dict:
        """
        Claim sessions with user_id=1 (orphaned) for the current user.
        
        Args:
            user_id: User ID to claim sessions for
        
        Returns:
            Dict with success status and count of claimed sessions
        """
        try:
            if user_id == 1:
                return {'success': False, 'error': 'Cannot claim with default user'}
            
            claimed_count = SessionQueries.claim_orphaned_sessions(user_id)
            
            if claimed_count > 0:
                logger.info(f"User {user_id} claimed {claimed_count} orphaned session(s)")
            
            return {'success': True, 'claimed': claimed_count}
        except Exception as e:
            logger.error(f"Error claiming orphaned sessions: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def list_sessions(user_id: int, status_filter: str = None, limit: int = 50) -> Dict:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User ID to get sessions for
            status_filter: Optional status filter
            limit: Max sessions to return
            
        Returns:
            Dict with success, sessions list, and count
        """
        try:
            sessions = SessionQueries.get_user_sessions(user_id, status_filter, limit)
            return {
                'success': True,
                'sessions': sessions,
                'count': len(sessions)
            }
        except Exception as e:
            logger.error(f"Error listing sessions for user {user_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_session_uploads(session_id: int) -> Dict:
        """
        Get all uploads/batches for a session.
        
        Returns:
            Dict with success, session_id, uploads list, and count
        """
        try:
            uploads = StudentQueries.get_session_uploads(session_id)
            return {
                'success': True,
                'session_id': session_id,
                'uploads': uploads,
                'count': len(uploads)
            }
        except Exception as e:
            logger.error(f"Error getting uploads for session {session_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_session_statistics(session_id: int) -> Dict:
        """
        Get comprehensive statistics for a session.
        
        Returns:
            Dict with success and stats object containing room/batch breakdowns
        """
        try:
            stats = SessionQueries.get_session_stats(session_id)
            if not stats:
                return {'success': False, 'error': 'Session not found'}
            return {'success': True, 'stats': stats}
        except Exception as e:
            logger.error(f"Error getting stats for session {session_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def start_or_resume_session(user_id: int, upload_ids: List[int], force_new: bool = False) -> Dict:
        """
        Smart session management - start new or resume existing session.
        
        Logic:
        - If active session exists and recent → add uploads to it
        - If active session is abandoned (>30min) or empty → expire it, create new
        - If no active session → create new
        
        Args:
            user_id: User ID
            upload_ids: List of upload IDs to include
            force_new: If True, always create new session
            
        Returns:
            Dict with session info and whether it was added to existing
        """
        import random
        import string
        from algo.database.db import get_db
        
        if not upload_ids:
            return {'success': False, 'error': 'No upload IDs provided'}
        
        db = get_db()
        
        try:
            # STRICT: Only check this user's active sessions (no cross-user leakage)
            cursor = db.execute("""
                SELECT session_id, last_activity, allocated_count, total_students, plan_id, user_id
                FROM allocation_sessions 
                WHERE status = 'active' AND user_id = ?
                ORDER BY last_activity DESC
                LIMIT 1
            """, (user_id,))
            existing = cursor.fetchone()
            
            if existing and not force_new:
                existing_id = existing['session_id']
                last_activity = existing['last_activity']
                allocated = existing['allocated_count']
                total = existing['total_students']
                plan_id = existing['plan_id']
                
                # Check if abandoned (using class constant)
                is_abandoned = False
                if last_activity:
                    try:
                        last_active = datetime.datetime.fromisoformat(str(last_activity).replace('Z', '+00:00'))
                        inactive_duration = datetime.datetime.now() - last_active.replace(tzinfo=None)
                        is_abandoned = inactive_duration > datetime.timedelta(minutes=SessionService.SESSION_ABANDONED_TIMEOUT_MINUTES)
                    except Exception as e:
                        logger.warning(f"Date parse warning: {e}")
                
                is_empty = (total or 0) == 0 and (allocated or 0) == 0
                
                if is_abandoned or is_empty:
                    # Expire abandoned/empty session
                    reason = "empty" if is_empty else "abandoned"
                    logger.info(f"Auto-expiring {reason} session {existing_id}")
                    db.execute("""
                        UPDATE allocation_sessions SET status = 'expired' WHERE session_id = ?
                    """, (existing_id,))
                    db.commit()
                    # Continue to create new session
                else:
                    # Add uploads to existing session
                    logger.info(f"Adding {len(upload_ids)} uploads to existing session {existing_id}")
                    
                    linked_count = 0
                    for upload_id in upload_ids:
                        cursor = db.execute("""
                            UPDATE uploads SET session_id = ?
                            WHERE id = ? AND (session_id IS NULL OR session_id = ?)
                        """, (existing_id, upload_id, existing_id))
                        linked_count += cursor.rowcount
                    
                    # Recalculate total students
                    cursor = db.execute("""
                        SELECT COUNT(*) FROM students s
                        JOIN uploads u ON s.upload_id = u.id
                        WHERE u.session_id = ?
                    """, (existing_id,))
                    new_total = cursor.fetchone()[0] or 0
                    
                    # Get current allocated count
                    cursor = db.execute("SELECT COUNT(*) FROM allocations WHERE session_id = ?", (existing_id,))
                    current_allocated = cursor.fetchone()[0] or 0
                    
                    # Update session
                    db.execute("""
                        UPDATE allocation_sessions
                        SET total_students = ?, allocated_count = ?, last_activity = CURRENT_TIMESTAMP,
                            user_id = COALESCE(user_id, ?)
                        WHERE session_id = ?
                    """, (new_total, current_allocated, user_id, existing_id))
                    
                    db.commit()
                    
                    # Get allocated rooms
                    allocated_rooms = AllocationQueries.get_allocated_rooms(existing_id)
                    
                    pending_count = max(0, new_total - current_allocated)
                    
                    logger.info(f"Added to session {existing_id}: total={new_total}, allocated={current_allocated}")
                    
                    return {
                        'success': True,
                        'message': f'Added {linked_count} uploads to existing session',
                        'added_to_existing': True,
                        'session': {
                            'session_id': existing_id,
                            'plan_id': plan_id,
                            'total_students': new_total,
                            'allocated_count': current_allocated,
                            'pending_count': pending_count,
                            'allocated_rooms': allocated_rooms
                        }
                    }
            
            # Create new session
            plan_id = f"PLAN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
            
            # Calculate total students from uploads
            total_students = 0
            if upload_ids:
                placeholders = ','.join('?' * len(upload_ids))
                cursor = db.execute(f"""
                    SELECT COUNT(*) FROM students 
                    WHERE upload_id IN ({placeholders})
                """, upload_ids)
                total_students = cursor.fetchone()[0] or 0
            
            # Create session
            cursor = db.execute("""
                INSERT INTO allocation_sessions 
                (user_id, plan_id, total_students, allocated_count, status, created_at, last_activity)
                VALUES (?, ?, ?, 0, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (user_id, plan_id, total_students))
            
            session_id = cursor.lastrowid
            
            # Link uploads to session
            for upload_id in upload_ids:
                db.execute("UPDATE uploads SET session_id = ? WHERE id = ?", (session_id, upload_id))
            
            db.commit()
            
            logger.info(f"Created session {session_id} with {total_students} students")
            
            return {
                'success': True,
                'added_to_existing': False,
                'session': {
                    'session_id': session_id,
                    'plan_id': plan_id,
                    'total_students': total_students,
                    'allocated_count': 0,
                    'pending_count': total_students,
                    'allocated_rooms': []
                }
            }
            
        except Exception as e:
            logger.error(f"Error in start_or_resume_session: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
