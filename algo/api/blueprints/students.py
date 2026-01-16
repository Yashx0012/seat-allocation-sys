# Student data management endpoints.
# Handles Excel/CSV file uploads, student data parsing, and batch persistence to the database.
from flask import Blueprint, request, jsonify
from algo.services.student_service import StudentService
from algo.utils.parser import StudentDataParser
from algo.auth_service import token_required
import logging
import os

student_bp = Blueprint('students', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@student_bp.route('/upload', methods=['POST'])
@token_required
def upload_students():
    """
    Step 1: Parse and preview student data
    """
    try:
        file = request.files.get('file')
        mode = int(request.form.get('mode', 2))
        batch_name = request.form.get('batch_name', 'Default')
        
        name_col = request.form.get('nameColumn')
        enrollment_col = request.form.get('enrollmentColumn')
        
        if not file:
            return jsonify({"error": "No file uploaded"}), 400
            
        parser = StudentDataParser()
        preview_data = parser.preview(file)
        
        # If preview failed
        if "error" in preview_data:
            return jsonify({"error": preview_data["error"]}), 400
            
        # Perform actual parse to get batch_id and sample
        parse_result = parser.parse_file(
            file_input=file,
            mode=mode,
            batch_name=batch_name,
            name_col=name_col,
            enrollment_col=enrollment_col
        )
        
        # Store file in a temporary location or keep in memory if possible?
        # For now, we return the parsed result. 
        # The frontend will send the batch_id back to commit.
        # To make this work without complex caching, we'll store the parse result 
        # in a temporary JSON file in algo/cache/temp_uploads/
        
        temp_dir = os.path.join('algo', 'cache', 'temp_uploads', str(request.user_id))
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_file = os.path.join(temp_dir, f"{parse_result.batch_id}.json")
        parser.to_json_file(temp_file, parse_result)
        
        return jsonify({
            "success": True,
            "batch_id": parse_result.batch_id,
            "rows_extracted": parse_result.rows_extracted,
            "sample": parse_result.data.get(batch_name, [])[:10],
            "warnings": [w.get('message', str(w)) for w in parse_result.warnings]
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500

@student_bp.route('/commit-upload', methods=['POST'])
@token_required
def commit_upload():
    """
    Step 2: Persist parsed data to DB
    """
    try:
        data = request.get_json()
        batch_id = data.get('batch_id')
        session_id = data.get('session_id')
        
        if not batch_id:
            return jsonify({"error": "batch_id required"}), 400
            
        # Verify session ownership if session_id is provided
        if session_id and int(session_id) > 0:
            from algo.database.db import get_db_connection
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM allocation_sessions WHERE session_id = ?", (session_id,))
            owner = cur.fetchone()
            conn.close()
            if not owner or owner[0] != request.user_id:
                return jsonify({"error": "Unauthorized session"}), 403
            
        # Load from temp cache
        temp_file = os.path.join('algo', 'cache', 'temp_uploads', str(request.user_id), f"{batch_id}.json")
        if not os.path.exists(temp_file):
            return jsonify({"error": "Upload session expired or not found"}), 404
            
        with open(temp_file, 'r') as f:
            import json
            parse_data = json.load(f)
            
        # Insert into DB via service (but service wants file_obj...)
        # Actually, let's use StudentQueries directly for the pre-parsed data
        from algo.database.queries.student_queries import StudentQueries
        
        batch_name = parse_data['batch_name']
        batch_color = parse_data.get('batch_color', '#3b82f6')
        filename = parse_data.get('source_filename', 'uploaded_file')
        
        # 1. Create upload record
        upload_id = StudentQueries.create_upload(
            session_id, 
            batch_id, 
            batch_name, 
            filename, 
            0, # size not crucial here
            batch_color
        )
        
        # 2. Bulk insert students
        students_raw = parse_data['data'].get(batch_name, [])
        students_to_insert = []
        for s in students_raw:
            students_to_insert.append((
                upload_id,
                batch_id,
                batch_name,
                s['enrollmentNo'],
                s.get('name', ''),
                batch_color,
                s.get('department', '')
            ))
            
        StudentQueries.bulk_insert_students(students_to_insert)
        
        # Cleanup temp file
        try:
            os.remove(temp_file)
        except: pass
        
        return jsonify({
            "success": True,
            "upload_id": upload_id,
            "inserted": len(students_to_insert)
        })
        
    except Exception as e:
        logger.error(f"Commit error: {e}")
        return jsonify({"error": str(e)}), 500
