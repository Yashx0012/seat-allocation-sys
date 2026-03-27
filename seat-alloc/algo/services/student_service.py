# Service for high-level student and batch data operations.
# Manages the processing of student uploads and provides access to session-bound student data.
import logging
import os
from werkzeug.utils import secure_filename
from typing import Dict, List, Optional
from algo.database.queries.student_queries import StudentQueries
from algo.utils.parser import StudentDataParser
from algo.config.settings import Config

logger = logging.getLogger(__name__)


class StudentService:
    """
    Student data management service.
    
    Handles all student-related business logic including:
    - File upload processing (Excel/CSV)
    - Student data validation and parsing
    - Batch information extraction
    - Session-bound student queries
    
    Usage:
        from algo.services import StudentService
        
        # Process an uploaded file
        result = StudentService.process_student_upload(
            session_id=5,
            file_obj=uploaded_file,
            batch_name="CSE-2024",
            batch_color="#BFDBFE"
        )
        
        # Get students for a session
        students = StudentService.get_session_students(session_id=5)
        
        # Get batch summary
        batches = StudentService.get_batch_summary(session_id=5)
    """

    @staticmethod
    def process_student_upload(session_id: int, file_obj, batch_name: str, batch_color: str) -> Dict:
        """
        Handle file upload, parse content, and save to DB.
        """
        # 1. Secure filename and save temp (optional, parser handles stream needed?)
        # Parser handles stream.
        filename = secure_filename(file_obj.filename)
        
        # 2. Parse Data
        parser = StudentDataParser()
        try:
            # Using mode 2 for Name+Enrollment
            result = parser.parse_file(
                file_input=file_obj,
                mode=2,
                batch_name=batch_name,
                batch_color=batch_color
            )
        except Exception as e:
            logger.error(f"Parser error: {e}")
            raise ValueError(f"Failed to parse file: {str(e)}")
            
        if result.rows_extracted == 0:
            raise ValueError("No valid student records found in file")

        # 3. Create Upload Record
        batch_id = result.batch_id
        file_size = 0 # Can get from stream if needed, or result
        upload_id = StudentQueries.create_upload(
            session_id, batch_id, batch_name, filename, file_size, result.batch_color
        )
        
        # 4. Bulk Insert Students
        students_data = [] # (upload_id, batch_id, batch_name, enrollment, name, color, department)
        
        # result.data is { batch_name: [ {name, enrollmentNo, department}, ... ] }
        batch_data = result.data.get(batch_name, [])
        
        for student in batch_data:
            students_data.append((
                upload_id,
                batch_id,
                batch_name,
                student['enrollmentNo'],
                student['name'],
                result.batch_color,
                student['department']
            ))
            
        StudentQueries.bulk_insert_students(students_data)
        
        return {
            "upload_id": upload_id,
            "batch_id": batch_id,
            "count": len(students_data),
            "warnings": result.warnings
        }

    @staticmethod
    def get_session_students(session_id: int) -> List[Dict]:
        return StudentQueries.get_students_by_session(session_id)
        
    @staticmethod
    def get_batch_summary(session_id: int) -> List[Dict]:
        return StudentQueries.get_batch_counts(session_id)
