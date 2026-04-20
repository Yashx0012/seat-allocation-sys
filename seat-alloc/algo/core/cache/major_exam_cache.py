"""
Major Exam Cache Manager
Handles cache operations for major exam plans
"""
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class MajorExamCacheManager:
    """Manages cache for major exam plans"""
    
    def __init__(self, cache_dir='cache'):
        self.cache_dir = Path(cache_dir)
        self.major_dir = self.cache_dir / 'major'
        self.major_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_user_dir(self, user_id: str) -> Path:
        """Get user-specific directory, maintaining isolation"""
        user_dir = self.major_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def generate_plan_id(self) -> str:
        """Generate unique plan ID for major exam"""
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"PLAN-major-{unique_id}"

    def _sanitize_plan_id(self, plan_id: str) -> str:
        """Allow only safe filename characters for plan IDs."""
        safe_plan_id = ''.join(c for c in str(plan_id) if c.isalnum() or c in ('-', '_'))
        if not safe_plan_id:
            raise ValueError('Invalid plan_id')
        return safe_plan_id
    
    def _get_plan_path(self, user_id: str, plan_id: str) -> Path:
        """Get full path to plan file"""
        user_dir = self._get_user_dir(user_id)
        safe_plan_id = self._sanitize_plan_id(plan_id)
        return user_dir / f"{safe_plan_id}.json"
    
    def store_plan(self, user_id: str, plan_id: str, plan_data: dict) -> bool:
        """Store plan in cache"""
        try:
            path = self._get_plan_path(user_id, plan_id)
            
            # Ensure metadata exists
            if 'metadata' not in plan_data:
                plan_data['metadata'] = {}
            
            created_at = plan_data.get('created_at')
            if not created_at and path.exists():
                try:
                    with open(path, 'r') as existing_file:
                        existing_plan = json.load(existing_file)
                    created_at = existing_plan.get('created_at')
                except Exception as e:
                    logger.warning('Failed to preserve created_at for %s: %s', plan_id, e)

            if not created_at:
                created_at = datetime.utcnow().isoformat() + 'Z'

            plan_data['user_id'] = user_id
            plan_data['plan_id'] = plan_id
            plan_data['created_at'] = created_at
            
            # Write to file
            with open(path, 'w') as f:
                json.dump(plan_data, f, indent=2)
            
            # VERIFY file was actually written
            if not path.exists():
                logger.error('File write verification failed: path=%s parent=%s parent_exists=%s', path, path.parent, path.parent.exists())
                return False
            
            # Verify file has content
            file_size = path.stat().st_size
            if file_size == 0:
                logger.error('File is empty after write: %s', path)
                return False
            
            logger.info('Stored major plan: user_id=%s plan_id=%s path=%s size=%s', user_id, plan_id, path, file_size)
            return True
        except Exception as e:
            logger.exception('Error storing major plan: user_id=%s plan_id=%s error=%s', user_id, plan_id, e)
            return False
    
    def retrieve_plan(self, user_id: str, plan_id: str) -> dict:
        """Retrieve plan from cache"""
        try:
            path = self._get_plan_path(user_id, plan_id)
            
            if not path.exists():
                return None
            
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error('Error retrieving major plan: user_id=%s plan_id=%s error=%s', user_id, plan_id, e)
            return None
    
    def update_plan(self, user_id: str, plan_id: str, plan_data: dict) -> bool:
        """Update existing plan"""
        return self.store_plan(user_id, plan_id, plan_data)
    
    def get_all_user_plans(self, user_id: str, limit: int = 5) -> list:
        """Get recent plans for a user (newest first)"""
        try:
            user_dir = self._get_user_dir(user_id)
            
            plans = []
            for file in sorted(
                user_dir.glob('PLAN-major-*.json'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )[:limit]:
                with open(file, 'r') as f:
                    plan = json.load(f)
                    plans.append({
                        'plan_id': plan.get('plan_id'),
                        'created_at': plan.get('created_at'),
                        'total_students': plan.get('metadata', {}).get('total_students', 0),
                        'allocated_count': plan.get('metadata', {}).get('allocated_count', 0),
                        'room_count': plan.get('metadata', {}).get('room_count', 0),
                        'status': plan.get('metadata', {}).get('status', 'pending')
                    })
            
            return plans
        except Exception as e:
            logger.error('Error getting major plans for user_id=%s: %s', user_id, e)
            return []
    
    def plan_exists(self, user_id: str, plan_id: str) -> bool:
        """Check if plan exists"""
        try:
            path = self._get_plan_path(user_id, plan_id)
            return path.exists()
        except Exception:
            return False
    
    def delete_plan(self, user_id: str, plan_id: str) -> bool:
        """Delete a plan"""
        try:
            path = self._get_plan_path(user_id, plan_id)
            
            if path.exists():
                path.unlink()
                return True
            
            return False
        except Exception as e:
            logger.error('Error deleting major plan: user_id=%s plan_id=%s error=%s', user_id, plan_id, e)
            return False
    
    def cleanup_old_plans(self, days: int = 30) -> int:
        """Remove plans older than specified days"""
        try:
            import time
            
            current_time = time.time()
            cutoff_time = current_time - (days * 86400)  # 86400 seconds per day
            
            deleted_count = 0
            for user_dir in self.major_dir.iterdir():
                if user_dir.is_dir():
                    for plan_file in user_dir.glob('PLAN-major-*.json'):
                        file_time = plan_file.stat().st_mtime
                        if file_time < cutoff_time:
                            plan_file.unlink()
                            deleted_count += 1
            
            if deleted_count > 0:
                logger.info('Cleaned up %s old major exam plans', deleted_count)
            
            return deleted_count
        except Exception as e:
            logger.error('Error cleaning up major exam plans: %s', e)
            return 0


# Singleton instance
_cache_manager = None

def get_major_cache_manager(cache_dir='cache'):
    """Get or create singleton cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = MajorExamCacheManager(cache_dir)
    return _cache_manager
