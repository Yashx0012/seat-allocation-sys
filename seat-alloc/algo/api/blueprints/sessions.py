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
from algo.services.auth_service import token_required

# Service layer imports (Phase 1 migration)
from algo.services import SessionService, AllocationService
from algo.core.cache.cache_manager import CacheManager
from algo.database.queries.allocation_queries import AllocationQueries

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
            from algo.services.auth_service import verify_token
            payload = verify_token(token)
            if payload and payload.get('user_id'):
                return payload['user_id']
        except Exception:
            pass
    
    # ✅ Raise error instead of returning fallback
    raise ValueError("Authentication required")


def _verify_session_owner(session_id: int, user_id: int) -> bool:
    """
    Verify that the user owns the specified session.
    STRICT: Only allows access if user_id matches. No ADMIN bypass.
    
    Args:
        session_id: The session ID to check
        user_id: The user ID to verify against
        
    Returns:
        True if access is allowed, False otherwise
    """
    from algo.database.queries.session_queries import SessionQueries
    
    session = SessionQueries.get_session_by_id(session_id)
    if not session:
        return False
    
    owner_id = session.get('user_id')
    
    # Allow if user owns the session
    if owner_id == user_id:
        return True
    
    # Allow if session is unassigned (NULL user_id) - legacy data
    if owner_id is None:
        return True
    
    return False


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
        from algo.database.queries.session_queries import SessionQueries
        from algo.database.db import get_db
        
        if not user_id:
            return {'success': False, 'error': 'user_id is required'}
        upload_ids = upload_ids or []
        
        # Generate plan_id if not provided
        if not plan_id:
            plan_id = f"PLAN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        
        # Create session via query layer (single source of truth for INSERT)
        session_id = SessionQueries.create_session(plan_id, user_id)
        
        # Link uploads and count students
        db = get_db()
        total_students = 0
        if upload_ids:
            for upload_id in upload_ids:
                db.execute("UPDATE uploads SET session_id = ? WHERE id = ?", (session_id, upload_id))
            
            placeholders = ','.join('?' * len(upload_ids))
            cursor = db.execute(f"SELECT COUNT(*) FROM students WHERE upload_id IN ({placeholders})", upload_ids)
            total_students = cursor.fetchone()[0] or 0
            
            SessionQueries.update_session_stats(session_id, total_students, 0)
        
        db.commit()
        
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
    Delegates to SessionService.delete_session() — single source of truth for cascade logic.
    
    Args:
        session_id: ID of session to delete
        user_id: Optional user ID for ownership check (not enforced here)
        hard_delete: If True, permanently delete. If False, just expire.
    
    Usage:
        from api.blueprints.sessions import deleteSession
        result = deleteSession(session_id=5)
    
    Returns:
        dict with success and message
    """
    result = SessionService.delete_session(session_id, hard_delete=hard_delete)
    if result.get('success'):
        print(f"🗑️ deleteSession: {result.get('message')}")
    return result


def getActiveSession(user_id=None):
    """
    Get active session programmatically.
    Delegates to SessionService.get_active_session().
    
    Usage:
        from api.blueprints.sessions import getActiveSession
        session = getActiveSession(user_id=1)
    """
    if not user_id:
        return None
    return SessionService.get_active_session(user_id)


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
        user_id = _get_user_id()
        if not _verify_session_owner(session_id, user_id):
            return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
        
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
    user_id = _get_user_id()
    if not _verify_session_owner(session_id, user_id):
        return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
    
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
    user_id = _get_user_id()
    if not _verify_session_owner(session_id, user_id):
        return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
    
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
    user_id = _get_user_id()
    if not _verify_session_owner(session_id, user_id):
        return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
    
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
        user_id = _get_user_id()
        if not _verify_session_owner(session_id, user_id):
            return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
        
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
        user_id = _get_user_id()
        if not _verify_session_owner(session_id, user_id):
            return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
        
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
        user_id = _get_user_id()
        if not _verify_session_owner(session_id, user_id):
            return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
        
        from algo.database.queries.student_queries import StudentQueries
        pending = StudentQueries.get_pending_students(session_id)
        
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
    user_id = _get_user_id()
    if not _verify_session_owner(session_id, user_id):
        return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
    
    result = SessionService.update_stats(session_id)
    status = 200 if result['success'] else 500
    return jsonify(result), status


# ============================================================================
# ROUTE: POST /api/sessions/force-new
# ============================================================================
@session_bp.route('/force-new', methods=['POST'])
@token_required
def force_new_session():
    """Force-expire current user's active sessions only"""
    try:
        user_id = _get_user_id()
        result = SessionService.expire_all_active(user_id=user_id)
        
        print(f"⚠️ Force-expired {result.get('expired_count', 0)} active session(s) for user {user_id}")
        
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
        user_id = _get_user_id()
        if not _verify_session_owner(session_id, user_id):
            return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
        
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
        user_id = _get_user_id()
        if not _verify_session_owner(session_id, user_id):
            return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
        
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
        user_id = _get_user_id()
        if not _verify_session_owner(session_id, user_id):
            return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
        
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
        user_id = _get_user_id()
        if not _verify_session_owner(session_id, user_id):
            return jsonify({"success": False, "error": "Access denied - you do not own this session"}), 403
        
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