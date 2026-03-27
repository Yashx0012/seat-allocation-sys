"""
Query Layer - Database Access Abstraction
==========================================

These query classes handle all direct database operations.
They are used by the Services layer.

Usage:
    from algo.database.queries import SessionQueries, StudentQueries
    
    # Get session by ID
    session = SessionQueries.get_session_by_id(session_id)
    
    # Get students for a session
    students = StudentQueries.get_students_by_session(session_id)
"""

from .session_queries import SessionQueries
from .allocation_queries import AllocationQueries
from .student_queries import StudentQueries
from .user_queries import UserQueries

__all__ = [
    'SessionQueries',
    'AllocationQueries',
    'StudentQueries',
    'UserQueries',
]
