"""
Services Layer - Business Logic Abstraction
============================================

These services encapsulate all business logic and should be used by:
- API Blueprints (HTTP layer)
- CLI commands (future)
- Background jobs (future)
- Tests

Usage:
    from algo.services import SessionService, StudentService, AllocationService
    
    # In a blueprint:
    result = SessionService.create_session(name, user_id)
    
    # Get students for a session
    students = StudentService.get_session_students(session_id)
    
    # Generate allocation
    allocation = AllocationService.allocate_classroom(session_id, classroom, distribution)
"""

from .session_service import SessionService
from .student_service import StudentService
from .allocation_service import AllocationService
from . import auth_service

__all__ = [
    'SessionService',
    'StudentService',
    'AllocationService',
    'auth_service',
]
