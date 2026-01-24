# api/blueprints/sessions.py - COMPLETE VERSION (All Endpoints)
"""
Session management endpoints for allocation workflow.
Handles session lifecycle: create, read, update, delete, and allocation operations.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import random
import string
from algo.auth_service import token_required

# Service layer imports (Phase 1 migration)
from algo.services import SessionService, AllocationService
from algo.core.cache.cache_manager import CacheManager

CACHE_MGR = CacheManager()

session_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')

# ============================================================================
# HELPERS
# ============================================================================

def _get_conn():
    """Get database connection"""
    from algo.database.db import get_db_connection
    return get_db_connection()


# ✅ Raise error instead of fallback
def _get_user_id():
    """Get user_id from request context. Raises if not authenticated."""
    if hasattr(request, 'user_id') and request.user_id:
        return request.user_id
    
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            from algo.auth_service import verify_token
            payload = verify_token(token)
            if payload and payload.get('user_id'):
                return payload['user_id']
        except Exception:
            pass
    
    # ✅ Raise error instead of returning fallback
    raise ValueError("Authentication required")


def _get_session_stats(session_id):
    """Get allocation statistics for a session"""
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    try:
        # Overall stats
        cur.execute("""
            SELECT total_students, allocated_count, status, plan_id
            FROM allocation_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        session_row = cur.fetchone()
        if not session_row:
            return None
        
        session_data = dict(session_row)
        
        # Per-room stats
        cur.execute("""
            SELECT
                c.name,
                c.rows * c.cols as capacity,
                COUNT(a.id) as allocated
            FROM classrooms c
            LEFT JOIN allocations a ON c.id = a.classroom_id AND a.session_id = ?
            WHERE c.id IN (SELECT DISTINCT classroom_id FROM allocations WHERE session_id = ?)
            GROUP BY c.id
        """, (session_id, session_id))
        
        room_stats = [dict(row) for row in cur.fetchall()]
        
        # Per-batch stats
        cur.execute("""
            SELECT batch_name, COUNT(*) as count
            FROM allocations
            WHERE session_id = ?
            GROUP BY batch_name
        """, (session_id,))
        
        batch_stats = [dict(row) for row in cur.fetchall()]
        
        # Completion rate
        completion_rate = 0
        total = session_data.get('total_students') or 0
        allocated = session_data.get('allocated_count') or 0
        if total > 0:
            completion_rate = round((allocated / total) * 100, 2)
        
        return {
            "session_id": session_id,
            "plan_id": session_data.get('plan_id'),
            "status": session_data.get('status'),
            "total_students": total,
            "allocated_count": allocated,
            "pending_count": max(0, total - allocated),
            "rooms": room_stats,
            "batches": batch_stats,
            "completion_rate": completion_rate
        }
        
    except Exception as e:
        print(f"❌ Error getting session stats: {e}")
        return None
    finally:
        conn.close()


def _get_allocated_rooms(cursor, session_id):
    """Get list of allocated rooms for a session"""
    cursor.execute("""
        SELECT 
            a.classroom_id,
            c.name as classroom_name,
            COUNT(a.id) as count
        FROM allocations a
        LEFT JOIN classrooms c ON a.classroom_id = c.id
        WHERE a.session_id = ?
        GROUP BY a.classroom_id, c.name
        ORDER BY c.name
    """, (session_id,))
    
    return [
        {
            'classroom_id': row[0],
            'classroom_name': row[1] or 'Unknown',
            'count': row[2] or 0
        }
        for row in cursor.fetchall()
    ]


# ============================================================================
# CALLABLE FUNCTIONS (for imports from other modules)
# ============================================================================

def createSession(user_id=None, plan_id=None, upload_ids=None):
    """
    Create a new session programmatically.
    
    Usage:
        from api.blueprints.sessions import createSession
        result = createSession(user_id=1, upload_ids=[1, 2, 3])
    
    Returns:
        dict with success, session_id, plan_id, total_students, etc.
    """
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        user_id = user_id or 1
        upload_ids = upload_ids or []
        
        # Generate plan_id if not provided
        if not plan_id:
            plan_id = f"PLAN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        
        # Calculate total students from uploads
        total_students = 0
        if upload_ids:
            placeholders = ','.join('?' * len(upload_ids))
            cursor.execute(f"""
                SELECT COUNT(*) FROM students 
                WHERE upload_id IN ({placeholders})
            """, upload_ids)
            total_students = cursor.fetchone()[0] or 0
        
        # Create session
        cursor.execute("""
            INSERT INTO allocation_sessions 
            (user_id, plan_id, total_students, allocated_count, status, created_at, last_activity)
            VALUES (?, ?, ?, 0, 'active', ?, ?)
        """, (user_id, plan_id, total_students, datetime.now().isoformat(), datetime.now().isoformat()))
        
        session_id = cursor.lastrowid
        
        # Link uploads to session
        for upload_id in upload_ids:
            cursor.execute("UPDATE uploads SET session_id = ? WHERE id = ?", (session_id, upload_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ createSession: Created session {session_id} with {total_students} students")
        
        return {
            'success': True,
            'session_id': session_id,
            'plan_id': plan_id,
            'total_students': total_students,
            'allocated_count': 0,
            'pending_count': total_students,
            'status': 'active'
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def deleteSession(session_id, user_id=None, hard_delete=True):
    """
    Delete a session programmatically.
    
    Args:
        session_id: ID of session to delete
        user_id: Optional user ID for ownership check
        hard_delete: If True, permanently delete. If False, just expire.
    
    Usage:
        from api.blueprints.sessions import deleteSession
        result = deleteSession(session_id=5)
    
    Returns:
        dict with success and message
    """
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        # Check session exists
        cursor.execute("SELECT user_id, status FROM allocation_sessions WHERE session_id = ?", (session_id,))
        session = cursor.fetchone()
        
        if not session:
            conn.close()
            return {'success': False, 'error': 'Session not found'}
        
        if hard_delete:
            # Delete in order (respect foreign keys)
            
            # 1. Delete allocations
            cursor.execute("DELETE FROM allocations WHERE session_id = ?", (session_id,))
            
            # 2. Delete allocation history (if table exists)
            try:
                cursor.execute("DELETE FROM allocation_history WHERE session_id = ?", (session_id,))
            except sqlite3.OperationalError:
                pass  # Table might not exist
            
            # 3. Delete students via uploads
            cursor.execute("""
                DELETE FROM students WHERE upload_id IN (
                    SELECT id FROM uploads WHERE session_id = ?
                )
            """, (session_id,))
            
            # 4. Delete uploads
            cursor.execute("DELETE FROM uploads WHERE session_id = ?", (session_id,))
            
            # 5. Delete session
            cursor.execute("DELETE FROM allocation_sessions WHERE session_id = ?", (session_id,))
            
            message = f'Session {session_id} permanently deleted'
        else:
            # Soft delete - just expire
            cursor.execute("""
                UPDATE allocation_sessions SET status = 'expired', last_activity = ?
                WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))
            
            message = f'Session {session_id} expired'
        
        conn.commit()
        conn.close()
        
        print(f"🗑️ deleteSession: {message}")
        
        return {'success': True, 'message': message}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def getActiveSession(user_id=None):
    """
    Get active session programmatically.
    
    Usage:
        from api.blueprints.sessions import getActiveSession
        session = getActiveSession(user_id=1)
    """
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        user_id = user_id or 1
        
        cursor.execute("""
            SELECT session_id, plan_id, total_students, allocated_count,
                   status, created_at, last_activity, user_id
            FROM allocation_sessions 
            WHERE status = 'active'
            ORDER BY CASE WHEN user_id = ? THEN 0 ELSE 1 END, last_activity DESC 
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        session_id = row[0]
        allocated_rooms = _get_allocated_rooms(cursor, session_id)
        
        conn.close()
        
        total = row[2] or 0
        allocated = row[3] or 0
        
        return {
            'session_id': row[0],
            'plan_id': row[1],
            'total_students': total,
            'allocated_count': allocated,
            'pending_count': max(0, total - allocated),
            'status': row[4],
            'created_at': row[5],
            'last_activity': row[6],
            'user_id': row[7],
            'allocated_rooms': allocated_rooms
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# ROUTE: GET /api/sessions/active
# ============================================================================
@session_bp.route('/active', methods=['GET'])
@token_required
def get_active_session():
    """Get the current active session"""
    try:
        user_id = _get_user_id()
        session_data = SessionService.get_active_session(user_id)
        
        if not session_data:
            return jsonify({
                'success': True,
                'message': 'No active session',
                'session_data': None
            }), 200
        
        print(f"✅ Active session {session_data['session_id']}: {session_data['allocated_count']}/{session_data['total_students']}")
        
        return jsonify({
            'success': True,
            'session_data': session_data
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'session_data': None
        }), 500


# ============================================================================
# ROUTE: GET /api/sessions/<id>
# ============================================================================
@session_bp.route('/<int:session_id>', methods=['GET'])
@token_required
def get_session(session_id):
    """Get specific session details"""
    try:
        session_dict = SessionService.get_session_with_rooms(session_id)
        
        if not session_dict:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        return jsonify({"success": True, "data": session_dict}), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: POST /api/sessions/start
# ============================================================================
@session_bp.route('/start', methods=['POST'])
@token_required
def start_session():
    """
    Smart session management (uses SessionService):
    - If active session exists and recent → add uploads to it
    - If active session is abandoned (>30min) or empty → expire it, create new
    - If no active session → create new
    """
    try:
        data = request.get_json() or {}
        upload_ids = data.get('upload_ids', [])
        force_new = data.get('force_new', False)
        
        print(f"📥 /start called: upload_ids={upload_ids}, force_new={force_new}")
        
        if not upload_ids:
            return jsonify({'success': False, 'error': 'No upload IDs provided'}), 400
        
        user_id = _get_user_id()
        
        result = SessionService.start_or_resume_session(
            user_id=user_id,
            upload_ids=upload_ids,
            force_new=force_new
        )
        
        if result.get('success'):
            action = "Added to existing" if result.get('added_to_existing') else "Created new"
            print(f"✅ {action} session: {result['session']['session_id']}")
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ROUTE: DELETE /api/sessions/<id>
# ============================================================================
@session_bp.route('/<int:session_id>', methods=['DELETE'])
@token_required
def delete_session_by_id(session_id):
    """Delete session by ID - DELETE /api/sessions/<id>"""
    result = deleteSession(session_id, hard_delete=True)
    status = 200 if result['success'] else (404 if 'not found' in result.get('error', '').lower() else 500)
    return jsonify(result), status


# ============================================================================
# ROUTE: DELETE /api/sessions/<id>/delete (alternate path)
# ============================================================================
@session_bp.route('/<int:session_id>/delete', methods=['DELETE', 'POST'])
@token_required
def delete_session_explicit(session_id):
    """Delete session - DELETE/POST /api/sessions/<id>/delete"""
    result = deleteSession(session_id, hard_delete=True)
    status = 200 if result['success'] else (404 if 'not found' in result.get('error', '').lower() else 500)
    return jsonify(result), status


# ============================================================================
# ROUTE: POST /api/sessions/<id>/expire (soft delete)
# ============================================================================
@session_bp.route('/<int:session_id>/expire', methods=['POST'])
@token_required
def expire_session(session_id):
    """Soft delete - just mark as expired (uses SessionService)"""
    result = SessionService.delete_session(session_id, hard_delete=False)
    status = 200 if result['success'] else (404 if 'not found' in result.get('error', '').lower() else 500)
    return jsonify(result), status


# ============================================================================
# ROUTE: GET /api/sessions/<id>/uploads
# ============================================================================
@session_bp.route('/<int:session_id>/uploads', methods=['GET'])
@token_required
def get_session_uploads(session_id):
    """Get all uploads/batches for a session (uses SessionService)"""
    try:
        result = SessionService.get_session_uploads(session_id)
        status = 200 if result.get('success') else 500
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: GET /api/sessions/<id>/stats
# ============================================================================
@session_bp.route('/<int:session_id>/stats', methods=['GET'])
@token_required
def get_session_statistics(session_id):
    """Get allocation statistics for a session (uses SessionService)"""
    try:
        result = SessionService.get_session_statistics(session_id)
        
        if not result.get('success'):
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: GET /api/sessions/<id>/pending
# ============================================================================
@session_bp.route('/<int:session_id>/pending', methods=['GET'])
@token_required
def get_session_pending(session_id):
    """Get unallocated students for a session"""
    try:
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT s.id, s.enrollment, s.name, s.batch_name, s.batch_id, s.batch_color
            FROM students s
            JOIN uploads u ON s.upload_id = u.id
            WHERE u.session_id = ?
            AND s.id NOT IN (
                SELECT student_id FROM allocations WHERE session_id = ?
            )
            ORDER BY s.batch_name, s.enrollment
        """, (session_id, session_id))
        
        pending = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return jsonify({
            "success": True,
            "pending": pending,
            "count": len(pending)
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: POST /api/sessions/<id>/refresh-totals
# ============================================================================
@session_bp.route('/<int:session_id>/refresh-totals', methods=['POST'])
@token_required
def refresh_session_totals(session_id):
    """Recalculate total_students and allocated_count (uses SessionService)"""
    result = SessionService.update_stats(session_id)
    status = 200 if result['success'] else 500
    return jsonify(result), status


# ============================================================================
# ROUTE: POST /api/sessions/force-new
# ============================================================================
@session_bp.route('/force-new', methods=['POST'])
@token_required
def force_new_session():
    """Force-expire ALL active sessions"""
    try:
        result = SessionService.expire_all_active()
        
        print(f"⚠️ Force-expired {result.get('expired_count', 0)} active session(s)")
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ROUTE: POST /api/sessions/claim-orphaned
# ============================================================================
@session_bp.route('/claim-orphaned', methods=['POST'])
@token_required
def claim_orphaned_sessions():
    """Claim sessions with user_id=1 (orphaned) for current user"""
    user_id = _get_user_id()
    
    try:
        result = SessionService.claim_orphaned_sessions(user_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        if result.get('claimed', 0) > 0:
            print(f"📝 User {user_id} claimed {result['claimed']} orphaned session(s)")
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: POST /api/sessions/<id>/heartbeat
# ============================================================================
@session_bp.route('/<int:session_id>/heartbeat', methods=['POST'])
@token_required
def heartbeat(session_id):
    """Update session activity timestamp"""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE allocation_sessions SET last_activity = ? WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        
        updated = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({"success": updated > 0}), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: POST /api/sessions/<id>/finalize
# ============================================================================
@session_bp.route('/<int:session_id>/finalize', methods=['POST'])
@token_required
def finalize_session(session_id):
    """Mark session as completed"""
    try:
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT plan_id, status, total_students, allocated_count
            FROM allocation_sessions WHERE session_id = ?
        """, (session_id,))
        
        session = cur.fetchone()
        
        if not session:
            conn.close()
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        if session['status'] != 'active':
            conn.close()
            return jsonify({"success": False, "error": f"Session is already {session['status']}"}), 400
        
        # Get allocated rooms
        cur.execute("""
            SELECT DISTINCT c.name
            FROM allocations a
            JOIN classrooms c ON a.classroom_id = c.id
            WHERE a.session_id = ?
        """, (session_id,))
        
        allocated_rooms = [row['name'] for row in cur.fetchall()]
        
        # Update status
        cur.execute("""
            UPDATE allocation_sessions
            SET status = 'completed', last_activity = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
        
        # ✅ FIX: Finalize rooms in Cache (Prune experimental rooms and mark as FINALIZED)
        plan_id = session['plan_id']
        if plan_id:
            try:
                success = CACHE_MGR.finalize_rooms(plan_id, allocated_rooms)
                if success:
                    print(f"✅ Cache finalized for plan: {plan_id}")
                else:
                    print(f"⚠️ Cache finalization returned False for plan: {plan_id}")
            except Exception as cache_err:
                print(f"❌ Cache finalization error: {cache_err}")

        print(f"🏁 Finalized session {session_id} ({session['plan_id']})")
        
        return jsonify({
            "success": True,
            "message": "Session finalized successfully",
            "plan_id": session['plan_id'],
            "rooms": allocated_rooms,
            "total_allocated": session['allocated_count']
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: POST /api/sessions/<id>/allocate-room
# ============================================================================
@session_bp.route('/<int:session_id>/allocate-room', methods=['POST'])
@token_required
def allocate_room_in_session(session_id):
    """Save allocation for ONE room (uses AllocationService)"""
    try:
        data = request.get_json() or {}
        classroom_id = data.get('classroom_id')
        seating_data = data.get('seating_data')
        selected_batch_names = data.get('selected_batch_names', [])
        
        if classroom_id is None or seating_data is None:
            return jsonify({"success": False, "error": "Missing classroom_id or seating_data"}), 400
        
        result = AllocationService.save_room_allocation(
            session_id=session_id,
            classroom_id=classroom_id,
            seating_data=seating_data,
            selected_batch_names=selected_batch_names
        )
        
        if result.get('success'):
            print(f"✅ Allocated {result.get('allocated_count', 0)} students")
            return jsonify(result), 200
        else:
            status = 404 if 'not found' in result.get('error', '').lower() else 400
            return jsonify(result), status
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: POST /api/sessions/<id>/undo
# ============================================================================
@session_bp.route('/<int:session_id>/undo', methods=['POST'])
@token_required
def undo_last_action(session_id):
    """Undo last room allocation (uses AllocationService)"""
    try:
        result = AllocationService.undo_last_allocation(session_id)
        
        if result.get('success'):
            print(f"↩️ Undid allocation: {result.get('message')}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: GET /api/sessions/list (get all sessions)
# ============================================================================
@session_bp.route('/list', methods=['GET'])
@token_required
def list_sessions():
    """Get all sessions for current user (uses SessionService)"""
    try:
        user_id = _get_user_id()
        status_filter = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        
        result = SessionService.list_sessions(user_id, status_filter, limit)
        status = 200 if result.get('success') else 500
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: POST /api/sessions/create (explicit create endpoint)
# ============================================================================
@session_bp.route('/create', methods=['POST'])
@token_required
def create_session_route():
    """Explicit session creation endpoint"""
    try:
        data = request.get_json() or {}
        upload_ids = data.get('upload_ids', [])
        plan_id = data.get('plan_id')
        
        if not upload_ids:
            return jsonify({'success': False, 'error': 'No upload IDs provided'}), 400
        
        user_id = _get_user_id()
        
        result = createSession(user_id=user_id, plan_id=plan_id, upload_ids=upload_ids)
        
        if result['success']:
            return jsonify({
                'success': True,
                'session': {
                    'session_id': result['session_id'],
                    'plan_id': result['plan_id'],
                    'total_students': result['total_students'],
                    'allocated_count': 0,
                    'pending_count': result['total_students'],
                    'status': 'active'
                }
            }), 201
        else:
            return jsonify(result), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# END OF FILE
# ============================================================================
print("✅ Sessions blueprint loaded with all endpoints")