# PDF generation and report export endpoints.
# Handles the creation of seating plan vectors, attendance sheets, and compressed export logs.
import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from algo.auth_service import token_required
from algo.core.cache.cache_manager import CacheManager

pdf_bp = Blueprint('pdf', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

CACHE_MGR = CacheManager()

# ============================================================================
# HELPER: Get seating from cache
# ============================================================================
def get_seating_from_cache(plan_id, room_no=None):
    """Retrieve seating data from cache"""
    try:
        snapshot = CACHE_MGR.load_snapshot(plan_id)
        if not snapshot:
            return None
        
        rooms = snapshot.get('rooms', {})
        
        if room_no:
            # Specific room requested
            room_data = rooms.get(room_no)
            if room_data:
                return {
                    'seating': room_data.get('raw_matrix', room_data.get('seating', [])),
                    'metadata': room_data.get('inputs', {}),
                    'batches': room_data.get('batches', {})
                }
            return None
        else:
            # Return first room if no specific room requested
            if rooms:
                first_room = list(rooms.keys())[0]
                room_data = rooms[first_room]
                return {
                    'seating': room_data.get('raw_matrix', room_data.get('seating', [])),
                    'metadata': room_data.get('inputs', {}),
                    'batches': room_data.get('batches', {})
                }
            
            # Fallback: maybe it's a direct structure
            if snapshot.get('seating') or snapshot.get('raw_matrix'):
                return {
                    'seating': snapshot.get('raw_matrix', snapshot.get('seating', [])),
                    'metadata': snapshot.get('metadata', snapshot.get('inputs', {})),
                    'batches': snapshot.get('batches', {})
                }
        
        return None
    except Exception as e:
        logger.error(f"Cache lookup error: {e}")
        return None

# ============================================================================
# HELPER: Get seating from Database (Fallback)
# ============================================================================
# ============================================================================
# HELPER: Get seating from Database (Fallback)
# ============================================================================
def get_seating_from_database(session_id, room_name=None):
    """Reconstruct seating data from database allocations"""
    try:
        from algo.database.db import get_db_connection
        import sqlite3
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # 1. Get classroom config
        if room_name:
            cur.execute("SELECT id, name, rows, cols, block_width, broken_seats FROM classrooms WHERE name = ?", (room_name,))
        else:
            # Fallback to first allocated room if no name provided
            cur.execute("""
                SELECT c.id, c.name, c.rows, c.cols, c.block_width, c.broken_seats
                FROM classrooms c
                JOIN allocations a ON c.id = a.classroom_id
                WHERE a.session_id = ?
                LIMIT 1
            """, (session_id,))
            
        classroom = cur.fetchone()
        if not classroom:
            conn.close()
            return None
            
        target_room_name = classroom['name']
        classroom_id = classroom['id']
        rows_count = classroom['rows']
        cols_count = classroom['cols']
        block_width = classroom['block_width']
        broken_seats_str = classroom['broken_seats'] or ""
        
        # 2. Get allocations for this room/session
        cur.execute("""
            SELECT 
                a.seat_position, a.enrollment, a.student_id,
                a.batch_name, a.paper_set, 
                s.name as student_name, s.batch_color
            FROM allocations a
            LEFT JOIN students s ON a.student_id = s.id
            WHERE a.session_id = ? AND a.classroom_id = ?
        """, (session_id, classroom_id))
        
        alloc_rows = cur.fetchall()
        conn.close()
        
        # 3. Reconstruct matrix
        matrix = [[None for _ in range(cols_count)] for _ in range(rows_count)]
        
        # Mark broken seats
        try:
            broken_list = [s.strip() for s in broken_seats_str.split(',') if s.strip()]
            for bs in broken_list:
                rr, cc = map(int, bs.split('-'))
                if 0 <= rr-1 < rows_count and 0 <= cc-1 < cols_count:
                    matrix[rr-1][cc-1] = {
                        'is_broken': True,
                        'display': 'BROKEN',
                        'color': '#FF0000',
                        'position': bs
                    }
        except: pass

        # Map allocations
        for r in alloc_rows:
            try:
                rr, cc = map(int, r['seat_position'].split('-'))
                if 0 <= rr-1 < rows_count and 0 <= cc-1 < cols_count:
                    matrix[rr-1][cc-1] = {
                        'position': r['seat_position'],
                        'roll_number': r['enrollment'],
                        'student_name': r['student_name'],
                        'batch_label': r['batch_name'],
                        'color': r['batch_color'] or '#F3F4F6',
                        'paper_set': r['paper_set'],
                        'status': 'allocated'
                    }
            except: continue
            
        # Fill rest as unallocated (if not broken)
        for r in range(rows_count):
            for c in range(cols_count):
                if matrix[r][c] is None:
                    matrix[r][c] = {
                        'is_unallocated': True,
                        'display': '',
                        'position': f"{r+1}-{c+1}",
                        'color': '#F3F4F6'
                    }

        return {
            'seating': matrix,
            'metadata': {
                'room_no': target_room_name,
                'rows': rows_count,
                'cols': cols_count,
                'block_width': block_width,
                'broken_seats': broken_seats_str
            },
            'batches': {}, # Re-built by CacheManager if needed, but not critical for PDF
            'source': 'database'
        }
        
    except Exception as e:
        logger.error(f"DB lookup error: {str(e)}")
        return None

# ============================================================================
# HELPER: Corrected 4-Step Hybrid Seating Data Retrieval
# ============================================================================
def get_seating_data_hybrid(data, user_id=None):
    """
    Unified 4-step retrieval mechanism:
    1. Check Cache (O(1)) via plan_id
    2. Check Session (O(1)) -> Get plan_id -> Try Cache
    3. reconstruct from Database (O(n))
    4. Use Request Payload
    """
    plan_id = data.get('plan_id') or data.get('snapshot_id')
    session_id = data.get('session_id')
    room_name = data.get('room_name') or data.get('room_no')
    
    # [1] Try Cache Directly
    if plan_id:
        logger.info(f"🔍 [Hybrid-Step 1] Checking cache for plan_id: {plan_id}")
        cached = get_seating_from_cache(plan_id, room_name)
        if cached:
            logger.info(f"⚡ [Hybrid HIT] Seating found in cache (Step 1)")
            return cached, "cache"
            
    # [2] Try Session -> Cache
    if session_id:
        logger.info(f"🔍 [Hybrid-Step 2] Checking session_id: {session_id}")
        try:
            from algo.database.db import get_db_connection
            conn = get_db_connection()
            cur = conn.cursor()
            if user_id:
                cur.execute("SELECT plan_id FROM allocation_sessions WHERE session_id = ? AND user_id = ?", (session_id, user_id))
            else:
                cur.execute("SELECT plan_id FROM allocation_sessions WHERE session_id = ?", (session_id,))
            row = cur.fetchone()
            conn.close()
            
            if row and row[0]:
                db_plan_id = row[0]
                logger.info(f"   ↳ Found plan_id: {db_plan_id}. Retrying cache...")
                cached = get_seating_from_cache(db_plan_id, room_name)
                if cached:
                    logger.info(f"⚡ [Hybrid HIT] Seating found in cache (Step 2)")
                    return cached, "cache"
        except Exception as e:
            logger.warning(f"Hybrid Step 2 warning: {e}")

    # [3] Fallback to Database Reconstruction
    if session_id:
        logger.info(f"⚠️ [Hybrid-Step 3] Cache missing. Falling back to DB reconstruction for session: {session_id}")
        db_seating = get_seating_from_database(session_id, room_name)
        if db_seating:
            return db_seating, "database"

    # [4] Use Request Payload
    if 'seating' in data:
        logger.info(f"📄 [Hybrid-Step 4] Using request payload seating data")
        return {
            'seating': data['seating'],
            'metadata': data.get('metadata', data.get('inputs', {})),
            'batches': data.get('batches', {})
        }, "request"

    return None, "none"

# ============================================================================
# POST /api/generate-pdf - Generate PDF from seating arrangement
# ============================================================================
@pdf_bp.route('/generate-pdf', methods=['POST'])
@token_required
def generate_pdf():
    """
    Generate PDF from seating arrangement.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = request.user_id
        
        # [STEP 1-3] Use Hybrid Seating Retrieval with ownership check
        seating_payload, seating_source = get_seating_data_hybrid(data, user_id=user_id)
        
        if not seating_payload or not seating_payload.get('seating'):
            return jsonify({
                "error": "No seating data available",
                "hint": "Ensure session is active or plan exists in cache"
            }), 400

        template_name = data.get('template_name', 'default')
        room_no = data.get('room_no') or data.get('room_name') or "Unknown"
        
        # ============================================================================
        # LAYER 2: PDF Generation - Let pdf_generation.py handle caching
        # ============================================================================
        logger.info(f"📋 [L1→L2] Passing to PDF generation: seating_source={seating_source}, user={user_id}, template={template_name}")
        
        try:
            from algo.pdf_gen.pdf_generation import get_or_create_seating_pdf
            
            pdf_path = get_or_create_seating_pdf(
                seating_payload,
                user_id=user_id,
                template_name=template_name
            )
        except Exception as pdf_err:
            logger.error(f"❌ PDF generation failed: {str(pdf_err)}")
            return jsonify({"error": f"PDF generation failed: {str(pdf_err)}"}), 500
        
        # Verify PDF exists
        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF file not created"}), 500
        
        # Generate filename
        meta_room = seating_payload.get('metadata', {}).get('room_no') or room_no or "Unknown"
        room_suffix = f"_{meta_room.replace(' ', '_')}" if meta_room else ""
        
        logger.info(f"✅ PDF ready: {pdf_path} (seating_source={seating_source})")
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"seating_plan{room_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"❌ PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============================================================================
# GET /api/plan-batches/<plan_id> - Get batch info for all rooms in a plan
# ============================================================================
@pdf_bp.route('/plan-batches/<plan_id>', methods=['GET'])
@token_required
def get_plan_batches(plan_id):
    """Get batch information for ALL rooms in a plan"""
    try:
        # Verify ownership of plan_id
        from algo.database.db import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM allocation_sessions WHERE plan_id = ?", (plan_id,))
        row = cur.fetchone()
        conn.close()
        
        if not row or row[0] != request.user_id:
            return jsonify({"error": "Unauthorized access to plan"}), 403

        cache_data = CACHE_MGR.load_snapshot(plan_id)
        
        if cache_data:
            # Return ALL rooms from cache
            all_rooms = cache_data.get('rooms', {})
            logger.info(f"📋 Plan {plan_id} found in CACHE with {len(all_rooms)} rooms")
        else:
            # Fallback to reconstructing from DB maybe?
            # For now, if not in cache, return error or empty
            return jsonify({"error": "Plan not found in cache"}), 404
            
        return jsonify({
            "plan_id": plan_id,
            "rooms": all_rooms,
            "metadata": cache_data.get('metadata', {}),
            "inputs": cache_data.get('inputs', {})
        })
        
    except Exception as e:
        logger.error(f"Error fetching plan batches: {e}")
        return jsonify({"error": str(e)}), 500
        import sqlite3
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get session info - filter by user_id
        cur.execute("SELECT session_id, total_students FROM allocation_sessions WHERE plan_id = ? AND user_id = ?", (plan_id, request.user_id))
        session_row = cur.fetchone()
        
        if not session_row:
            conn.close()
            return jsonify({"error": "Plan not found in cache or database"}), 404
            
        session_id = session_row['session_id']
        total_students = session_row['total_students']
        
        # Get batches linked to this session
        cur.execute("""
            SELECT DISTINCT batch_name, batch_color 
            FROM uploads 
            WHERE session_id = ?
        """, (session_id,))
        
        batches = []
        for b in cur.fetchall():
            batches.append({
                "name": b['batch_name'],
                "color": b['batch_color'] or "#3b82f6"
            })
            
        conn.close()
        
        return jsonify({
            "plan_id": plan_id,
            "rooms": {}, # No rooms yet if no cache
            "metadata": {
                "plan_id": plan_id,
                "total_students": total_students,
                "batches": batches
            },
            "inputs": {},
            "source": "database"
        })
        
    except Exception as e:
        logger.error(f"Get plan batches error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# POST /api/generate-pdf/batch - Batch PDF generation
# ============================================================================
@pdf_bp.route('/generate-pdf/batch', methods=['POST'])
@token_required
def generate_pdf_batch():
    """Generate PDFs for multiple rooms"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        plan_id = data.get('plan_id')
        room_names = data.get('rooms', [])
        
        if not plan_id:
            return jsonify({"error": "plan_id required"}), 400
        
        cache_data = CACHE_MGR.load_snapshot(plan_id)
        if not cache_data:
            return jsonify({"error": "Plan not found"}), 404
        
        all_rooms = cache_data.get('rooms', {})
        
        # If no specific rooms, use all
        if not room_names:
            room_names = list(all_rooms.keys())
        
        if not room_names:
            return jsonify({"error": "No rooms available"}), 400
        
        from algo.pdf_gen.pdf_generation import get_or_create_seating_pdf
        
        generated_files = []
        errors = []
        
        for room_name in room_names:
            # Use hybrid mechanism for each room in batch
            room_request = {**data, 'room_name': room_name}
            room_payload, room_source = get_seating_data_hybrid(room_request)
            
            if not room_payload:
                errors.append(f"Room '{room_name}' could not be retrieved")
                continue
            
            try:
                pdf_path = get_or_create_seating_pdf(
                    room_payload,
                    user_id=data.get('user_id', 'batch'),
                    template_name=data.get('template_name', 'default')
                )
                generated_files.append({
                    'room': room_name,
                    'path': pdf_path,
                    'filename': os.path.basename(pdf_path)
                })
            except Exception as e:
                errors.append(f"Room '{room_name}': {str(e)}")
        
        return jsonify({
            "success": True,
            "generated": len(generated_files),
            "files": generated_files,
            "errors": errors
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# Download PDF endpoint
# ============================================================================
@pdf_bp.route('/download-pdf/<filename>', methods=['GET'])
@token_required
def download_pdf(filename):
    """Serve the generated PDF"""
    import glob
    
    directory = os.path.abspath("algo/pdf_gen/seat_plan_generated")
    
    # Try direct path
    path = os.path.join(directory, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    
    # Try searching in subdirs
    found = glob.glob(os.path.join(directory, "**", filename), recursive=True)
    if found:
        return send_file(found[0], as_attachment=True)
    
    return jsonify({"error": "File not found"}), 404

# ============================================================================
# Template Management Routes
# ============================================================================
@pdf_bp.route('/template/config', methods=['GET'])
@token_required
def get_template_config():
    """Get user's current template configuration - LEGACY COMPATIBLE"""
    try:
        from algo.pdf_gen.template_manager import template_manager
        user_id = request.user_id
        template_name = request.args.get('template_name', 'default')
        config = template_manager.get_user_template(user_id, template_name)
        
        # Transform banner_image_path to relative URL for frontend
        if config and config.get('banner_image_path'):
            filename = os.path.basename(config['banner_image_path'])
            config['banner_image_path'] = f"/api/template/banner/{filename}"
            
        # LEGACY Format required by frontend
        template_hash = template_manager.get_template_hash(user_id, template_name)
        
        return jsonify({
            "success": True,
            "template": config,
            "template_hash": template_hash,
            "message": "Template loaded successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@pdf_bp.route('/template/config', methods=['POST'])
@token_required
def save_template_config():
    """Save user template configuration - Handles both JSON and FormData"""
    try:
        from algo.pdf_gen.template_manager import template_manager
        user_id = request.user_id
        
        # Support both JSON and multipart/form-data
        if request.content_type and 'multipart/form-data' in request.content_type:
            template_data = {
                'dept_name': request.form.get('dept_name', ''),
                'exam_details': request.form.get('exam_details', ''),
                'seating_plan_title': request.form.get('seating_plan_title', ''),
                'branch_text': request.form.get('branch_text', ''),
                'room_number': request.form.get('room_number', ''),
                'coordinator_name': request.form.get('coordinator_name', ''),
                'coordinator_title': request.form.get('coordinator_title', ''),
            }
            template_name = request.form.get('template_name', 'default')
            
            # Handle banner upload if nested in FormData
            if 'bannerImage' in request.files:
                file = request.files['bannerImage']
                banner_path = template_manager.save_user_banner(user_id, file, template_name)
                if banner_path:
                    template_data['banner_image_path'] = banner_path
        else:
            data = request.json or {}
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400
            template_name = data.get('template_name', 'default')
            template_data = data

        success = template_manager.save_user_template(user_id, template_data, template_name)
        
        if success:
            # Clean up old banners
            template_manager.delete_old_banners(user_id, keep_latest=3)
            
            # Legacy format
            updated_template = template_manager.get_user_template(user_id, template_name)
            
            # Transform banner_image_path to relative URL for frontend
            if updated_template and updated_template.get('banner_image_path'):
                fname = os.path.basename(updated_template['banner_image_path'])
                updated_template['banner_image_path'] = f"/api/template/banner/{fname}"
                
            new_hash = template_manager.get_template_hash(user_id, template_name)
            
            return jsonify({
                "success": True,
                "message": "Template saved successfully!",
                "template": updated_template,
                "template_hash": new_hash
            })
        return jsonify({"success": False, "error": "Failed to save template"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@pdf_bp.route('/template/banner', methods=['POST'])
@token_required
def upload_banner():
    try:
        from algo.pdf_gen.template_manager import template_manager
        if 'banner' not in request.files and 'bannerImage' not in request.files:
            return jsonify({"success": False, "error": "No file"}), 400
        
        file = request.files.get('banner') or request.files.get('bannerImage')
        user_id = request.user_id
        path = template_manager.save_user_banner(user_id, file)
        
        if path:
            # Return RELATIVE path for frontend
            filename = os.path.basename(path)
            relative_path = f"/api/template/banner/{filename}"
            return jsonify({"success": True, "path": relative_path})
        return jsonify({"success": False, "error": "Upload failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# POST /api/export-attendance - Generate attendance sheet PDF
# ============================================================================
@pdf_bp.route('/export-attendance', methods=['POST'])
@token_required
def export_attendance():
    """Export attendance sheet with correct metadata field mapping"""
    import io
    import time
    
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        batch_or_room = data.get('batch_name')
        target_batch_name = batch_or_room # Explicitly define for internal PDF logic
        frontend_metadata = data.get('metadata', {})
        room_no = frontend_metadata.get('room_no') or frontend_metadata.get('room_name')
        
        logger.info(f"📋 Attendance request: plan={plan_id}, batch_or_room={batch_or_room}, room_no={room_no}")
        
        # [STEP 1-3] Use Hybrid Seating Retrieval with ownership check
        seating_payload, source = get_seating_data_hybrid(data, user_id=request.user_id)
        
        if not seating_payload:
            return jsonify({
                "error": f"Seating data for '{batch_or_room}' not found",
                "available_rooms": list(rooms.keys()) if rooms else []
            }), 404
        
        # If cache hit gave us multi-room plan, we need to extract specific room data
        # but get_seating_data_hybrid(data) with room_no should handle that inside step 1/2.
        
        # Extract students and batches for attendance
        all_students = []
        batch_info = {}
        
        # Reconstruct students list from the matrix we got (hybrid result is normalized)
        matrix = seating_payload.get('seating', [])
        target_room_name = seating_payload.get('metadata', {}).get('room_no') or room_no
        
        # If it was a room-level payload:
        if isinstance(matrix, list) and len(matrix) > 0 and isinstance(matrix[0], list):
            for row in matrix:
                for seat in row:
                    if seat and not seat.get('is_broken') and not seat.get('is_unallocated'):
                        # If a specific batch was requested, filter by it
                        if batch_or_room and batch_or_room != target_room_name:
                             if seat.get('batch_label') == batch_or_room:
                                 all_students.append(seat)
                        else:
                            all_students.append(seat)
                            
        # If no students found from matrix, try searching the 'batches' object if present
        if not all_students and 'batches' in seating_payload:
            batches = seating_payload.get('batches', {})
            if batch_or_room in batches:
                all_students = batches[batch_or_room].get('students', [])
                batch_info = batches[batch_or_room].get('info', {})
            elif room_no in batches: # Fallback
                all_students = batches[room_no].get('students', [])
                batch_info = batches[room_no].get('info', {})
            else:
                # Get all students if batch_or_room matches room
                for b_name, b_data in batches.items():
                    all_students.extend(b_data.get('students', []))
                    if not batch_info: batch_info = b_data.get('info', {})
        
        if not all_students:
            return jsonify({
                "error": f"No students found for '{batch_or_room}'",
                "available_rooms": list(rooms.keys())
            }), 404
        
        # Map metadata to EXACT field names that create_attendance_pdf expects
        complete_metadata = {
            'exam_title': frontend_metadata.get('exam_title') or frontend_metadata.get('exam_name') or 'EXAMINATION-ATTENDANCE SHEET',
            'course_name': frontend_metadata.get('course_name') or frontend_metadata.get('department') or 'N/A',
            'course_code': frontend_metadata.get('course_code') or 'N/A',
            'date': frontend_metadata.get('date') or frontend_metadata.get('exam_date') or '',
            'time': frontend_metadata.get('time') or '',
            'year': frontend_metadata.get('year') or str(datetime.now().year),
            'room_no': target_room_name or room_no or 'N/A',
        }
        
        logger.info(f"📋 Generating attendance: room={target_room_name}, batch={target_batch_name}, students={len(all_students)}")
        
        # Generate PDF
        timestamp = int(time.time())
        safe_name = (target_batch_name or target_room_name or 'attendance').replace(' ', '_').replace('/', '-')
        temp_filename = f"temp_attendance_{safe_name}_{timestamp}.pdf"
        
        try:
            from algo.attendence_gen.attend_gen import create_attendance_pdf
            
            create_attendance_pdf(
                temp_filename,
                all_students,
                target_batch_name or target_room_name or 'All',
                complete_metadata,
                batch_info
            )
        except ImportError:
            return jsonify({"error": "Attendance PDF generation module not available"}), 500
        
        # Read and send
        return_data = io.BytesIO()
        with open(temp_filename, 'rb') as f:
            return_data.write(f.read())
        return_data.seek(0)
        
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        
        download_name = f"Attendance_{safe_name}_{complete_metadata['course_code']}_{timestamp}.pdf"
        
        logger.info(f"✅ Attendance PDF generated: {download_name}")
        
        return send_file(
            return_data,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        logger.error(f"❌ Export attendance error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
@pdf_bp.route('/test-pdf', methods=['GET'])
@token_required
def generate_test_pdf():
    """Generate a test PDF with sample data using current template"""
    try:
        user_id = request.user_id
        template_name = request.args.get('template_name', 'default')
        
        # Create sample student data
        sample_seating_matrix = [
            [
                {'roll_number': 'BTCS24001', 'name': 'Aarav Sharma', 'batch_label': 'Batch A', 'paper_set': 'A', 'color': '#e3f2fd'},
                {'roll_number': 'BTCS24002', 'name': 'Vivaan Verma', 'batch_label': 'Batch B', 'paper_set': 'B', 'color': '#f3e5f5'},
                {'roll_number': 'BTCS24003', 'name': 'Aditya Gupta', 'batch_label': 'Batch A', 'paper_set': 'A', 'color': '#e3f2fd'},
                {'roll_number': 'BTCS24004', 'name': 'Vihaan Kumar', 'batch_label': 'Batch B', 'paper_set': 'B', 'color': '#f3e5f5'}
            ],
            [
                {'roll_number': 'BTCS24005', 'name': 'Arjun Singh', 'batch_label': 'Batch A', 'paper_set': 'A', 'color': '#e3f2fd'},
                {'roll_number': 'BTCS24006', 'name': 'Aadhya Patel', 'batch_label': 'Batch B', 'paper_set': 'B', 'color': '#f3e5f5'},
                {'roll_number': 'BTCS24007', 'name': 'Ananya Reddy', 'batch_label': 'Batch A', 'paper_set': 'A', 'color': '#e3f2fd'},
                {'roll_number': 'BTCS24008', 'name': 'Pari Mehta', 'batch_label': 'Batch B', 'paper_set': 'B', 'color': '#f3e5f5'}
            ]
        ]

        seating_payload = {
            'seating': sample_seating_matrix,
            'metadata': {
                'rows': 2, 
                'cols': 4, 
                'blocks': 1,
                'total_students': 8,
                'room_no': 'TEST-101'
            }
        }
        
        from algo.pdf_gen.pdf_generation import get_or_create_seating_pdf
        pdf_path = get_or_create_seating_pdf(
            seating_payload,
            user_id=str(user_id),
            template_name=template_name
        )
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'test_seating_plan_{datetime.now().strftime("%H%M%S")}.pdf'
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating test PDF: {e}")
        return jsonify({"success": False, "error": f'Failed to generate test PDF: {str(e)}'}), 500

@pdf_bp.route('/template/banner/<path:filename>', methods=['GET'])
@token_required
def serve_banner_image(filename):
    """Serve uploaded banner images"""
    try:
        from algo.pdf_gen.template_manager import template_manager
        user_id = request.user_id
        user_folder = os.path.join(template_manager.upload_folder, str(user_id))
        file_path = os.path.join(user_folder, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            logger.warning(f"⚠️ Banner file not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        logger.error(f"❌ Error serving banner: {e}")
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/template/config', methods=['DELETE'])
@token_required
def reset_template_config():
    """Reset user's template to system default"""
    try:
        from algo.pdf_gen.template_manager import template_manager
        user_id = request.user_id
        template_name = request.args.get('template_name', 'default')
        
        # Get system default
        default_template = template_manager._get_default_template()
        
        # Save as user's template (reset)
        success = template_manager.save_user_template(user_id, default_template, template_name)
        
        if not success:
            return jsonify({
                "success": False,
                "error": "Failed to reset template"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "Template reset to default",
            "template": default_template
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Template reset error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
