import sqlite3
import datetime
from typing import Optional, Dict, List
from algo.database.db import get_db

class SessionQueries:
    @staticmethod
    def get_session_by_id(session_id: int) -> Optional[Dict]:
        db = get_db()
        cursor = db.execute("SELECT * FROM allocation_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_session_by_plan_id(plan_id: str) -> Optional[Dict]:
        db = get_db()
        cursor = db.execute("SELECT * FROM allocation_sessions WHERE plan_id = ?", (plan_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def create_session(plan_id: str, user_id: int = 1, name: str = None) -> int:
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO allocation_sessions (plan_id, user_id, name, status, created_at)
            VALUES (?, ?, ?, 'active', CURRENT_TIMESTAMP)
            """,
            (plan_id, user_id, name)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update_session_stats(session_id: int, total: int, allocated: int):
        db = get_db()
        db.execute(
            """
            UPDATE allocation_sessions 
            SET total_students = ?, allocated_count = ?, last_activity = CURRENT_TIMESTAMP
            WHERE session_id = ?
            """,
            (total, allocated, session_id)
        )
        db.commit()

    @staticmethod
    def mark_session_completed(session_id: int):
        db = get_db()
        db.execute(
            """
            UPDATE allocation_sessions 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP 
            WHERE session_id = ?
            """,
            (session_id,)
        )
        db.commit()

    @staticmethod
    def expire_session(session_id: int, hard_delete: bool = False):
        db = get_db()
        if hard_delete:
            db.execute("DELETE FROM allocation_sessions WHERE session_id = ?", (session_id,))
        else:
            db.execute(
                "UPDATE allocation_sessions SET status = 'expired' WHERE session_id = ?",
                (session_id,)
            )
        db.commit()
    
    @staticmethod
    def get_active_sessions(user_id: Optional[int] = None) -> List[Dict]:
        db = get_db()
        query = "SELECT * FROM allocation_sessions WHERE status IN ('active', 'completed')"
        params = []
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY created_at DESC"
        cursor = db.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def check_empty_session(session_id: int) -> bool:
        db = get_db()
        cursor = db.execute("""
            SELECT 
                (SELECT COUNT(*) FROM uploads WHERE session_id = ?) as upload_count,
                (SELECT COUNT(*) FROM allocations WHERE session_id = ?) as allocation_count
        """, (session_id, session_id))
        row = cursor.fetchone()
        if not row:
            return True # Treat non-existent as empty/deletable
        return row['upload_count'] == 0 and row['allocation_count'] == 0
