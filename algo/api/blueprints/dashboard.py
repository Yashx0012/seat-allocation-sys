# Dashboard data endpoints.
# Provides statistics, recent activity overview, and active session information for the management UI.
from flask import Blueprint, jsonify, request
from algo.database.db import get_db_connection
from algo.auth_service import token_required
import sqlite3
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

def _get_user_id():
    """Get user_id from request context"""
    if hasattr(request, 'user_id') and request.user_id:
        return request.user_id
    return 1

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_stats():
    """Get dashboard statistics - MATCHES FRONTEND EXPECTED FORMAT"""
    user_id = _get_user_id()
    
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Total classrooms
        cur.execute("SELECT COUNT(*) as count FROM classrooms")
        total_classrooms = cur.fetchone()['count']
        
        # Total students (across all uploads)
        cur.execute("SELECT COUNT(*) as count FROM students")
        total_students = cur.fetchone()['count']
        
        # Allocated seats (from allocations table)
        cur.execute("""
            SELECT COUNT(*) as count FROM allocations a
            JOIN allocation_sessions s ON a.session_id = s.session_id
            WHERE s.user_id = ? OR s.user_id = 1 OR s.user_id IS NULL
        """, (user_id,))
        allocated_seats = cur.fetchone()['count']
        
        # Completed plans
        cur.execute("""
            SELECT COUNT(*) as count FROM allocation_sessions 
            WHERE status = 'completed' AND (user_id = ? OR user_id = 1 OR user_id IS NULL)
        """, (user_id,))
        completed_plans = cur.fetchone()['count']
        
        # Calculate changes (compare to 7 days ago - simplified)
        # For now, return 0 as we don't track historical data
        
        conn.close()
        
        return jsonify({
            "success": True,  # Frontend expects "success", not "status"
            "stats": {
                "total_students": total_students,
                "total_classrooms": total_classrooms,
                "allocated_seats": allocated_seats,
                "completed_plans": completed_plans,
                # Change percentages (placeholder - would need historical tracking)
                "students_change": 0,
                "classrooms_change": 0,
                "allocation_change": 0,
                "plans_change": 0
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@dashboard_bp.route('/activity', methods=['GET'])
@token_required
def get_activity():
    """Get recent activity log - RETURNS ACTUAL DATA"""
    user_id = _get_user_id()
    limit = request.args.get('limit', 10, type=int)
    
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        activities = []
        
        # Get recent session activities
        cur.execute("""
            SELECT 
                session_id,
                plan_id,
                status,
                total_students,
                allocated_count,
                created_at,
                last_activity
            FROM allocation_sessions 
            WHERE user_id = ? OR user_id = 1 OR user_id IS NULL
            ORDER BY COALESCE(last_activity, created_at) DESC
            LIMIT ?
        """, (user_id, limit))
        
        for row in cur.fetchall():
            row_dict = dict(row)
            
            # Format timestamp
            timestamp = row_dict.get('last_activity') or row_dict.get('created_at')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%I:%M %p')
                except:
                    time_str = 'Recently'
            else:
                time_str = 'Unknown'
            
            # Determine activity type and message
            status = row_dict.get('status', 'unknown')
            allocated = row_dict.get('allocated_count', 0)
            total = row_dict.get('total_students', 0)
            plan_id = row_dict.get('plan_id', 'Unknown')
            
            if status == 'completed':
                activity_type = 'success'
                message = f"Plan '{plan_id}' completed - {allocated} students allocated"
            elif status == 'active' and allocated > 0:
                activity_type = 'process'
                message = f"Plan '{plan_id}' in progress - {allocated}/{total} allocated"
            elif status == 'active':
                activity_type = 'info'
                message = f"Plan '{plan_id}' started with {total} students"
            else:
                activity_type = 'info'
                message = f"Plan '{plan_id}' - {status}"
            
            activities.append({
                "id": f"session_{row_dict.get('session_id')}",
                "time": time_str,
                "message": message,
                "type": activity_type
            })
        
        # If no activities, add a placeholder
        if not activities:
            activities.append({
                "id": "empty_1",
                "time": "Now",
                "message": "No recent activity. Start by uploading student data.",
                "type": "info"
            })
        
        conn.close()
        
        return jsonify({
            "success": True,
            "activities": activities
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e), "activities": []}), 500


@dashboard_bp.route('/session-info', methods=['GET'])
@token_required
def get_session_info():
    """Get current session and upcoming exam info"""
    user_id = _get_user_id()
    
    try:
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
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Check for active allocation (indicates upcoming exam)
        cur.execute("""
            SELECT plan_id, created_at, total_students, allocated_count
            FROM allocation_sessions 
            WHERE status = 'active' AND (user_id = ? OR user_id = 1 OR user_id IS NULL)
            ORDER BY last_activity DESC 
            LIMIT 1
        """, (user_id,))
        row = cur.fetchone()
        
        if row:
            row_dict = dict(row)
            # Estimate exam is 3 days from now
            exam_date = now + timedelta(days=3)
            next_exam = {
                "name": row_dict.get('plan_id') or "Upcoming Exam",
                "date": exam_date.strftime("%b %d"),
                "days_remaining": 3
            }
        
        conn.close()
        
        return jsonify({
            "success": True,
            "current_session": current_session,
            "next_exam": next_exam
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500