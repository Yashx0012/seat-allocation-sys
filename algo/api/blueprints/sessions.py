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
        session_data = getActiveSession(user_id)
        
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
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM allocation_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        session_dict = dict(row)
        
        # Get allocated rooms
        allocated_rooms = _get_allocated_rooms(cursor, session_id)
        session_dict['allocated_rooms'] = allocated_rooms
        
        conn.close()
        
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
    Smart session management:
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
        conn = _get_conn()
        cursor = conn.cursor()
        
        # Check for existing active session
        cursor.execute("""
            SELECT session_id, last_activity, allocated_count, total_students, plan_id, user_id
            FROM allocation_sessions 
            WHERE status = 'active'
            ORDER BY CASE WHEN user_id = ? THEN 0 ELSE 1 END, last_activity DESC
            LIMIT 1
        """, (user_id,))
        existing = cursor.fetchone()
        
        if existing and not force_new:
            existing_id, last_activity, allocated, total, plan_id, owner_id = existing
            
            # Check if abandoned (>30 min inactive)
            is_abandoned = False
            if last_activity:
                try:
                    last_active = datetime.fromisoformat(str(last_activity).replace('Z', '+00:00'))
                    inactive_duration = datetime.now() - last_active.replace(tzinfo=None)
                    is_abandoned = inactive_duration > timedelta(minutes=30)
                except Exception as e:
                    print(f"⚠️ Date parse warning: {e}")
            
            is_empty = (total or 0) == 0 and (allocated or 0) == 0
            
            if is_abandoned or is_empty:
                # Expire abandoned/empty session
                reason = "empty" if is_empty else "abandoned"
                print(f"⏰ Auto-expiring {reason} session {existing_id}")
                cursor.execute("""
                    UPDATE allocation_sessions SET status = 'expired' WHERE session_id = ?
                """, (existing_id,))
                # Continue to create new session
            else:
                # Add uploads to existing session
                print(f"📎 Adding {len(upload_ids)} uploads to existing session {existing_id}")
                
                linked_count = 0
                for upload_id in upload_ids:
                    cursor.execute("""
                        UPDATE uploads SET session_id = ?
                        WHERE id = ? AND (session_id IS NULL OR session_id = ?)
                    """, (existing_id, upload_id, existing_id))
                    linked_count += cursor.rowcount
                
                # Recalculate total students
                cursor.execute("""
                    SELECT COUNT(*) FROM students s
                    JOIN uploads u ON s.upload_id = u.id
                    WHERE u.session_id = ?
                """, (existing_id,))
                new_total = cursor.fetchone()[0] or 0
                
                # Get current allocated count
                cursor.execute("SELECT COUNT(*) FROM allocations WHERE session_id = ?", (existing_id,))
                current_allocated = cursor.fetchone()[0] or 0
                
                # Update session
                cursor.execute("""
                    UPDATE allocation_sessions
                    SET total_students = ?, allocated_count = ?, last_activity = ?,
                        user_id = COALESCE(user_id, ?)
                    WHERE session_id = ?
                """, (new_total, current_allocated, datetime.now().isoformat(), user_id, existing_id))
                
                # Get allocated rooms
                allocated_rooms = _get_allocated_rooms(cursor, existing_id)
                
                conn.commit()
                conn.close()
                
                pending_count = max(0, new_total - current_allocated)
                
                print(f"✅ Added to session {existing_id}: total={new_total}, allocated={current_allocated}")
                
                return jsonify({
                    'success': True,
                    'message': f'Added {linked_count} uploads to existing session',
                    'added_to_existing': True,
                    'session': {
                        'session_id': existing_id,
                        'plan_id': plan_id,
                        'total_students': new_total,
                        'allocated_count': current_allocated,
                        'pending_count': pending_count,
                        'allocated_rooms': allocated_rooms
                    }
                }), 200
        
        # Create new session
        conn.close()  # Close before calling createSession (it opens its own connection)
        
        result = createSession(user_id=user_id, upload_ids=upload_ids)
        
        if result['success']:
            return jsonify({
                'success': True,
                'added_to_existing': False,
                'session': {
                    'session_id': result['session_id'],
                    'plan_id': result['plan_id'],
                    'total_students': result['total_students'],
                    'allocated_count': 0,
                    'pending_count': result['total_students'],
                    'allocated_rooms': []
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Failed to create session')}), 500
        
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
    """Soft delete - just mark as expired"""
    result = deleteSession(session_id, hard_delete=False)
    status = 200 if result['success'] else 500
    return jsonify(result), status


# ============================================================================
# ROUTE: GET /api/sessions/<id>/uploads
# ============================================================================
@session_bp.route('/<int:session_id>/uploads', methods=['GET'])
@token_required
def get_session_uploads(session_id):
    """Get all uploads/batches for a session"""
    try:
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                u.id as upload_id,
                u.batch_id,
                u.batch_name,
                u.batch_color,
                u.original_filename,
                u.created_at as uploaded_at,
                COUNT(s.id) as student_count
            FROM uploads u
            LEFT JOIN students s ON u.id = s.upload_id
            WHERE u.session_id = ?
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """, (session_id,))
        
        uploads = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "uploads": uploads,
            "count": len(uploads)
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ROUTE: GET /api/sessions/<id>/stats
# ============================================================================
@session_bp.route('/<int:session_id>/stats', methods=['GET'])
@token_required
def get_session_statistics(session_id):
    """Get allocation statistics for a session"""
    try:
        stats = _get_session_stats(session_id)
        
        if not stats:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        return jsonify({"success": True, "stats": stats}), 200
        
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
    """Recalculate total_students and allocated_count"""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        # Calculate total students from linked uploads
        cursor.execute("""
            SELECT COUNT(*) FROM students s
            JOIN uploads u ON s.upload_id = u.id
            WHERE u.session_id = ?
        """, (session_id,))
        total_students = cursor.fetchone()[0] or 0
        
        # Calculate allocated count
        cursor.execute("SELECT COUNT(*) FROM allocations WHERE session_id = ?", (session_id,))
        allocated_count = cursor.fetchone()[0] or 0
        
        # Update session
        cursor.execute("""
            UPDATE allocation_sessions
            SET total_students = ?, allocated_count = ?, last_activity = ?
            WHERE session_id = ?
        """, (total_students, allocated_count, datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
        
        pending_count = max(0, total_students - allocated_count)
        
        print(f"🔄 Refreshed session {session_id}: total={total_students}, allocated={allocated_count}")
        
        return jsonify({
            'success': True,
            'total_students': total_students,
            'allocated_count': allocated_count,
            'pending_count': pending_count
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ROUTE: POST /api/sessions/force-new
# ============================================================================
@session_bp.route('/force-new', methods=['POST'])
@token_required
def force_new_session():
    """Force-expire ALL active sessions"""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE allocation_sessions SET status = 'expired', last_activity = ?
            WHERE status = 'active'
        """, (datetime.now().isoformat(),))
        
        expired_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"⚠️ Force-expired {expired_count} active session(s)")
        
        return jsonify({
            "success": True,
            "message": f"Expired {expired_count} active sessions",
            "expired_count": expired_count
        }), 200
        
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
    
    if user_id == 1:
        return jsonify({"success": False, "error": "Cannot claim with default user"}), 400
    
    try:
        conn = _get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE allocation_sessions 
            SET user_id = ?
            WHERE user_id = 1 AND status = 'active'
        """, (user_id,))
        
        claimed = cur.rowcount
        conn.commit()
        conn.close()
        
        if claimed > 0:
            print(f"📝 User {user_id} claimed {claimed} orphaned session(s)")
        
        return jsonify({"success": True, "claimed": claimed}), 200
        
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
    """Save allocation for ONE room"""
    try:
        data = request.get_json() or {}
        classroom_id = data.get('classroom_id')
        seating_data = data.get('seating_data')
        room_no = data.get('room_no', '')
        selected_batch_names = data.get('selected_batch_names', [])
        
        if classroom_id is None or seating_data is None:
            return jsonify({"success": False, "error": "Missing classroom_id or seating_data"}), 400
        
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Validate session
        cur.execute("""
            SELECT session_id, plan_id, status, total_students, allocated_count
            FROM allocation_sessions WHERE session_id = ?
        """, (session_id,))
        
        session_row = cur.fetchone()
        
        if not session_row:
            conn.close()
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        if session_row['status'] != 'active':
            conn.close()
            return jsonify({"success": False, "error": f"Session is {session_row['status']}, not active"}), 400
        
        # Get classroom info
        cur.execute("SELECT id, name, rows, cols FROM classrooms WHERE id = ?", (classroom_id,))
        classroom = cur.fetchone()
        if not classroom:
            conn.close()
            return jsonify({"success": False, "error": "Classroom not found"}), 404
        
        # Process seating matrix
        seating_matrix = seating_data.get('seating', [])
        allocated_students = []
        
        for row_idx, row in enumerate(seating_matrix):
            if not isinstance(row, list):
                continue
            for col_idx, seat in enumerate(row):
                if not seat or seat.get('is_broken') or seat.get('is_unallocated'):
                    continue
                
                enrollment = seat.get('roll_number')
                if not enrollment:
                    continue
                
                # Find student
                cur.execute("""
                    SELECT s.id, s.batch_name
                    FROM students s
                    JOIN uploads u ON s.upload_id = u.id
                    WHERE s.enrollment = ?
                    AND u.session_id = ?
                    AND s.id NOT IN (SELECT student_id FROM allocations WHERE session_id = ?)
                """, (enrollment, session_id, session_id))
                
                student_row = cur.fetchone()
                
                if student_row:
                    # Filter by batch if specified
                    if selected_batch_names and student_row['batch_name'] not in selected_batch_names:
                        continue
                    
                    # Insert allocation
                    cur.execute("""
                        INSERT INTO allocations
                        (session_id, classroom_id, student_id, enrollment, seat_position, batch_name, paper_set)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        session_id, 
                        classroom_id, 
                        student_row['id'], 
                        enrollment,
                        f"{row_idx + 1}-{col_idx + 1}", 
                        student_row['batch_name'], 
                        seat.get('paper_set', 'A')
                    ))
                    
                    allocated_students.append(enrollment)
        
        # Update session totals
        cur.execute("""
            UPDATE allocation_sessions
            SET allocated_count = allocated_count + ?, last_activity = ?
            WHERE session_id = ?
        """, (len(allocated_students), datetime.now().isoformat(), session_id))
        
        # Add to history (if table exists)
        try:
            cur.execute("SELECT COALESCE(MAX(step_number), 0) + 1 FROM allocation_history WHERE session_id = ?", (session_id,))
            step_num = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO allocation_history (session_id, step_number, classroom_id, action_type, students_affected, created_at)
                VALUES (?, ?, ?, 'allocate', ?, ?)
            """, (session_id, step_num, classroom_id, len(allocated_students), datetime.now().isoformat()))
        except sqlite3.OperationalError:
            pass  # allocation_history table might not exist
        
        conn.commit()
        
        # Get fresh totals
        cur.execute("""
            SELECT total_students, allocated_count, plan_id 
            FROM allocation_sessions WHERE session_id = ?
        """, (session_id,))
        fresh = cur.fetchone()
        
        # Get all allocated rooms
        allocated_rooms = _get_allocated_rooms(cur, session_id)
        
        conn.close()
        
        fresh_total = fresh['total_students'] or 0
        fresh_allocated = fresh['allocated_count'] or 0
        fresh_pending = max(0, fresh_total - fresh_allocated)
        
        print(f"✅ Allocated {len(allocated_students)} students to {classroom['name']}")
        
        return jsonify({
            "success": True,
            "message": f"Allocated {len(allocated_students)} students to {classroom['name']}",
            "allocated_count": len(allocated_students),
            "remaining_count": fresh_pending,
            "session": {
                "session_id": session_id,
                "plan_id": fresh['plan_id'],
                "total_students": fresh_total,
                "allocated_count": fresh_allocated,
                "pending_count": fresh_pending,
                "allocated_rooms": allocated_rooms
            },
            "can_finalize": fresh_pending == 0
        }), 200
        
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
    """Undo last room allocation"""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        
        # Try to find last allocation from history
        history_id = None
        target_classroom = None
        affected = 0
        
        try:
            cur.execute("""
                SELECT id, classroom_id, students_affected
                FROM allocation_history
                WHERE session_id = ? AND action_type = 'allocate'
                ORDER BY step_number DESC LIMIT 1
            """, (session_id,))
            last_step = cur.fetchone()
            
            if last_step:
                history_id, target_classroom, affected = last_step
        except sqlite3.OperationalError:
            pass  # Table might not exist
        
        # Fallback: find last classroom with allocations
        if not target_classroom:
            cur.execute("""
                SELECT classroom_id, COUNT(*) as cnt
                FROM allocations WHERE session_id = ?
                GROUP BY classroom_id ORDER BY MAX(id) DESC LIMIT 1
            """, (session_id,))
            fallback = cur.fetchone()
            
            if not fallback:
                conn.close()
                return jsonify({"success": False, "message": "Nothing to undo"}), 400
            
            target_classroom, affected = fallback
        
        # Get classroom name for message
        cur.execute("SELECT name FROM classrooms WHERE id = ?", (target_classroom,))
        classroom_row = cur.fetchone()
        classroom_name = classroom_row[0] if classroom_row else f"Room {target_classroom}"
        
        # Delete allocations for that classroom
        cur.execute("""
            DELETE FROM allocations WHERE session_id = ? AND classroom_id = ?
        """, (session_id, target_classroom))
        deleted = cur.rowcount
        
        # Update session count
        cur.execute("""
            UPDATE allocation_sessions
            SET allocated_count = MAX(0, allocated_count - ?), last_activity = ?
            WHERE session_id = ?
        """, (deleted, datetime.now().isoformat(), session_id))
        
        # Remove history record if exists
        if history_id:
            try:
                cur.execute("DELETE FROM allocation_history WHERE id = ?", (history_id,))
            except:
                pass
        
        conn.commit()
        conn.close()
        
        print(f"↩️ Undid allocation for {classroom_name} ({deleted} students)")
        
        return jsonify({
            "success": True,
            "message": f"Undid allocation for {classroom_name} ({deleted} students)",
            "classroom_name": classroom_name,
            "students_restored": deleted
        }), 200
        
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
    """Get all sessions for current user"""
    try:
        user_id = _get_user_id()
        status_filter = request.args.get('status')  # Optional filter
        limit = request.args.get('limit', 50, type=int)
        
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        query = """
            SELECT session_id, plan_id, total_students, allocated_count, status, created_at, last_activity
            FROM allocation_sessions
            WHERE user_id = ? OR user_id = 1 OR user_id IS NULL
        """
        params = [user_id]
        
        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)
        
        query += " ORDER BY last_activity DESC LIMIT ?"
        params.append(limit)
        
        cur.execute(query, params)
        
        sessions = []
        for row in cur.fetchall():
            session_dict = dict(row)
            total = session_dict.get('total_students') or 0
            allocated = session_dict.get('allocated_count') or 0
            session_dict['pending_count'] = max(0, total - allocated)
            sessions.append(session_dict)
        
        conn.close()
        
        return jsonify({
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        }), 200
        
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