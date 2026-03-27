from typing import List, Dict, Optional
from algo.database.db import get_db

class AllocationQueries:
    @staticmethod
    def get_allocations_by_session(session_id: int) -> List[Dict]:
        db = get_db()
        cursor = db.execute("""
            SELECT a.seat_position, a.paper_set, a.enrollment, s.name, s.batch_name, c.name as room_name, a.classroom_id
            FROM allocations a
            JOIN students s ON a.student_id = s.id
            LEFT JOIN classrooms c ON a.classroom_id = c.id
            WHERE a.session_id = ?
            ORDER BY c.name, a.seat_position
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def save_allocation_batch(allocations: List[tuple]):
        """
        Bulk insert allocations.
        allocations: list of (session_id, classroom_id, student_id, enrollment, seat_pos, batch_name, paper_set)
        """
        db = get_db()
        db.executemany("""
            INSERT INTO allocations 
            (session_id, classroom_id, student_id, enrollment, seat_position, batch_name, paper_set)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, allocations)
        db.commit()

    @staticmethod
    def clear_session_allocations(session_id: int):
        db = get_db()
        db.execute("DELETE FROM allocations WHERE session_id = ?", (session_id,))
        db.commit()
    
    @staticmethod
    def get_allocated_student_ids(session_id: int) -> List[int]:
        db = get_db()
        cursor = db.execute("SELECT student_id FROM allocations WHERE session_id = ?", (session_id,))
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def get_allocated_rooms(session_id: int) -> List[Dict]:
        """
        Get list of rooms with allocation counts for a session.
        
        Args:
            session_id: The session ID to get rooms for
            
        Returns:
            List of dicts with classroom_id, classroom_name, and count
        """
        db = get_db()
        cursor = db.execute("""
            SELECT 
                a.classroom_id,
                c.name as classroom_name,
                COUNT(*) as count
            FROM allocations a
            LEFT JOIN classrooms c ON a.classroom_id = c.id
            WHERE a.session_id = ?
            GROUP BY a.classroom_id
            ORDER BY c.name
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]
