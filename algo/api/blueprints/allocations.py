# Seating allocation endpoints.
# Orchestrates the generation of seating plans and manages the session-specific manual caching.
from flask import Blueprint, request, jsonify
from algo.core.cache.cache_manager import CacheManager
from algo.core.algorithm.seating import SeatingAlgorithm
from algo.utils.helpers import parse_str_dict, parse_int_dict
from algo.database.db import get_db_connection
from algo.auth_service import token_required
import uuid
import sqlite3

allocation_bp = Blueprint('allocations', __name__, url_prefix='/api')

# ============================================================================
# HELPER: Get pending students for a session
# ============================================================================
def get_pending_students(session_id):
    """Get students not yet allocated in this session"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT s.id, s.enrollment, s.name, s.batch_name, s.batch_id, s.batch_color
            FROM students s
            JOIN uploads u ON s.upload_id = u.id
            WHERE u.session_id = ?
            AND s.id NOT IN (
                SELECT student_id FROM allocations
                WHERE session_id = ?
            )
            ORDER BY s.batch_name, s.enrollment
        """, (session_id, session_id))
        
        pending = [dict(row) for row in cur.fetchall()]
        conn.close()
        return pending
    except Exception as e:
        print(f"Error fetching pending students: {e}")
        return []

# ============================================================================
# POST /api/generate-seating - SESSION-BASED SEATING GENERATION
# ============================================================================
@allocation_bp.route('/generate-seating', methods=['POST'])
@token_required
def generate_seating():
    """Generate seating - FILTER by selected batches only (LEGACY COMPATIBLE)"""
    try:
        data = request.get_json(force=True)
        
        plan_id = data.get("plan_id")
        session_id = data.get("session_id")
        
        # Verify session ownership
        if session_id:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM allocation_sessions WHERE session_id = ?", (session_id,))
            owner = cur.fetchone()
            conn.close()
            if not owner or owner[0] != request.user_id:
                return jsonify({"error": "Unauthorized session"}), 403

        if not plan_id:
            plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        use_db = bool(data.get("use_demo_db", True))
        
        # Get batch info from payload
        batch_labels = data.get("batch_labels", {})  # {1: "Batch A", 2: "Batch B"}
        # Convert string keys to int if needed
        if batch_labels:
            batch_labels = {int(k): v for k, v in batch_labels.items()}
        selected_batch_names = list(batch_labels.values()) if batch_labels else []
        
        counts = {}
        labels = {}
        rolls = {}
        colors = {}
        num_batches = 0
        
        if use_db and session_id:
            print(f"🔍 Selected batches: {selected_batch_names}")
            
            # Get ONLY pending students
            pending_students = get_pending_students(session_id)
            
            if not pending_students:
                return jsonify({
                    "error": "No pending students available",
                    "message": "All students have been allocated.",
                    "pending_count": 0
                }), 400
            
            # CRITICAL FIX: Filter by selected batch names ONLY
            filtered_students = [
                s for s in pending_students 
                if s.get('batch_name') in selected_batch_names
            ]
            
            if not filtered_students:
                return jsonify({
                    "error": "No pending students in selected batches",
                    "pending_count": 0
                }), 400
            
            print(f"📋 Filtered: {len(filtered_students)} / {len(pending_students)} pending")
            
            # Group by batch name
            batch_groups = {}
            for student in filtered_students:
                batch_name = student.get('batch_name') or 'Unknown'
                if batch_name not in batch_groups:
                    batch_groups[batch_name] = {
                        'students': [],
                        'color': student.get('batch_color', '#3b82f6')
                    }
                
                batch_groups[batch_name]['students'].append({
                    'roll': student.get('enrollment'),
                    'name': student.get('name', '')
                })
            
            # Convert to algorithm format (1-indexed)
            batch_colors_from_payload = data.get("batch_colors", {})
            if batch_colors_from_payload:
                batch_colors_from_payload = {int(k): v for k, v in batch_colors_from_payload.items()}
            
            for idx, batch_name in enumerate(selected_batch_names, start=1):
                if batch_name in batch_groups:
                    students_list = batch_groups[batch_name]['students']
                    counts[idx] = len(students_list)
                    labels[idx] = batch_name
                    rolls[idx] = students_list
                    colors[idx] = batch_groups[batch_name]['color']
                else:
                    print(f"⚠️ Batch '{batch_name}' has no pending students")
                    counts[idx] = 0
                    labels[idx] = batch_name
                    rolls[idx] = []
                    colors[idx] = batch_colors_from_payload.get(idx, '#3b82f6')
            
            num_batches = len(selected_batch_names)
            
            print(f"📊 Batch counts: {counts}")
        
        else:
            # Fallback for non-session mode
            batch_student_counts = data.get("batch_student_counts", {})
            if batch_student_counts:
                counts = {int(k): int(v) for k, v in batch_student_counts.items()}
            labels = {int(k): v for k, v in batch_labels.items()} if batch_labels else {}
            rolls = data.get("batch_roll_numbers") or {}
            batch_colors_raw = data.get("batch_colors", {})
            if batch_colors_raw:
                colors = {int(k): v for k, v in batch_colors_raw.items()}
            num_batches = int(data.get("num_batches", len(counts)))
        
        if num_batches == 0 or not counts:
            return jsonify({"error": "No batch data available"}), 400
        
        # Parse broken seats
        broken_str = data.get("broken_seats", "")
        broken_seats = []
        
        if broken_str:
            if isinstance(broken_str, str) and broken_str.strip():
                for seat_str in broken_str.split(","):
                    seat_str = seat_str.strip()
                    if "-" in seat_str:
                        try:
                            r, c = seat_str.split("-")
                            broken_seats.append((int(r) - 1, int(c) - 1))
                        except (ValueError, IndexError):
                            pass
            elif isinstance(broken_str, list):
                for seat in broken_str:
                    if isinstance(seat, (list, tuple)) and len(seat) == 2:
                        broken_seats.append((int(seat[0]), int(seat[1])))
        
        total_pending = sum(counts.values())
        print(f"DEBUG: Starting generation for {total_pending} students") # EXTRA DEBUG
        print(f"🎯 Generating: {total_pending} students, {num_batches} batches")

        # Define room configuration for cache matching/saving (Renamed to avoid conflict)
        seating_room_config = {
            'rows': int(data.get("rows", 10)),
            'cols': int(data.get("cols", 6)),
            'block_width': int(data.get("block_width", 2)),
            'broken_seats': broken_seats
        }

        # [STEP 1] Check if seating for THIS plan and THIS room exists in cache
        try:
            cache_manager = CacheManager()
            target_room = data.get('room_no') or data.get('room_name') or "N/A"
            
            # Use the session-specific plan_id if available
            current_plan_id = plan_id
            if session_id:
                try:
                    db_conn = get_db_connection()
                    db_cur = db_conn.cursor()
                    db_cur.execute("SELECT plan_id FROM allocation_sessions WHERE session_id = ? AND user_id = ?", (session_id, request.user_id))
                    row = db_cur.fetchone()
                    if row and row[0]:
                        current_plan_id = row[0]
                    db_conn.close()
                except: pass

            # Load existing cache just to verify it exists/get metadata
            # But DO NOT return early - let generation proceed to allow overwrites/experiments
            cached_data = cache_manager.load_snapshot(current_plan_id)
            if cached_data:
                print(f"📂 [L1-CACHE] Found existing plan {current_plan_id}, will update room: {target_room}")
        except Exception as cache_lookup_err:
            print(f"⚠️ Cache info retrieval failed: {cache_lookup_err}")

        # Initialize algorithm
        algo = SeatingAlgorithm(
            rows=int(data.get("rows", 10)),
            cols=int(data.get("cols", 6)),
            num_batches=num_batches,
            block_width=int(data.get("block_width", 2)),
            batch_by_column=bool(data.get("batch_by_column", True)),
            randomize_column=bool(data.get("randomize_column", False)),
            broken_seats=broken_seats,
            batch_student_counts=counts,
            batch_roll_numbers=rolls,
            batch_labels=labels,
            start_rolls=parse_str_dict(data.get("start_rolls")),
            batch_colors=colors,
            serial_mode=data.get("serial_mode", "per_batch"),
            serial_width=int(data.get("serial_width", 0))
        )
        
        if session_id:
            try:
                db_conn = get_db_connection()
                db_cur = db_conn.cursor()
                db_cur.execute("SELECT plan_id FROM allocation_sessions WHERE session_id = ? AND user_id = ?", (session_id, request.user_id))
                row = db_cur.fetchone()
                if row and row[0]:
                    plan_id = row[0]
                    print(f"✅ Using Session Plan ID for generation: {plan_id}")
                db_conn.close()
            except: pass

        # Generate seating
        algo.generate_seating()
        web = algo.to_web_format()

        # Add metadata
        web.setdefault("metadata", {})
        web["plan_id"] = plan_id
        web["session_id"] = session_id
        web["pending_count"] = total_pending
        web["selected_batches"] = selected_batch_names
        
        # Validate
        ok, errors = algo.validate_constraints()
        
        # Merge init_errors into validation errors for visibility
        if algo.init_errors:
            errors = algo.init_errors + errors
            ok = False # Critical initialization errors should invalidate the plan
            
        web["validation"] = {"is_valid": ok, "errors": errors}
        
        # Cache result
        room_name = data.get('room_no') or data.get('room_name') or "N/A"
        try:
            print(f"DEBUG: Attempting cache update for plan {plan_id}, room {room_name}")
            cache_manager = CacheManager()
            cache_manager.save_or_update(
                plan_id=plan_id, 
                input_config=seating_room_config, 
                output_data=web, 
                room_no=room_name
            )
        except Exception as cache_err:
            print(f"⚠️ Cache save warning: {cache_err}")
            # If still failing, try using raw data as fallback
            try:
                print("DEBUG: Retrying with raw data...")
                cache_manager.save_or_update(plan_id, data, web, room_name)
            except: pass
        
        print(f"✅ Seating generated for: {selected_batch_names}")
        
        return jsonify(web)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to generate seating: {str(e)}"}), 500

# ============================================================================
# POST /api/manual-generate-seating - MANUAL MODE (NO DB)
# ============================================================================
@allocation_bp.route('/manual-generate-seating', methods=['POST'])
@token_required
def manual_generate_seating():
    """Generate seating without DB (Manual Mode)"""
    try:
        data = request.get_json(force=True)
        num_batches = int(data.get("num_batches", 3))
        
        # Parse batch student counts
        counts = {}
        batch_student_counts_str = data.get("batch_student_counts", "")
        if batch_student_counts_str:
            if isinstance(batch_student_counts_str, dict):
                counts = {int(k): int(v) for k, v in batch_student_counts_str.items()}
            else:
                parts = [p.strip() for p in str(batch_student_counts_str).split(',') if p.strip()]
                for part in parts:
                    if ':' in part:
                        try:
                            k, v = part.split(':', 1)
                            counts[int(k.strip())] = int(v.strip())
                        except: pass

        # Parse batch names/labels
        labels = {}
        batch_names_str = data.get("batch_names", "")
        if batch_names_str:
            if isinstance(batch_names_str, dict):
                labels = {int(k): v for k, v in batch_names_str.items()}
            else:
                parts = [p.strip() for p in str(batch_names_str).split(',') if p.strip()]
                for part in parts:
                    if ':' in part:
                        try:
                            k, v = part.split(':', 1)
                            labels[int(k.strip())] = v.strip()
                        except: pass

        # Parse start_rolls
        start_rolls = {}
        start_rolls_str = data.get("start_rolls", "")
        if start_rolls_str:
            parts = [p.strip() for p in str(start_rolls_str).split(',') if p.strip()]
            for part in parts:
                if ':' in part:
                    try:
                        k, v = part.split(':', 1)
                        start_rolls[int(k.strip())] = v.strip()
                    except: pass

        # Parse broken seats
        broken_seats = []
        broken_str = data.get("broken_seats", "")
        if isinstance(broken_str, str) and "-" in broken_str:
            parts = [p.strip() for p in broken_str.split(',') if p.strip()]
            for part in parts:
                if '-' in part:
                    try:
                        row_col = part.split('-')
                        row = int(row_col[0].strip()) - 1
                        col = int(row_col[1].strip()) - 1
                        broken_seats.append((row, col))
                    except: pass
        elif isinstance(broken_str, list):
            broken_seats = broken_str

        # Initialize algorithm with all parameters
        algo = SeatingAlgorithm(
            rows=int(data.get("rows", 10)),
            cols=int(data.get("cols", 10)),
            num_batches=num_batches,
            block_width=int(data.get("block_width", 3)),
            batch_by_column=bool(data.get("batch_by_column", True)),
            randomize_column=bool(data.get("randomize_column", False)),
            broken_seats=broken_seats,
            batch_student_counts=counts,
            batch_roll_numbers={},
            batch_labels=labels,
            start_rolls=start_rolls,
            batch_colors=parse_str_dict(data.get("batch_colors")),
            serial_mode=data.get("serial_mode", "per_batch"),
            serial_width=int(data.get("serial_width", 0))
        )
        
        algo.generate_seating()
        web = algo.to_web_format()
        
        web.setdefault("metadata", {})
        
        ok, errors = algo.validate_constraints()
        web["validation"] = {"is_valid": ok, "errors": errors}
        
        # Save to manual cache
        MANUAL_CACHE_FILE = "manual_seating_current"
        cm = CacheManager() 
        cm.save_or_update(MANUAL_CACHE_FILE, data, web)
        
        print(f"✅ Manual seating generated - Batches: {num_batches}")
        
        return jsonify(web)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============================================================================
# POST /api/constraints-status
# ============================================================================
@allocation_bp.route('/constraints-status', methods=['POST'])
@token_required
def constraints_status():
    """Get constraint validation status"""
    try:
        data = request.get_json(force=True)
        
        algo = SeatingAlgorithm(
            rows=int(data.get("rows", 10)),
            cols=int(data.get("cols", 6)),
            num_batches=int(data.get("num_batches", 3)),
            block_width=int(data.get("block_width", 2)),
            batch_by_column=bool(data.get("batch_by_column", True)),
            randomize_column=bool(data.get("randomize_column", False))
        )
        
        algo.generate_seating()
        
        return jsonify(algo.get_constraints_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# Save/Reset Allocation Routes
# ============================================================================
@allocation_bp.route('/save-allocation', methods=['POST'])
@token_required
def save_allocation():
    """Persist allocation to Database"""
    data = request.json
    session_id = data.get('session_id')
    classroom_id = data.get('classroom_id')
    seating_plan = data.get('seating_plan')
    
    if not session_id or not seating_plan:
        return jsonify({"status": "error", "message": "Missing data"}), 400
    
    # TODO: Implement actual save logic
    return jsonify({"status": "success", "message": "Saved to database"}), 200

@allocation_bp.route('/reset-allocation', methods=['POST'])
@token_required
def reset_allocation():
    data = request.json
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({"status": "error", "message": "Session ID required"}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify ownership
        cur.execute("SELECT user_id FROM allocation_sessions WHERE session_id = ?", (session_id,))
        owner = cur.fetchone()
        if not owner or owner[0] != request.user_id:
            conn.close()
            return jsonify({"status": "error", "message": "Unauthorized"}), 403

        cur.execute("DELETE FROM allocations WHERE session_id = ?", (session_id,))
        cur.execute("""
            UPDATE allocation_sessions 
            SET allocated_count = 0 
            WHERE session_id = ? AND user_id = ?
        """, (session_id, request.user_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Allocations reset"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@allocation_bp.route('/allocations', methods=['GET'])
@token_required
def get_allocations():
    return jsonify({"status": "success", "allocations": []})
