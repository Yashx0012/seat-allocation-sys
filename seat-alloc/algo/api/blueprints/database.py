# api/blueprints/database.py
"""
Database management endpoints.
Provides alternative paths for session operations used by Database Manager UI.
"""

from flask import Blueprint, jsonify, request
from algo.api.blueprints.sessions import deleteSession, getActiveSession, _get_conn
import sqlite3

database_bp = Blueprint('database', __name__, url_prefix='/api/database')

# ============================================================================
# DELETE /api/database/session/<id>/delete
# ============================================================================
@database_bp.route('/session/<int:session_id>/delete', methods=['DELETE', 'POST'])
def delete_session_via_database(session_id):
    """Delete session via database manager path"""
    result = deleteSession(session_id, hard_delete=True)
    status = 200 if result['success'] else (404 if 'not found' in result.get('error', '').lower() else 500)
    return jsonify(result), status


# ============================================================================
# GET /api/database/sessions
# ============================================================================
@database_bp.route('/sessions', methods=['GET'])
def list_all_sessions():
    """List all sessions for database manager"""
    try:
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT session_id, plan_id, user_id, total_students, allocated_count, 
                   status, created_at, last_activity
            FROM allocation_sessions
            ORDER BY created_at DESC
        """)
        
        sessions = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return jsonify({"success": True, "sessions": sessions}), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# DELETE /api/database/sessions/clear-all
# ============================================================================
@database_bp.route('/sessions/clear-all', methods=['DELETE', 'POST'])
def clear_all_sessions():
    """Clear all sessions (DANGER)"""
    if not request.args.get('confirm') == 'yes':
        return jsonify({"success": False, "error": "Add ?confirm=yes to confirm"}), 400
    
    try:
        conn = _get_conn()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM allocations")
        cur.execute("DELETE FROM allocation_history")
        cur.execute("DELETE FROM students")
        cur.execute("DELETE FROM uploads")
        cur.execute("DELETE FROM allocation_sessions")
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "All sessions cleared"}), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


print("✅ Database blueprint loaded")