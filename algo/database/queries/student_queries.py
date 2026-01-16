from typing import List, Dict, Optional, Tuple
from algo.database.db import get_db

class StudentQueries:
    @staticmethod
    def create_upload(session_id: int, batch_id: str, batch_name: str, filename: str, file_size: int, batch_color: str) -> int:
        db = get_db()
        cursor = db.execute("""
            INSERT INTO uploads (session_id, batch_id, batch_name, original_filename, file_size, batch_color)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, batch_id, batch_name, filename, file_size, batch_color))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def bulk_insert_students(students_data: List[tuple]):
        """
        students_data: list of (upload_id, batch_id, batch_name, enrollment, name, color, department)
        """
        db = get_db()
        db.executemany("""
            INSERT OR IGNORE INTO students 
            (upload_id, batch_id, batch_name, enrollment, name, batch_color, department)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, students_data)
        db.commit()

    @staticmethod
    def get_students_by_session(session_id: int) -> List[Dict]:
        """Get all students associated with a session (via uploads)"""
        db = get_db()
        cursor = db.execute("""
            SELECT s.* 
            FROM students s
            JOIN uploads u ON s.upload_id = u.id
            WHERE u.session_id = ?
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_batch_counts(session_id: Optional[int] = None) -> List[Dict]:
        db = get_db()
        if session_id:
            cursor = db.execute("""
                SELECT s.batch_name, COUNT(*) as count, MAX(s.batch_color) as color
                FROM students s
                JOIN uploads u ON s.upload_id = u.id
                WHERE u.session_id = ?
                GROUP BY s.batch_name
                ORDER BY s.batch_name
            """, (session_id,))
        else:
            cursor = db.execute("""
                SELECT batch_name, COUNT(*) as count, MAX(batch_color) as color
                FROM students
                GROUP BY batch_name
                ORDER BY batch_name
            """)
        return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def delete_upload_batch(upload_id: int):
        db = get_db()
        db.execute("DELETE FROM uploads WHERE id = ?", (upload_id,))
        # Students cascade deleted
        db.commit()
