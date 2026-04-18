"""
Major Exam Cache Manager
Handles cache operations for major exam plans
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
import shutil


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
    
    def _get_plan_path(self, user_id: str, plan_id: str) -> Path:
        """Get full path to plan file"""
        user_dir = self._get_user_dir(user_id)
        return user_dir / f"{plan_id}.json"
    
    def store_plan(self, user_id: str, plan_id: str, plan_data: dict) -> bool:
        """Store plan in cache"""
        try:
            path = self._get_plan_path(user_id, plan_id)
            
            # Ensure metadata exists
            if 'metadata' not in plan_data:
                plan_data['metadata'] = {}
            
            plan_data['user_id'] = user_id
            plan_data['plan_id'] = plan_id
            plan_data['created_at'] = datetime.utcnow().isoformat() + 'Z'
            
            # Write to file
            with open(path, 'w') as f:
                json.dump(plan_data, f, indent=2)
            
            # VERIFY file was actually written
            if not path.exists():
                print(f"❌ CRITICAL: File write verification FAILED: {path}")
                print(f"   Parent dir: {path.parent}")
                print(f"   Parent exists: {path.parent.exists()}")
                return False
            
            # Verify file has content
            file_size = path.stat().st_size
            if file_size == 0:
                print(f"❌ CRITICAL: File is empty after write: {path}")
                return False
            
            print(f"✅ STORED PLAN: user_id={user_id}, plan_id={plan_id}")
            print(f"   Path: {path}")
            print(f"   Size: {file_size} bytes")
            return True
        except Exception as e:
            print(f"❌ Error storing plan: {e}")
            print(f"   user_id: {user_id}")
            print(f"   plan_id: {plan_id}")
            import traceback
            traceback.print_exc()
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
            print(f"❌ Error retrieving plan: {e}")
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
            print(f"❌ Error getting user plans: {e}")
            return []
    
    def plan_exists(self, user_id: str, plan_id: str) -> bool:
        """Check if plan exists"""
        path = self._get_plan_path(user_id, plan_id)
        return path.exists()
    
    def delete_plan(self, user_id: str, plan_id: str) -> bool:
        """Delete a plan"""
        try:
            path = self._get_plan_path(user_id, plan_id)
            
            if path.exists():
                path.unlink()
                return True
            
            return False
        except Exception as e:
            print(f"❌ Error deleting plan: {e}")
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
                print(f"🗑️  Cleaned up {deleted_count} old major exam plans")
            
            return deleted_count
        except Exception as e:
            print(f"❌ Error cleaning up plans: {e}")
            return 0


# Singleton instance
_cache_manager = None

def get_major_cache_manager(cache_dir='cache'):
    """Get or create singleton cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = MajorExamCacheManager(cache_dir)
    return _cache_manager
