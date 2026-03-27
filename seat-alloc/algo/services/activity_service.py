# Service for managing user activity logs with 7-day retention.
# Tracks user actions for audit and per-user activity history.
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ActivityService:
    """
    User activity logging service with configurable retention.
    
    Provides per-user activity logging with automatic cleanup of old entries.
    Default retention is 7 days.
    
    Usage:
        from algo.services.activity_service import ActivityService
        
        # Log an action
        ActivityService.log_action(user_id=1, action="Created session", details="session_id=5")
        
        # Get user's activity
        activities = ActivityService.get_user_activity(user_id=1, limit=50)
        
        # Cleanup old logs (called on startup)
        ActivityService.cleanup_old_logs()
    """
    
    LOG_RETENTION_DAYS = 7  # Keep logs for 7 days
    
    @staticmethod
    def log_action(
        user_id: int, 
        action: str, 
        details: str = None, 
        endpoint: str = None, 
        ip_address: str = None
    ) -> bool:
        """
        Log a user action to the activity log.
        
        Args:
            user_id: The user performing the action
            action: Description of the action (e.g., "Created session", "Uploaded file")
            details: Optional additional details
            endpoint: Optional API endpoint that was called
            ip_address: Optional IP address of the request
            
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            from algo.database.db import get_db
            db = get_db()
            
            db.execute("""
                INSERT INTO user_activity_log (user_id, action, details, endpoint, ip_address)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, action, details, endpoint, ip_address))
            db.commit()
            
            return True
        except Exception as e:
            logger.warning(f"Failed to log activity for user {user_id}: {e}")
            return False
    
    @staticmethod
    def get_user_activity(user_id: int, limit: int = 50, days: int = None) -> List[Dict]:
        """
        Get activity log for a specific user.
        
        Args:
            user_id: The user ID to get activity for
            limit: Maximum number of entries to return
            days: Optional number of days to look back (default: LOG_RETENTION_DAYS)
            
        Returns:
            List of activity log entries as dicts
        """
        try:
            from algo.database.db import get_db
            db = get_db()
            
            # Default to retention period
            if days is None:
                days = ActivityService.LOG_RETENTION_DAYS
            
            threshold = datetime.now() - timedelta(days=days)
            
            cursor = db.execute("""
                SELECT id, action, details, endpoint, ip_address, created_at
                FROM user_activity_log 
                WHERE user_id = ? AND created_at >= ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, threshold.isoformat(), limit))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get activity for user {user_id}: {e}")
            return []
    
    @staticmethod
    def cleanup_old_logs() -> int:
        """
        Delete activity logs older than the retention period.
        
        Should be called periodically (e.g., on app startup, daily cron).
        
        Returns:
            Number of deleted entries
        """
        try:
            from algo.database.db import get_db
            db = get_db()
            
            threshold = datetime.now() - timedelta(days=ActivityService.LOG_RETENTION_DAYS)
            
            cursor = db.execute("""
                DELETE FROM user_activity_log 
                WHERE created_at < ?
            """, (threshold.isoformat(),))
            
            deleted = cursor.rowcount
            db.commit()
            
            if deleted > 0:
                logger.info(f"🧹 Cleaned up {deleted} activity log entries older than {ActivityService.LOG_RETENTION_DAYS} days")
            
            return deleted
        except Exception as e:
            logger.error(f"Failed to cleanup old activity logs: {e}")
            return 0
    
    @staticmethod
    def get_activity_summary(user_id: int, days: int = 7) -> Dict:
        """
        Get a summary of user activity over a period.
        
        Args:
            user_id: The user ID to summarize
            days: Number of days to look back
            
        Returns:
            Dict with action counts and recent activity
        """
        try:
            from algo.database.db import get_db
            db = get_db()
            
            threshold = datetime.now() - timedelta(days=days)
            
            # Count actions by type
            cursor = db.execute("""
                SELECT action, COUNT(*) as count
                FROM user_activity_log 
                WHERE user_id = ? AND created_at >= ?
                GROUP BY action
                ORDER BY count DESC
                LIMIT 10
            """, (user_id, threshold.isoformat()))
            
            action_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Total count
            cursor = db.execute("""
                SELECT COUNT(*) FROM user_activity_log 
                WHERE user_id = ? AND created_at >= ?
            """, (user_id, threshold.isoformat()))
            
            total_count = cursor.fetchone()[0]
            
            return {
                'user_id': user_id,
                'period_days': days,
                'total_actions': total_count,
                'action_breakdown': action_counts
            }
        except Exception as e:
            logger.error(f"Failed to get activity summary for user {user_id}: {e}")
            return {'user_id': user_id, 'total_actions': 0, 'action_breakdown': {}}
