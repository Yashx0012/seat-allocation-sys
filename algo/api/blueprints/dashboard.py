# Dashboard data endpoints.
# Provides statistics, recent activity overview, and active session information for the management UI.
from flask import Blueprint, jsonify, request
from algo.database.db import get_db_connection
from algo.auth_service import token_required
import sqlite3

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM classrooms")
        classrooms = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM students")
        students = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM allocation_sessions WHERE status='active' AND user_id = ?", (request.user_id,))
        active_sessions = cur.fetchone()[0]
        
        conn.close()
        return jsonify({
            "status": "success",
            "stats": {
                "classrooms": classrooms,
                "students": students,
                "active_sessions": active_sessions
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@dashboard_bp.route('/activity', methods=['GET'])
@token_required
def get_activity():
    # Placeholder for activity log
    # In a real app this would query the allocation_history or user_activity table
    return jsonify({"status": "success", "data": []})

@dashboard_bp.route('/session-info', methods=['GET'])
@token_required
def get_session_info():
    """
    Get current session and upcoming exam info - LEGACY COMPATIBLE.
    Always returns success key system status.
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate current semester
        now = datetime.now()
        month = now.month
        year = now.year
        
        if month >= 1 and month <= 5:
            current_session = f"Spring Semester {year}"
        elif month >= 6 and month <= 7:
            current_session = f"Summer Session {year}"
        else:
            current_session = f"Fall Semester {year}"
        
        next_exam = None
        total_students = 0
        allocated_students = 0
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Check for active allocation (indicates upcoming exam) for THIS user
        cur.execute("""
            SELECT plan_id, created_at, total_students, allocated_count
            FROM allocation_sessions 
            WHERE status = 'active' AND user_id = ?
            ORDER BY last_activity DESC 
            LIMIT 1
        """, (request.user_id,))
        row = cur.fetchone()
        
        if row:
            # Estimate exam is 3 days from now
            exam_date = now + timedelta(days=3)
            next_exam = {
                "name": row['plan_id'] or "Upcoming Exam",
                "date": exam_date.strftime("%b %d"),
                "days_remaining": 3
            }
        
        # Get total student count
        cur.execute("SELECT COUNT(*) FROM students")
        total_students = cur.fetchone()[0] or 0
        
        # Get allocated students count (from all active/completed sessions) for THIS user
        cur.execute("""
            SELECT COUNT(DISTINCT a.student_id) FROM allocations a
            JOIN allocation_sessions s ON a.session_id = s.session_id
            WHERE s.status IN ('active', 'completed') AND s.user_id = ?
        """, (request.user_id,))
        allocated_students = cur.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            "success": True,
            "current_session": current_session,
            "next_exam": next_exam,
            "system_status": {
                "total_students": total_students,
                "allocated_students": allocated_students,
                "pending_students": max(0, total_students - allocated_students),
                "health": "healthy" if total_students > 0 else "empty"
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
