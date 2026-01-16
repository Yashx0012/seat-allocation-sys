# Allocation session management endpoints.
# Controls session lifecycle including initialization, heartbeats, finalization, and student allocation tracking.
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from algo.auth_service import token_required
import sqlite3
import random
import string

session_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')

# ============================================================================
# HELPER: Get DB Connection
# ============================================================================
def _get_conn():
    from algo.database.db import get_db_connection
    return get_db_connection()

# ============================================================================
# HELPER: Get Session Statistics
# ============================================================================
def _get_session_stats(session_id):
    """Get allocation statistics for a session"""
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    try:
        # Overall stats
        cur.execute("""
            SELECT total_students, allocated_count, status
            FROM allocation_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        session_row = cur.fetchone()
        if not session_row:
            return {}
        
        session_data = dict(session_row)
        
        # Per-room stats
        cur.execute("""
            SELECT
                c.name,
                c.rows * c.cols as capacity,
                COUNT(a.id) as allocated,
                c.rows * c.cols - COUNT(a.id) as empty_seats
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
        
        # Calculate completion rate
        completion_rate = 0
        if session_data['total_students'] and session_data['total_students'] > 0:
            completion_rate = round(
                (session_data['allocated_count'] / session_data['total_students']) * 100, 2
            )
        
        return {
            "session": session_data,
            "rooms": room_stats,
            "batches": batch_stats,
            "completion_rate": completion_rate
        }
        
    except Exception as e:
        print(f"❌ Error getting session stats: {e}")
        return {}
    finally:
        conn.close()


# POST /api/sessions/start - LEGACY COMPATIBLE
# ============================================================================
@session_bp.route('/start', methods=['POST'])
@token_required
def start_session():
    """
    Start new allocation session - LEGACY COMPATIBLE.
    
    Checks for existing active session:
    - If active AND user active in last 30 min → return error
    - If active BUT inactive > 30 min → auto-expire then create new
    - Otherwise → create new session
    """
    try:
        data = request.get_json() or {}
        print(f"DEBUG: start_session data: {data}")
        upload_ids = data.get('upload_ids', [])
        print(f"DEBUG: upload_ids: {upload_ids}")
        
        if not upload_ids:
            return jsonify({
                'success': False,
                'error': 'No upload IDs provided'
            }), 400
        
        conn = _get_conn()
        cursor = conn.cursor()
        
        # Check for existing active session for THIS user
        cursor.execute("""
            SELECT session_id, last_activity, allocated_count, total_students
            FROM allocation_sessions 
            WHERE status = 'active' AND user_id = ?
            ORDER BY last_activity DESC
            LIMIT 1
        """, (request.user_id,))
        existing = cursor.fetchone()
        
        if existing:
            existing_id = existing[0]
            last_activity = existing[1]
            allocated = existing[2] or 0
            total = existing[3] or 0
            
            # Check if session is abandoned (no activity in 30 minutes)
            if last_activity:
                try:
                    last_active = datetime.fromisoformat(str(last_activity))
                    inactive_duration = datetime.now() - last_active
                    
                    if inactive_duration > timedelta(minutes=30) or total == 0:
                        # Auto-expire abandoned or empty session
                        reason = "orphaned/empty" if total == 0 else "abandoned"
                        print(f"⏰ Auto-expiring {reason} session {existing_id}")
                        cursor.execute("""
                            UPDATE allocation_sessions
                            SET status = 'expired'
                            WHERE session_id = ?
                        """, (existing_id,))
                        # Continue to create new session
                    else:
                        # Session is legitimately active - return error
                        conn.close()
                        return jsonify({
                            'success': False,
                            'error': 'An active session already exists',
                            'existing_session': {
                                'session_id': existing_id,
                                'allocated': allocated,
                                'total': total,
                                'last_activity': str(last_activity)
                            }
                        }), 400
                except Exception as e:
                    print(f"Date parse error: {e}")
                    # If date parsing fails, continue to create new session
        
        # Generate plan_id
        plan_id = f"PLAN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        
        # Calculate total students from uploads
        placeholders = ','.join('?' * len(upload_ids))
        cursor.execute(f"""
            SELECT COUNT(*) FROM students 
            WHERE upload_id IN ({placeholders})
        """, upload_ids)
        
        total_students = cursor.fetchone()[0] or 0
        
        # Create session
        cursor.execute("""
            INSERT INTO allocation_sessions (user_id, plan_id, total_students, allocated_count, status, last_activity)
            VALUES (?, ?, ?, 0, 'active', ?)
        """, (request.user_id, plan_id, total_students, datetime.now().isoformat()))
        
        session_id = cursor.lastrowid
        
        # Link uploads to session
        for upload_id in upload_ids:
            cursor.execute("""
                UPDATE uploads
                SET session_id = ?
                WHERE id = ?
            """, (session_id, upload_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Created session {session_id} with plan_id {plan_id}, {total_students} students")
        
        return jsonify({
            'success': True,
            'session': {
                'session_id': session_id,
                'plan_id': plan_id,
                'total_students': total_students,
                'allocated_count': 0,
                'pending_count': total_students,
                'allocated_rooms': []
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# GET /api/sessions/active - LEGACY COMPATIBLE
# ============================================================================
@session_bp.route('/active', methods=['GET'])
@token_required
def get_active_session():
    """Get the active session with all required data"""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        # Get active session for THIS user
        cursor.execute("""
            SELECT 
                session_id, 
                plan_id, 
                total_students, 
                allocated_count,
                status,
                created_at,
                last_activity
            FROM allocation_sessions 
            WHERE status = 'active' AND user_id = ?
            ORDER BY last_activity DESC 
            LIMIT 1
        """, (request.user_id,))
        
        session_row = cursor.fetchone()
        
        if not session_row:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'No active session',
                'session_data': None
            }), 200
        
        session_id = session_row[0]
        
        # Get allocated rooms
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
        
        allocated_rooms_rows = cursor.fetchall()
        
        allocated_rooms = []
        if allocated_rooms_rows:
            for row in allocated_rooms_rows:
                allocated_rooms.append({
                    'classroom_id': row[0],
                    'classroom_name': row[1] or 'Unknown',
                    'count': row[2] or 0
                })
        
        conn.close()
        
        total_students = session_row[2] or 0
        allocated_count = session_row[3] or 0
        pending_count = max(0, total_students - allocated_count)
        
        return jsonify({
            'success': True,
            'session_data': {
                'session_id': session_row[0],
                'plan_id': session_row[1],
                'total_students': total_students,
                'allocated_count': allocated_count,
                'pending_count': pending_count,
                'status': session_row[4],
                'created_at': session_row[5],
                'last_activity': session_row[6],
                'allocated_rooms': allocated_rooms
            }
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
# GET /api/sessions/<id> - Get specific session
# ============================================================================
@session_bp.route('/<int:session_id>', methods=['GET'])
@token_required
def get_session(session_id):
    """Get session details"""
    try:
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM allocation_sessions WHERE session_id = ? AND user_id = ?", (session_id, request.user_id))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({"status": "error", "message": "Session not found"}), 404
        return jsonify({"status": "success", "data": dict(row)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# DELETE /api/sessions/<id>/delete - Expire session
# ============================================================================
@session_bp.route('/<int:session_id>/delete', methods=['DELETE'])
@token_required
def delete_session(session_id):
    """Delete/Expire a session"""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE allocation_sessions SET status = 'expired' WHERE session_id = ? AND user_id = ?
        """, (session_id, request.user_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Session deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# GET /api/sessions/<id>/status - Check session expiry
# ============================================================================
@session_bp.route('/<int:session_id>/status', methods=['GET'])
@token_required
def check_status(session_id):
    """Check session health/expiry"""
    try:
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.*, u.last_activity as user_last_activity
            FROM allocation_sessions s
            LEFT JOIN user_activity u ON s.user_id = u.user_id
            WHERE s.session_id = ? AND s.user_id = ?
        """, (session_id, request.user_id))
        
        session = cursor.fetchone()
        conn.close()
        
        if not session:
            return jsonify({"should_expire": True, "reason": "Session not found"}), 200
        
        if session['status'] in ['completed', 'archived']:
            return jsonify({"should_expire": False, "reason": "Session is completed/archived"}), 200
        
        # Check user activity
        if session['user_last_activity']:
            last_activity = datetime.fromisoformat(str(session['user_last_activity']))
            inactive_duration = datetime.now() - last_activity
            
            if inactive_duration > timedelta(minutes=30):
                return jsonify({
                    "should_expire": True, 
                    "reason": f"User inactive for {int(inactive_duration.total_seconds() / 60)} minutes"
                }), 200
        
        return jsonify({"should_expire": False, "reason": "Session is active"}), 200
        
    except Exception as e:
        return jsonify({"should_expire": False, "reason": f"Error: {str(e)}"}), 200

# ============================================================================
# POST /api/sessions/<id>/heartbeat - Update activity
# ============================================================================
@session_bp.route('/<int:session_id>/heartbeat', methods=['POST'])
@token_required
def heartbeat(session_id):
    """Update session activity timestamp"""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE allocation_sessions
            SET last_activity = ?
            WHERE session_id = ? AND user_id = ?
        """, (datetime.now().isoformat(), session_id, request.user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# GET /api/sessions/<id>/uploads - Get uploads for session
# ============================================================================
@session_bp.route('/<int:session_id>/uploads', methods=['GET'])
@token_required
def get_session_uploads(session_id):
    """Get all uploads/batches for a session"""
    try:
        # Verify ownership
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM allocation_sessions WHERE session_id = ?", (session_id,))
        owner = cur.fetchone()
        if not owner or owner[0] != request.user_id:
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403

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
            "uploads": uploads
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# POST /api/sessions/force-new - Force create new session
# ============================================================================
@session_bp.route('/force-new', methods=['POST'])
@token_required
def force_new_session():
    """Force-expire any active sessions so a new one can be started"""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        # Force-expire MY active sessions
        cursor.execute("""
            UPDATE allocation_sessions
            SET status = 'expired'
            WHERE status = 'active' AND user_id = ?
        """, (request.user_id,))
        expired_count = cursor.rowcount
        print(f"⚠️ Force-expired {expired_count} active session(s)")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Expired {expired_count} active sessions. Ready to start new session."
        })
        
    except Exception as e:
        print(f"Force new error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# POST /api/sessions/<id>/recover - Recover expired session
# ============================================================================
@session_bp.route('/<int:session_id>/recover', methods=['POST'])
@token_required
def recover_session(session_id):
    """Recover an expired session"""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE allocation_sessions
            SET status = 'active', last_activity = ?
            WHERE session_id = ? AND status = 'expired' AND user_id = ?
        """, (datetime.now().isoformat(), session_id, request.user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Session not found or not recoverable"}), 404
        
        conn.commit()
        conn.close()
        
        print(f"🔄 Recovered session {session_id}")
        
        return jsonify({
            "success": True,
            "message": "Session recovered successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# POST /api/sessions/<id>/finalize - Mark session complete
# ============================================================================
@session_bp.route('/<int:session_id>/finalize', methods=['POST'])
@token_required
def finalize_session(session_id):
    """Finalize session - mark complete and clean cache"""
    try:
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get session info - filter by user_id
        cur.execute("""
            SELECT plan_id, total_students, allocated_count, status
            FROM allocation_sessions
            WHERE session_id = ? AND user_id = ?
        """, (session_id, request.user_id))
        
        session = cur.fetchone()
        
        if not session:
            conn.close()
            return jsonify({"error": "Session not found"}), 404
        
        if session['status'] != 'active':
            conn.close()
            return jsonify({"error": f"Session is already {session['status']}"}), 400
        
        plan_id = session['plan_id']
        
        # Get list of allocated rooms
        cur.execute("""
            SELECT DISTINCT c.name
            FROM allocations a
            JOIN classrooms c ON a.classroom_id = c.id
            WHERE a.session_id = ?
        """, (session_id,))
        
        allocated_rooms = [row['name'] for row in cur.fetchall()]
        
        print(f"🏁 Finalizing session {session_id}, rooms: {allocated_rooms}")
        
        # Update session status
        cur.execute("""
            UPDATE allocation_sessions
            SET status = 'completed',
                last_activity = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
        
        # Try to finalize cache if available
        try:
            from algo.core.cache.cache_manager import CacheManager
            cache_manager = CacheManager()
            if allocated_rooms:
                cache_manager.finalize_rooms(plan_id, allocated_rooms)
                print(f"✅ Cache finalized with rooms: {allocated_rooms}")
        except Exception as cache_err:
            print(f"⚠️ Cache finalize warning: {cache_err}")
        
        return jsonify({
            "success": True,
            "message": "Session finalized successfully",
            "plan_id": plan_id,
            "rooms": allocated_rooms
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============================================================================
# GET /api/sessions/<id>/pending - Get pending students
# ============================================================================
@session_bp.route('/<int:session_id>/pending', methods=['GET'])
@token_required
def get_session_pending(session_id):
    """Get pending (unallocated) students for session"""
    try:
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT s.id, s.enrollment, s.name, s.batch_name, s.batch_id, s.batch_color
            FROM students s
            JOIN uploads u ON s.upload_id = u.id
            WHERE u.session_id = ? AND u.user_id = ?
            AND s.id NOT IN (
                SELECT student_id FROM allocations
                WHERE session_id = ?
            )
            ORDER BY s.batch_name, s.enrollment
        """, (session_id, request.user_id, session_id))
        
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
# POST /api/sessions/<id>/allocate-room - Allocate room in session
# ============================================================================
@session_bp.route('/<int:session_id>/allocate-room', methods=['POST'])
@token_required
def allocate_room_in_session(session_id):
    """Save allocation for ONE room"""
    try:
        data = request.get_json() or {}
        classroom_id = data.get('classroom_id')
        seating_data = data.get('seating_data')
        selected_batch_names = data.get('selected_batch_names', [])
        
        if classroom_id is None or seating_data is None:
            return jsonify({"error": "Missing classroom_id or seating_data"}), 400
        
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Validate session - check ownership
        cur.execute("""
            SELECT session_id, plan_id, status, total_students, allocated_count
            FROM allocation_sessions
            WHERE session_id = ? AND user_id = ?
        """, (session_id, request.user_id))
        
        session_row = cur.fetchone()
        
        if not session_row:
            conn.close()
            return jsonify({"error": "Session not found"}), 404
        
        if session_row['status'] != 'active':
            conn.close()
            return jsonify({"error": f"Session is {session_row['status']}, cannot allocate"}), 400
        
        # Get classroom info
        cur.execute("SELECT id, name, rows, cols FROM classrooms WHERE id = ?", (classroom_id,))
        classroom = cur.fetchone()
        if not classroom:
            conn.close()
            return jsonify({"error": "Classroom not found"}), 404
        
        # Process seating and save to database
        seating_matrix = seating_data.get('seating', [])
        allocated_students = []
        
        for row_idx, row in enumerate(seating_matrix):
            for col_idx, seat in enumerate(row):
                if seat and not seat.get('is_broken') and not seat.get('is_unallocated'):
                    enrollment = seat.get('roll_number')
                    if not enrollment:
                        continue
                    
                    # Find unallocated student
                    cur.execute("""
                        SELECT s.id, s.batch_name
                        FROM students s
                        JOIN uploads u ON s.upload_id = u.id
                        WHERE s.enrollment = ?
                        AND u.session_id = ?
                        AND s.id NOT IN (
                            SELECT student_id FROM allocations WHERE session_id = ?
                        )
                    """, (enrollment, session_id, session_id))
                    
                    student_row = cur.fetchone()
                    
                    if student_row:
                        student_id = student_row['id']
                        batch_name = student_row['batch_name']
                        
                        if selected_batch_names and batch_name not in selected_batch_names:
                            continue
                        
                        seat_pos = f"{row_idx + 1}-{col_idx + 1}"
                        paper_set = seat.get('paper_set', 'A')
                        
                        cur.execute("""
                            INSERT INTO allocations
                            (session_id, classroom_id, student_id, enrollment,
                             seat_position, batch_name, paper_set)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (session_id, classroom_id, student_id, enrollment,
                              seat_pos, batch_name, paper_set))
                        
                        allocated_students.append({
                            'enrollment': enrollment,
                            'seat': seat_pos,
                            'batch': batch_name,
                            'paper_set': paper_set
                        })
        
        # Update session totals
        cur.execute("""
            UPDATE allocation_sessions
            SET allocated_count = allocated_count + ?,
                last_activity = ?
            WHERE session_id = ?
        """, (len(allocated_students), datetime.now().isoformat(), session_id))
        
        conn.commit()
        
        # Get fresh session data
        cur.execute("""
            SELECT session_id, plan_id, total_students, allocated_count, status
            FROM allocation_sessions WHERE session_id = ?
        """, (session_id,))
        fresh = cur.fetchone()
        
        # Get allocated rooms
        cur.execute("""
            SELECT a.classroom_id, c.name as classroom_name, COUNT(a.id) as count
            FROM allocations a
            LEFT JOIN classrooms c ON a.classroom_id = c.id
            WHERE a.session_id = ?
            GROUP BY a.classroom_id, c.name
        """, (session_id,))
        
        allocated_rooms = [
            {'classroom_id': r[0], 'classroom_name': r[1] or 'Unknown', 'count': r[2] or 0}
            for r in cur.fetchall()
        ]
        
        # HISTORY TRACKING (Legacy Compatible)
        try:
            # Determine step number
            cur.execute("SELECT COALESCE(MAX(step_number), 0) + 1 FROM allocation_history WHERE session_id = ?", (session_id,))
            step_num = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO allocation_history
                (session_id, step_number, classroom_id, action_type, students_affected)
                VALUES (?, ?, ?, 'allocate', ?)
            """, (session_id, step_num, classroom_id, len(allocated_students)))
            conn.commit()
        except Exception as hist_e:
            print(f"⚠️ History tracking failed: {hist_e}")
            # Don't fail the request, just log it
            
        conn.close()
        
        # Save to Cache (Legacy Compatibility)
        try:
            from algo.core.cache.cache_manager import CacheManager
            cache_mgr = CacheManager()
            
            # Construct payload for cache
            # seating_data from request contains 'seating' (matrix)
            # We need to construct valid input_config and output_data
            
            # Use metadata from seating_data if available, relative to room
            meta = seating_data.get('metadata', {}) or seating_data.get('inputs', {})
            
            # Ensure output_data has 'seating'
            output_payload = {
                'seating': seating_matrix, # verify this variable exists in scope (it does from earlier)
                'stats': {}, # Optional stats
                'metadata': meta,
                'inputs': meta,
                'batches': {} # We could populate this but CacheManager rebuilds it from seating
            }
            
            cache_mgr.save_or_update(
                plan_id=fresh['plan_id'],
                input_config=meta, 
                output_data=output_payload, 
                room_no=classroom['name']
            )
            print(f"✅ Saved to CACHE: plan={fresh['plan_id']}, room={classroom['name']}")
            
        except Exception as cache_err:
            print(f"⚠️ Cache save warning: {cache_err}")

        fresh_total = fresh['total_students'] or 0
        fresh_allocated = fresh['allocated_count'] or 0
        fresh_pending = max(0, fresh_total - fresh_allocated)
        
        return jsonify({
            "success": True,
            "message": f"Allocated {len(allocated_students)} students",
            "allocated_count": len(allocated_students),
            "session": {
                "session_id": fresh['session_id'],
                "plan_id": fresh['plan_id'],
                "total_students": fresh_total,
                "allocated_count": fresh_allocated,
                "pending_count": fresh_pending,
                "status": fresh['status'],
                "allocated_rooms": allocated_rooms
            },
            "remaining_count": fresh_pending,
            "pending_count": fresh_pending,
            "can_finalize": fresh_pending == 0
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============================================================================
# POST /api/sessions/<id>/undo - Undo last allocation
# ============================================================================
@session_bp.route('/<int:session_id>/undo', methods=['POST'])
@token_required
def undo_last_session_action(session_id):
    """Undo the last allocation action for this session"""
    conn = _get_conn()
    cur = conn.cursor()
    
    try:
        # Verify ownership
        cur.execute("SELECT user_id FROM allocation_sessions WHERE session_id = ?", (session_id,))
        owner = cur.fetchone()
        if not owner or owner[0] != request.user_id:
            conn.close()
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        # 1. Try to find the last action from history
        cur.execute("""
            SELECT id, classroom_id, students_affected
            FROM allocation_history
            WHERE session_id = ? AND action_type = 'allocate'
            ORDER BY step_number DESC
            LIMIT 1
        """, (session_id,))
        
        last_step = cur.fetchone()
        
        target_classroom_id = None
        affected_count = 0
        history_record_id = None
        
        if last_step:
            history_record_id, target_classroom_id, affected_count = last_step
            # print(f"DEBUG: Found history record {history_record_id} for room {target_classroom_id}")
        else:
            # FALLBACK: No history found. Check if there are ANY allocations using table data.
            # We assume the last batch of allocations (highest ID) belongs to the last action.
            # print(f"DEBUG: No history found for session {session_id}. Checking allocations table fallback.")
            
            # Use MAX(id) to find the latest inserted allocations
            cur.execute("""
                SELECT classroom_id, COUNT(*) as cnt
                FROM allocations 
                WHERE session_id = ?
                GROUP BY classroom_id
                ORDER BY MAX(id) DESC
                LIMIT 1
            """, (session_id,))
            
            fallback_row = cur.fetchone()
            if fallback_row:
                target_classroom_id, affected_count = fallback_row
                # print(f"DEBUG: Fallback found: Undoing room {target_classroom_id} with {affected_count} seats.")
            
        if not target_classroom_id:
            conn.close()
            return jsonify({
                "success": False, 
                "message": "No allocations to undo"
            }), 400
            
        # 2. Perform Undo: Delete allocations
        cur.execute("""
            DELETE FROM allocations
            WHERE session_id = ? AND classroom_id = ?
        """, (session_id, target_classroom_id))
        
        # 3. Update Session Totals
        cur.execute("""
            UPDATE allocation_sessions
            SET allocated_count = MAX(0, allocated_count - ?),
                last_activity = ?
            WHERE session_id = ?
        """, (affected_count, datetime.now().isoformat(), session_id))
        
        # 4. Update History
        # Get next step number
        cur.execute("SELECT COALESCE(MAX(step_number), 0) + 1 FROM allocation_history WHERE session_id = ?", (session_id,))
        next_step = cur.fetchone()[0]
        
        # Insert 'undo' record for visibility
        cur.execute("""
            INSERT INTO allocation_history
            (session_id, step_number, classroom_id, action_type, students_affected)
            VALUES (?, ?, ?, 'undo', ?)
        """, (session_id, next_step, target_classroom_id, affected_count))
        
        # CRITICAL: If we used an existing history record, DELETE it so it is not undone again.
        if history_record_id:
            cur.execute("DELETE FROM allocation_history WHERE id = ?", (history_record_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": f"Undid allocation for room {target_classroom_id} ({affected_count} students removed)"
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        if conn: conn.close()
        return jsonify({"success": False, "message": str(e)}), 500
        # Let's delete the history record of the action we just undid to be safe and logical.
        
        cur.execute("DELETE FROM allocation_history WHERE id = ?", (history_id,))
        
        conn.commit()
        
        # Update Cache (Remove room from cache if needed)
        # We should probably reload the plan and remove this room to stay consistent
        # ... (Advanced: impl cache update if strictly needed, but DB is source of truth for next allocate)
        
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": f"Undid allocation for classroom (Students: {students_affected})"
        }), 200
        
    except Exception as e:
        if conn: conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# GET /api/sessions/<id>/stats - Get session statistics
# ============================================================================
@session_bp.route('/<int:session_id>/stats', methods=['GET'])
@token_required
def get_session_statistics(session_id):
    """Get allocation statistics for session"""
    try:
        # Verify ownership
        conn_v = _get_conn()
        cur_v = conn_v.cursor()
        cur_v.execute("SELECT user_id FROM allocation_sessions WHERE session_id = ?", (session_id,))
        owner = cur_v.fetchone()
        conn_v.close()
        
        if not owner or owner[0] != request.user_id:
            return jsonify({"error": "Unauthorized"}), 403

        stats = _get_session_stats(session_id)
        
        if not stats:
            return jsonify({"error": "Session not found or no stats available"}), 404
        
        return jsonify({
            "success": True,
            "stats": stats
        }), 200
        
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500
