import sys
import os
from datetime import datetime
import time
import io
import json
import sqlite3
from pathlib import Path
from functools import wraps
from typing import Dict, List, Tuple

from flask import Flask, jsonify, request, send_file, render_template_string, session, render_template
from flask_cors import CORS
from leftover_calculator import LeftoverCalculator

from pdf_gen.pdf_generation import get_or_create_seating_pdf
from pdf_gen.template_manager import template_manager

from cache_manager import CacheManager
from attendence_gen.attend_gen import create_attendance_pdf
cache_manager = CacheManager()
import uuid


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, "Backend")

if os.path.exists(BACKEND_DIR):
    sys.path.insert(0, BACKEND_DIR)
    print(f"✅ Added to path: {BACKEND_DIR}")

auth_signup = None
auth_login = None
verify_token = None
get_user_by_token = None
update_user_profile = None
google_auth_handler = None

try:
    from auth_service import (
        signup as auth_signup,
        login as auth_login,
        verify_token,
        get_user_by_token,
        update_user_profile,
        google_auth_handler
    )
    print("✅ Auth service imported successfully")
except ImportError as e:
    try:
        from algo.auth_service import (
            signup as auth_signup,
            login as auth_login,
            verify_token,
            get_user_by_token,
            update_user_profile,
            google_auth_handler
        )
        print("✅ Auth service imported successfully (from Backend package)")
    except ImportError as e2:
        print("\n" + "!" * 70)
        print("⚠️  WARNING: Auth module could not be imported")
        print(f"Error: {e2}")
        print("!" * 70 + "\n")

try:
    from pdf_gen import create_seating_pdf
    print("✅ PDF generation module loaded")
except ImportError:
    print("⚠️  PDF generation module not found")
    create_seating_pdf = None

try:
    from student_parser import StudentDataParser
    from algo import SeatingAlgorithm
    print("✅ Student parser and algorithm modules loaded")
except ImportError as e:
    print(f"⚠️  Warning: Could not import local modules: {e}")
    StudentDataParser = None
    SeatingAlgorithm = None

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "demo.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-prod')
app.config['FEEDBACK_FOLDER'] = BASE_DIR / "feedback_files"
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

# Attendence generation module import 
try:
    from attendence_gen.attend_gen import generate_attendance_pdf
    print("✅ Attendance PDF module loaded")
except ImportError:
    generate_attendance_pdf = None

# --------------------------------------------------
# CACHE LAYER: Pending Students Management
# --------------------------------------------------
class SessionCacheManager:
    """Manages session-specific data in cache (pending students, allocations)"""
    
    @staticmethod
    def save_pending_students(session_id, pending_students):
        """Save pending students list to cache"""
        cache_key = f"session_{session_id}_pending"
        file_path = cache_manager.get_file_path(cache_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump({
                "session_id": session_id,
                "pending_students": pending_students,
                "updated_at": datetime.now().isoformat()
            }, f, indent=2)
        print(f"✅ Cached {len(pending_students)} pending students for session {session_id}")
        return cache_key

    @staticmethod
    def get_pending_students_from_cache(session_id):
        """Get pending students from cache (fast path)"""
        cache_key = f"session_{session_id}_pending"
        file_path = cache_manager.get_file_path(cache_key)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    print(f"📦 Retrieved {len(data['pending_students'])} pending students from cache (session {session_id})")
                    return data['pending_students']
            except Exception as e:
                print(f"⚠️  Cache read error: {e}")
        
        print(f"⚠️  No cache found for session {session_id}, will query DB")
        return None

    @staticmethod
    def clear_session_cache(session_id):
        """Clear session cache after finalization"""
        cache_key = f"session_{session_id}_pending"
        file_path = cache_manager.get_file_path(cache_key)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Cleared cache for session {session_id}")

    @staticmethod
    def save_room_allocation_cache(session_id, classroom_id, allocated_enrollments):
        """Save list of students allocated to a room"""
        cache_key = f"session_{session_id}_room_{classroom_id}_allocated"
        file_path = cache_manager.get_file_path(cache_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump({
                "session_id": session_id,
                "classroom_id": classroom_id,
                "allocated_enrollments": allocated_enrollments,
                "count": len(allocated_enrollments),
                "allocated_at": datetime.now().isoformat()
            }, f, indent=2)
        print(f"✅ Cached {len(allocated_enrollments)} allocations for room {classroom_id} in session {session_id}")

session_cache = SessionCacheManager()

# --------------------------------------------------
# Enhanced DB Bootstrap with Session Tables
# --------------------------------------------------
def ensure_demo_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Classroom Registry
    cur.execute("""
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            rows INTEGER NOT NULL,
            cols INTEGER NOT NULL,
            broken_seats TEXT,
            block_width INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT UNIQUE,
            batch_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id INTEGER,
            batch_id TEXT,
            batch_name TEXT,
            enrollment TEXT NOT NULL,
            name TEXT,
            inserted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(upload_id, enrollment)
        );
    """)

    # 2. NEW: Allocation Sessions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS allocation_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            status TEXT CHECK(status IN ('active', 'completed', 'archived')) DEFAULT 'active',
            total_students INTEGER,
            total_allocated INTEGER DEFAULT 0
        );
    """)

    # 3. NEW: Session-File Mapping
    cur.execute("""
        CREATE TABLE IF NOT EXISTS session_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            upload_id INTEGER NOT NULL,
            FOREIGN KEY (session_id) REFERENCES allocation_sessions(session_id),
            FOREIGN KEY (upload_id) REFERENCES uploads(id),
            UNIQUE(session_id, upload_id)
        );
    """)

    # 4. NEW: Classroom-Level Allocations
    cur.execute("""
        CREATE TABLE IF NOT EXISTS classroom_allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            classroom_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            enrollment TEXT NOT NULL,
            seat_position TEXT,
            allocation_status TEXT CHECK(allocation_status IN ('allocated', 'pending', 'overflow')) DEFAULT 'pending',
            allocated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES allocation_sessions(session_id),
            FOREIGN KEY (classroom_id) REFERENCES classrooms(id),
            FOREIGN KEY (student_id) REFERENCES students(id),
            UNIQUE(session_id, student_id, classroom_id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            upload_id INTEGER,
            enrollment TEXT,
            room_id TEXT,
            seat_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            issue_type TEXT NOT NULL,
            priority TEXT NOT NULL,
            description TEXT NOT NULL,
            feature_suggestion TEXT,
            additional_info TEXT,
            file_path TEXT,
            file_name TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at DATETIME,
            admin_response TEXT
        );
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")

# --------------------------------------------------
# Session Management with Cache Integration
# --------------------------------------------------

def create_allocation_session(plan_id, upload_ids, total_students):
    """Create new allocation session and CACHE initial pending students"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO allocation_sessions (plan_id, total_students, status) VALUES (?, ?, 'active')",
            (plan_id, total_students)
        )
        session_id = cur.lastrowid
        
        # Link uploaded files
        for upload_id in upload_ids:
            cur.execute(
                "INSERT INTO session_files (session_id, upload_id) VALUES (?, ?)",
                (session_id, upload_id)
            )
        
        conn.commit()
        
        # IMMEDIATELY fetch and CACHE all pending students from DB
       # IMMEDIATELY fetch and CACHE all pending students from DB
        cur.execute("""
            SELECT DISTINCT s.id, s.enrollment, s.name, s.batch_name, s.batch_id
            FROM students s
            JOIN session_files sf ON s.upload_id = sf.upload_id
            WHERE sf.session_id = ?
            ORDER BY s.enrollment
        """, (session_id,))
        
        pending = [dict((cur.description[i][0], row[i]) for i in range(len(cur.description))) for row in cur.fetchall()]
        
        # CACHE pending students aggressively
        session_cache.save_pending_students(session_id, pending)
        
        print(f"✅ Created session {session_id} with {len(pending)} pending students (cached)")
        return session_id
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_pending_students(session_id, use_cache=True):
    """
    AGGRESSIVE CACHE STRATEGY:
    1. Try cache FIRST (fast)
    2. Fall back to DB only if cache miss
    3. Update cache on every change
    """
    if use_cache:
        # FAST PATH: Check cache first
        cached = session_cache.get_pending_students_from_cache(session_id)
        if cached is not None:
            return cached
    
    # SLOW PATH: Query DB only if cache miss
    print(f"⚠️  Cache miss for session {session_id}, querying DB...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT DISTINCT s.id, s.enrollment, s.name, s.batch_name, s.batch_id
            FROM students s
            WHERE s.id NOT IN (
                SELECT student_id FROM classroom_allocations 
                WHERE session_id = ? AND allocation_status = 'allocated'
            )
            AND s.id IN (
                SELECT DISTINCT st.id
                FROM students st
                JOIN session_files sf ON st.id IN (
                    SELECT st2.id FROM students st2 
                    WHERE st2.upload_id IN (SELECT upload_id FROM session_files WHERE session_id = ?)
                )
            )
            ORDER BY s.enrollment
        """, (session_id, session_id))
        
        pending = [dict(row) for row in cur.fetchall()]
        
        # UPDATE cache after DB query
        session_cache.save_pending_students(session_id, pending)
        
        return pending
    except Exception as e:
        print(f"❌ Error fetching pending students: {e}")
        return []
    finally:
        conn.close()

def save_room_allocation(session_id, classroom_id, seating_data):
    """
    Save room allocation, update cache with remaining pending students
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    allocated_enrollments = []
    
    try:
        # Extract allocated students from seating
        for row in seating_data.get('seating', []):
            for seat in row:
                if seat and not seat.get('is_broken') and not seat.get('is_unallocated'):
                    enrollment = seat.get('roll_number')
                    allocated_enrollments.append(enrollment)
                    
                    # Find and update student in DB
                    cur.execute("SELECT id FROM students WHERE enrollment = ?", (enrollment,))
                    student_row = cur.fetchone()
                    if student_row:
                        student_id = student_row[0]
                        seat_pos = f"{seat.get('row', '')}-{seat.get('col', '')}"
                        
                        cur.execute("""
                            INSERT OR REPLACE INTO classroom_allocations 
                            (session_id, classroom_id, student_id, enrollment, seat_position, allocation_status)
                            VALUES (?, ?, ?, ?, ?, 'allocated')
                        """, (session_id, classroom_id, student_id, enrollment, seat_pos))
        
        # Update session total
        cur.execute("""
            UPDATE allocation_sessions 
            SET total_allocated = total_allocated + ?
            WHERE session_id = ?
        """, (len(allocated_enrollments), session_id))
        
        conn.commit()
        
        # CACHE the room allocation
        session_cache.save_room_allocation_cache(session_id, classroom_id, allocated_enrollments)
        
        # GET UPDATED pending from DB and CACHE it
        pending = get_pending_students(session_id, use_cache=False)
        
        print(f"✅ Saved {len(allocated_enrollments)} allocations for room {classroom_id}")
        print(f"📦 Updated cache with {len(pending)} remaining pending students")
        
        return len(allocated_enrollments), pending
    except Exception as e:
        print(f"❌ Error saving room allocation: {e}")
        conn.rollback()
        return 0, []
    finally:
        conn.close()

def finalize_session(session_id, plan_id):
    """Mark session complete and CLEAR cache"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE allocation_sessions 
            SET status = 'completed', completed_at = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        
        conn.commit()
        
        # CLEAR all session caches
        session_cache.clear_session_cache(session_id)
        
        print(f"✅ Finalized session {session_id} and cleared cache")
        return True
    except Exception as e:
        print(f"❌ Error finalizing session: {e}")
        return False
    finally:
        conn.close()

# --------------------------------------------------
# API ENDPOINTS: Session Management
# --------------------------------------------------

@app.route("/api/create-session", methods=["POST"])
def create_session_endpoint():
    """Create new allocation session with cache initialization"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        upload_ids = data.get('upload_ids', [])
        total_students = data.get('total_students', 0)
        
        if not plan_id or not upload_ids:
            return jsonify({"error": "Missing plan_id or upload_ids"}), 400
        
        session_id = create_allocation_session(plan_id, upload_ids, total_students)
        
        if not session_id:
            return jsonify({"error": "Failed to create session"}), 500
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "plan_id": plan_id,
            "total_students": total_students,
            "cache_status": "initialized"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pending-students/<int:session_id>", methods=["GET"])
def get_pending_students_endpoint(session_id):
    """Get pending students (uses CACHE first)"""
    try:
        use_cache = request.args.get('cache', 'true').lower() == 'true'
        pending = get_pending_students(session_id, use_cache=use_cache)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "pending_count": len(pending),
            "pending_students": pending
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/save-room-allocation", methods=["POST"])
def save_room_allocation_endpoint():
    """Save room allocation and UPDATE cache with pending students"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        classroom_id = data.get('classroom_id')
        seating_data = data.get('seating_data')
        
        if not all([session_id, classroom_id, seating_data]):
            return jsonify({"error": "Missing required fields"}), 400
        
        allocated, pending = save_room_allocation(session_id, classroom_id, seating_data)
        
        return jsonify({
            "success": True,
            "allocated_count": allocated,
            "pending_count": len(pending),
            "pending_students": pending,
            "cache_updated": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/finalize-session", methods=["POST"])
def finalize_session_endpoint():
    """Finalize session and CLEAR cache"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        plan_id = data.get('plan_id')
        
        if not session_id or not plan_id:
            return jsonify({"error": "Missing session_id or plan_id"}), 400
        
        # Verify no pending
        pending = get_pending_students(session_id)
        if pending:
            return jsonify({
                "error": f"Cannot finalize: {len(pending)} students still pending"
            }), 400
        
        success = finalize_session(session_id, plan_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Session finalized and cache cleared",
                "session_id": session_id,
                "plan_id": plan_id
            })
        else:
            return jsonify({"error": "Failed to finalize session"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/session-status/<int:session_id>", methods=["GET"])
def get_session_status(session_id):
    """Get session status with cache stats"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT session_id, plan_id, status, total_students, total_allocated, created_at
            FROM allocation_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        session_row = cur.fetchone()
        if not session_row:
            conn.close()
            return jsonify({"error": "Session not found"}), 404
        
        session_data = dict(session_row)
        pending = get_pending_students(session_id, use_cache=True)
        
        conn.close()
        
        return jsonify({
            "success": True,
            "session": session_data,
            "total_allocated": session_data['total_allocated'],
            "total_students": session_data['total_students'],
            "pending_count": len(pending),
            "cache_hit": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------
# Keep all existing endpoints from original app.py
# --------------------------------------------------



ensure_demo_db()

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def parse_int_dict(val):
    if isinstance(val, dict): 
        return {int(k): int(v) for k, v in val.items()}
    if isinstance(val, str) and val:
        try: 
            return json.loads(val)
        except: 
            pass
    return {}

def parse_str_dict(val):
    if isinstance(val, dict): 
        return {int(k): str(v) for k, v in val.items()}
    if isinstance(val, str) and val:
        try: 
            return json.loads(val)
        except: 
            pass
    return {}

def get_batch_counts_and_labels_from_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT batch_name, COUNT(*) FROM students GROUP BY batch_name ORDER BY batch_name")
    rows = cur.fetchall()
    conn.close()
    counts, labels = {}, {}
    for i, (name, count) in enumerate(rows, start=1):
        counts[i] = count
        labels[i] = name
    return counts, labels

def get_batch_roll_numbers_from_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # 1. Fetch all three necessary columns
    cur.execute("SELECT batch_name, enrollment, name FROM students ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    
    groups = {}
    # 2. Correctly unpack all three values from the row
    for batch_name, enr, name in rows:
        # 3. Store as a dictionary so algo.py can access both roll and name
        groups.setdefault(batch_name, []).append({
            "roll": enr,
            "name": name if name else ""  # Handle empty names safely
        })
        
        
    # 4. Return the integer-mapped dictionary required by the Algorithm
    return {i + 1: groups[k] for i, k in enumerate(sorted(groups))}
# --------------------------------------------------
# Auth Decorator
# --------------------------------------------------
def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if verify_token is None: 
            return jsonify({"error": "Auth module not available"}), 501
        
        auth = request.headers.get("Authorization")
        if not auth: 
            return jsonify({"error": "Token missing"}), 401
        
        try:
            token = auth.split(" ")[1]
        except IndexError:
            return jsonify({"error": "Invalid authorization header"}), 401
            
        payload = verify_token(token)
        if not payload: 
            return jsonify({"error": "Invalid or expired token"}), 401
        
        request.user_id = payload.get("user_id")
        return fn(*args, **kwargs)
    return wrapper
# FEEDBACK ROUTES
# --------------------------------------------------

@app.route("/api/feedback", methods=["POST"])
@token_required
def submit_feedback():
    """Submit new feedback"""
    try:
        issue_type = request.form.get('issueType')
        priority = request.form.get('priority')
        description = request.form.get('description')
        feature_suggestion = request.form.get('featureSuggestion', '')
        additional_info = request.form.get('additionalInfo', '')
        
        if not all([issue_type, priority, description]):
            return jsonify({"error": "Missing required fields"}), 400
        
        file_path = None
        file_name = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                try:
                    app.config['FEEDBACK_FOLDER'].mkdir(exist_ok=True, parents=True)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    safe_filename = f"{timestamp}_{file.filename}"
                    file_path = app.config['FEEDBACK_FOLDER'] / safe_filename
                    file.save(str(file_path))
                    file_name = file.filename
                    print(f"✅ Feedback file saved: {file_path}")
                except Exception as file_error:
                    print(f"⚠️  File upload error: {file_error}")
                    file_path = None
                    file_name = None
        
        # Ensure user_id is available
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            print("⚠️  Warning: user_id not set by token_required decorator")
            user_id = 1  # Default for testing
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO feedback (
                user_id, issue_type, priority, description, 
                feature_suggestion, additional_info, file_path, file_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, issue_type, priority, description,
            feature_suggestion, additional_info,
            str(file_path) if file_path else None, file_name
        ))
        feedback_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Feedback submitted successfully: ID={feedback_id}, User={user_id}")
        
        return jsonify({
            "success": True, 
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id
        }), 201
        
    except Exception as e:
        print(f"❌ Error in submit_feedback: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/feedback", methods=["GET"])
@token_required
def get_user_feedback():
    """Get all feedback submitted by the current user"""
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({"error": "User not authenticated"}), 401
            
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, issue_type, priority, description, 
                   feature_suggestion, additional_info, file_name,
                   status, created_at, resolved_at, admin_response
            FROM feedback 
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        feedback_list = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        print(f"✅ Retrieved {len(feedback_list)} feedback records for user {user_id}")
        
        return jsonify({
            "success": True,
            "feedback": feedback_list
        })
        
    except Exception as e:
        print(f"❌ Error in get_user_feedback: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback/<int:feedback_id>", methods=["GET"])
@token_required
def get_feedback_detail(feedback_id):
    """Get detailed feedback by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM feedback 
            WHERE id = ? AND user_id = ?
        """, (feedback_id, request.user_id))
        
        row = cur.fetchone()
        conn.close()
        
        if not row:
            return jsonify({"error": "Feedback not found"}), 404
        
        return jsonify({
            "success": True,
            "feedback": dict(row)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback/<int:feedback_id>/file", methods=["GET"])
@token_required
def download_feedback_file(feedback_id):
    """Download attached file from feedback"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT file_path, file_name FROM feedback 
            WHERE id = ? AND user_id = ?
        """, (feedback_id, request.user_id))
        
        row = cur.fetchone()
        conn.close()
        
        if not row or not row['file_path']:
            return jsonify({"error": "File not found"}), 404
        
        file_path = Path(row['file_path'])
        if not file_path.exists():
            return jsonify({"error": "File no longer exists"}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=row['file_name']
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# ADMIN ROUTES
# --------------------------------------------------

@app.route("/api/admin/feedback", methods=["GET"])
@token_required
def get_all_feedback():
    """Get all feedback (admin only)"""
    try:
        status = request.args.get('status', None)
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        if status:
            cur.execute("""
                SELECT f.*, u.username, u.email 
                FROM feedback f
                LEFT JOIN users u ON f.user_id = u.id
                WHERE f.status = ?
                ORDER BY f.created_at DESC
            """, (status,))
        else:
            cur.execute("""
                SELECT f.*, u.username, u.email 
                FROM feedback f
                LEFT JOIN users u ON f.user_id = u.id
                ORDER BY f.created_at DESC
            """)
        
        feedback_list = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return jsonify({
            "success": True,
            "feedback": feedback_list
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/feedback/<int:feedback_id>/resolve", methods=["PUT"])
@token_required
def resolve_feedback(feedback_id):
    """Mark feedback as resolved (admin only)"""
    try:
        data = request.get_json()
        admin_response = data.get('adminResponse', '')
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE feedback 
            SET status = 'resolved',
                resolved_at = CURRENT_TIMESTAMP,
                admin_response = ?
            WHERE id = ?
        """, (admin_response, feedback_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Feedback marked as resolved"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/feedback/<int:feedback_id>", methods=["DELETE"])
@token_required
def delete_feedback(feedback_id):
    """Delete feedback (admin only)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("SELECT file_path FROM feedback WHERE id = ?", (feedback_id,))
        row = cur.fetchone()
        
        if row and row[0]:
            file_path = Path(row[0])
            if file_path.exists():
                file_path.unlink()
        
        cur.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Feedback deleted successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------
# 7. API ROUTES: CLASSROOMS
# --------------------------------------------------
@app.route("/api/classrooms", methods=["GET"])
def get_classrooms():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM classrooms ORDER BY name ASC")
    rooms = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rooms)

@app.route("/api/classrooms", methods=["POST"])
def save_classroom():
    data = request.get_json()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT OR REPLACE INTO classrooms (id, name, rows, cols, broken_seats, block_width)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data.get('id'), data['name'], data['rows'], data['cols'], 
              data.get('broken_seats', ''), data.get('block_width', 1)))
        conn.commit()
        return jsonify({"success": True, "message": "Classroom saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route("/api/classrooms/<int:room_id>", methods=["DELETE"])
def delete_classroom(room_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM classrooms WHERE id = ?", (room_id,))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# --------------------------------------------------
# AUTH ROUTES
# --------------------------------------------------
@app.route("/api/auth/signup", methods=["POST"])
def signup_route():
    if auth_signup is None: 
        return jsonify({"error": "Auth module not available"}), 501
    
    data = request.get_json(force=True)
    ok, msg = auth_signup(
        data.get("username"),
        data.get("email"),
        data.get("password"),
        data.get("role", "STUDENT"),
    )
    return jsonify({"success": ok, "message": msg}), 201 if ok else 400

@app.route("/api/auth/login", methods=["POST"])
def login_route():
    if auth_login is None: 
        return jsonify({"error": "Auth module not available"}), 501
    
    data = request.get_json(force=True)
    ok, user, token = auth_login(data.get("email"), data.get("password"))
    if not ok:
        return jsonify({"error": token}), 401
    return jsonify({"token": token, "user": user})

# ============================================================================
# GOOGLE AUTH ROUTE (NEW)
# ============================================================================
@app.route("/api/auth/google", methods=["POST"])
def google_auth_route():
    """Handle Google OAuth token and create/update user"""
    if google_auth_handler is None:
        return jsonify({"error": "Google auth not available"}), 501
    
    data = request.get_json(force=True)
    token = data.get("token")
    
    if not token:
        return jsonify({"error": "No token provided"}), 400
    
    ok, user, auth_token = google_auth_handler(token)
    if not ok:
        return jsonify({"error": user}), 401
    
    return jsonify({"token": auth_token, "user": user})

@app.route("/api/auth/profile", methods=["GET"])
@token_required
def get_profile_route():
    if get_user_by_token is None: 
        return jsonify({"error": "Auth module not available"}), 501
    
    auth_header = request.headers.get("Authorization")
    if not auth_header: 
        return jsonify({"error": "Missing token"}), 401
    
    try:
        token = auth_header.split(" ")[1]
        user = get_user_by_token(token)
        
        if not user:
            return jsonify({"error": "User not found or token invalid"}), 404
            
        return jsonify({"success": True, "user": user})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/auth/profile", methods=["PUT"])
@token_required
def update_profile_route():
    if update_user_profile is None: 
        return jsonify({"error": "Auth module not available"}), 501
    
    data = request.get_json(force=True)
    username = data.get("username")
    email = data.get("email")
    
    ok, msg = update_user_profile(request.user_id, username, email)
    
    if ok:
        user = get_user_by_token(request.headers.get("Authorization").split(" ")[1])
        return jsonify({"success": True, "message": msg, "user": user})
    else:
        return jsonify({"success": False, "error": msg}), 400

@app.route("/api/auth/logout", methods=["POST"])
def logout_route():
    return jsonify({"success": True, "message": "Logged out successfully"})

# --------------------------------------------------
# Upload Routes
# --------------------------------------------------
@app.route("/api/upload-preview", methods=["POST"])
def api_upload_preview():
    try:
        if "file" not in request.files: 
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == '': 
            return jsonify({"error": "No file selected"}), 400
        
        if StudentDataParser is None:
            return jsonify({"error": "Parser module not available"}), 500
        
        file_content = file.read()
        parser = StudentDataParser()
        preview_data = parser.preview(io.BytesIO(file_content), max_rows=10)
        
        return jsonify({"success": True, **preview_data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/upload", methods=["POST"])
def api_upload():
    try:
        if "file" not in request.files: 
            return jsonify({"error": "No file"}), 400
        
        if StudentDataParser is None:
            return jsonify({"error": "Parser module not available"}), 500
        
        file = request.files["file"]
        mode = int(request.form.get("mode", 2))
        batch_name = request.form.get("batch_name", "BATCH1")
        name_col = request.form.get("nameColumn", None)
        enrollment_col = request.form.get("enrollmentColumn", None)
        
        file_content = file.read()
        parser = StudentDataParser()
        pr = parser.parse_file(
            io.BytesIO(file_content),
            mode=mode, 
            batch_name=batch_name,
            name_col=name_col, 
            enrollment_col=enrollment_col
        )
        
        if not hasattr(app, 'config'): 
            app.config = {}
        if 'UPLOAD_CACHE' not in app.config: 
            app.config['UPLOAD_CACHE'] = {}
        
        app.config['UPLOAD_CACHE'][pr.batch_id] = pr
        
        return jsonify({
            "success": True,
            "batch_id": pr.batch_id,
            "batch_name": pr.batch_name,
            "rows_extracted": pr.rows_extracted,
            "sample": pr.data[pr.batch_name][:10],
            "preview": {
                "columns": list(pr.data[pr.batch_name][0].keys()) if pr.mode == 2 and pr.data[pr.batch_name] else [],
                "totalRows": pr.rows_total,
                "extractedRows": pr.rows_extracted
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/commit-upload", methods=["POST"])
def commit_upload():
    try:
        body = request.get_json(force=True)
        batch_id = body.get("batch_id")
        cache = app.config.get("UPLOAD_CACHE", {})
        pr = cache.get(batch_id)
        
        if not pr: 
            return jsonify({"error": "Preview expired or not found"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO uploads (batch_id, batch_name) VALUES (?, ?)", 
            (pr.batch_id, pr.batch_name)
        )
        upload_id = cur.lastrowid
        
        inserted, skipped = 0, 0
        for row in pr.data[pr.batch_name]:
            enr = row.get("enrollmentNo") if isinstance(row, dict) else str(row)
            name = row.get("name") if isinstance(row, dict) else None
            
            if not enr: 
                skipped += 1
                continue
            
            try:
                cur.execute(
                    "INSERT INTO students (upload_id, batch_id, batch_name, enrollment, name) VALUES (?, ?, ?, ?, ?)", 
                    (upload_id, pr.batch_id, pr.batch_name, enr, name)
                )
                inserted += 1
            except sqlite3.IntegrityError:
                skipped += 1
        
        conn.commit()
        conn.close()
        
        if batch_id in app.config['UPLOAD_CACHE']: 
            del app.config['UPLOAD_CACHE'][batch_id]
        
        return jsonify({"success": True, "inserted": inserted, "skipped": skipped})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------
# Data Access
# --------------------------------------------------
@app.route("/api/students", methods=["GET"])
def api_students():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC LIMIT 1000")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

# --------------------------------------------------
# Allocation Routes (Permanent ID Logic)
# --------------------------------------------------

@app.route("/api/generate-seating", methods=["POST"])
def generate_seating():
    if SeatingAlgorithm is None:
        return jsonify({"error": "SeatingAlgorithm module not available"}), 500
    
    data = request.get_json(force=True)
    
    # --- PERMANENT ID LOGIC ---
    # 1. Determine the Plan ID
    plan_id = data.get("plan_id")
    is_new_plan = False

    if not plan_id:
        # Generate a fresh ID only if one wasn't provided
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        is_new_plan = True
    
    # 2. Extract settings for the Algorithm
    use_db = bool(data.get("use_demo_db", True))
    if use_db:
        counts, labels = get_batch_counts_and_labels_from_db()
        rolls = get_batch_roll_numbers_from_db()
        num_batches = len(counts)
    else:
        counts = parse_int_dict(data.get("batch_student_counts"))
        labels = parse_str_dict(data.get("batch_labels"))
        rolls = data.get("batch_roll_numbers") or {}
        num_batches = int(data.get("num_batches", 3))

    # Parse broken seats
    broken_str = data.get("broken_seats", "")
    broken_seats = []
    if isinstance(broken_str, str) and "-" in broken_str:
        broken_seats = [(int(r)-1, int(c)-1) for r, c in (p.split("-") for p in broken_str.split(",") if "-" in p)]
    elif isinstance(broken_str, list):
        broken_seats = broken_str 

    # 3. Run the Algorithm
    # We pass all configuration data to the algorithm
    algo = SeatingAlgorithm(
        rows=int(data.get("rows", 10)),
        cols=int(data.get("cols", 6)),
        num_batches=num_batches,
        block_width=int(data.get("block_width", 2)),
        batch_by_column=bool(data.get("batch_by_column", True)),
        enforce_no_adjacent_batches=bool(data.get("enforce_no_adjacent_batches", False)),
        broken_seats=broken_seats,
        batch_student_counts=counts,
        batch_roll_numbers=rolls,
        batch_labels=labels,
        start_rolls=parse_str_dict(data.get("start_rolls")),
        batch_colors=parse_str_dict(data.get("batch_colors")),
        serial_mode=data.get("serial_mode", "per_batch"),
        serial_width=int(data.get("serial_width", 0))
    )

    algo.generate_seating()
    web = algo.to_web_format()
    
    # 4. Finalize response object
    web.setdefault("metadata", {})
    # Crucial: Send the ID back so the Frontend can include it in the next request
    web["plan_id"] = plan_id  
    
    ok, errors = algo.validate_constraints()
    web["validation"] = {"is_valid": ok, "errors": errors}
    
    # 5. OVERWRITE CACHE: This ensures we update the SAME file
    # Using save_or_update prevents duplication in the /cache folder
    cache_manager.save_or_update(plan_id, data, web)
    
    action_type = "Created" if is_new_plan else "Updated"
    print(f"💾 {action_type} plan: {plan_id} (Cache Overwritten)")

    return jsonify(web)

@app.route("/api/constraints-status", methods=["POST"])
def constraints_status():
    """Remains dynamic for real-time UI feedback (not cached)"""
    if SeatingAlgorithm is None: 
        return jsonify({"error": "Algorithm module not available"}), 500
    
    data = request.get_json(force=True)
    algo = SeatingAlgorithm(
        rows=int(data.get("rows", 10)),
        cols=int(data.get("cols", 6)),
        num_batches=int(data.get("num_batches", 3)),
        block_width=int(data.get("block_width", 2)),
        batch_by_column=bool(data.get("batch_by_column", True)),
        enforce_no_adjacent_batches=bool(data.get("enforce_no_adjacent_batches", False))
    )
    algo.generate_seating()
    return jsonify(algo.get_constraints_status())
# ============================================================================
# PDF GENERATION
# ============================================================================
@app.route('/template-editor')
def template_editor():
    """Serve the template editor interface"""
    return render_template('template_editor.html')
    # Since we changed Flask configuration, if 'template_editor.html'
    # is still a separate file, you should ensure it is in the 'templates' folder
    # or handle it as part of the React build. 
    # If the TemplateEditor is a React component, this route should also use render_template('index.html')
    # and let React Router handle the /template-editor path.

@app.route('/api/template-config', methods=['GET', 'POST'])
def manage_template():
    user_id = 'test_user'
    template_name = request.args.get('template_name', 'default')
    
    if request.method == 'GET':
        try:
            template = template_manager.get_user_template(user_id, template_name)
            return jsonify({
                'success': True,
                'template': template,
                'user_id': user_id
            })
        except Exception as e:
            return jsonify({'error': f'Failed to load template: {str(e)}'}), 500
    
    elif request.method == 'POST':
        try:
            template_data = request.form.to_dict()
            
            if 'bannerImage' in request.files:
                file = request.files['bannerImage']
                if file and file.filename:
                    image_path = template_manager.save_user_banner(user_id, file, template_name)
                    if image_path:
                        template_data['banner_image_path'] = image_path
            
            template_manager.save_user_template(user_id, template_data, template_name)
            
            return jsonify({
                'success': True,
                'message': 'Template updated successfully',
                'template': template_manager.get_user_template(user_id, template_name)
            })
            
        except Exception as e:
            return jsonify({'error': f'Failed to update template: {str(e)}'}), 500
# ============================================================================
# FIXED PDF GENERATION (Snapshot-Aware)
# ============================================================================

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # 1. Try to load from Central Cache if a snapshot_id is provided
        # This ensures the PDF exactly matches what was generated by the algo
        snapshot_id = data.get('snapshot_id')
        
        if snapshot_id:
            snapshot = cache_manager.load_snapshot(snapshot_id)
            if snapshot:
                seating_payload = snapshot['seating_data']
                print(f"📄 Generating PDF from Snapshot: {snapshot_id}")
            else:
                return jsonify({"error": "Cached snapshot not found. Please regenerate seating."}), 404
        else:
            # Fallback for direct data sends (like from your frontend preview)
            if 'seating' not in data:
                return jsonify({"error": "Invalid seating data"}), 400
            seating_payload = data
            print("📄 Generating PDF from raw request data")

        user_id = 'test_user'
        template_name = request.args.get('template_name', 'default')
        
        # 2. Call the generator with the validated payload
        pdf_path = get_or_create_seating_pdf(
            seating_payload, 
            user_id=user_id, 
            template_name=template_name
        )
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"seating_plan_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        )
    except Exception as e:
        print(f"❌ PDF Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-pdf', methods=['GET'])
def test_pdf():
    """Generates a sample PDF to verify the generator and template system work."""
    user_id = 'test_user'
    template_name = request.args.get('template_name', 'default')
    
    sample_data = {
        'seating': [
            [
                {'roll_number': '2021001', 'paper_set': 'A', 'color': '#e3f2fd'},
                {'roll_number': '2021002', 'paper_set': 'B', 'color': '#f3e5f5'},
                {'roll_number': '2021003', 'paper_set': 'A', 'color': '#e8f5e8'}
            ],
            [
                {'roll_number': '2021004', 'paper_set': 'B', 'color': '#fff3e0'},
                {'is_broken': True, 'display': 'BROKEN', 'color': '#ffebee'},
                {'roll_number': '2021005', 'paper_set': 'A', 'color': '#e3f2fd'}
            ]
        ],
        'metadata': {'rows': 2, 'cols': 3, 'blocks': 1, 'block_width': 3}
    }
    
    try:
        # Note: We don't cache test PDFs to avoid cluttering the system
        pdf_path = get_or_create_seating_pdf(sample_data, user_id=user_id, template_name=template_name)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"test_seating_plan.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ============================================================================
# ATTENDANCE GENERATION & ALLOCATIONS
# ============================================================================

@app.route('/api/allocations', methods=['GET'])
def get_all_allocations():
    """Fetches list of previous uploads/plans for the frontend to select from"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT batch_id, batch_name, created_at FROM uploads")
        rows = cur.fetchall()
        conn.close()
        return jsonify([{"id": r[0], "batch_name": r[1], "date": r[2]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/plan-batches/<plan_id>', methods=['GET'])
def get_plan_batches(plan_id):
    """
    NEW: This route helps the frontend 'Attendance Page' know 
    which batches exist in a plan so it can render the forms.
    """
    cache_data = cache_manager.load_snapshot(plan_id)
    if not cache_data:
        return jsonify({"error": "Plan not found"}), 404
    
    # Return just the batch names and their pre-parsed info
    batch_list = {}
    for label, data in cache_data.get('batches', {}).items():
        batch_list[label] = data.get('info', {})
        
    return jsonify({
        "plan_id": plan_id,
        "batches": batch_list,
        "room_no": cache_data.get('inputs', {}).get('room_id', 'N/A')
    })

@app.route('/api/export-attendance', methods=['POST'])
def export_attendance():
    """
    FIXED: The main route to generate a PDF for a SPECIFIC batch 
    using the structured cache data.
    """
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        batch_name = data.get('batch_name')
        frontend_metadata = data.get('metadata', {}) 

        # 1. Load the structured cache created by CacheManager
        cache_data = cache_manager.load_snapshot(plan_id)
        if not cache_data:
            return jsonify({"error": "Seating plan cache not found"}), 404

        # 2. Get the specific batch data organized by CacheManager
        batch_data = cache_data.get('batches', {}).get(batch_name)
        if not batch_data:
            return jsonify({"error": f"Batch '{batch_name}' not found in this plan"}), 404

        # 3. Path for temporary PDF generation
        temp_filename = f"temp_{plan_id}_{batch_name.replace(' ', '_')}.pdf"
        
        # 4. Generate PDF using the pre-structured data
        # student_list = batch_data['students']
        # extracted_info = batch_data['info']
        create_attendance_pdf(
            temp_filename, 
            batch_data['students'], 
            batch_name, 
            frontend_metadata, 
            batch_data['info']
        )

        # 5. Read PDF into memory and return to user
        return_data = io.BytesIO()
        with open(temp_filename, 'rb') as f:
            return_data.write(f.read())
        return_data.seek(0)
        
        # 6. Cleanup the temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        return send_file(
            return_data,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Attendance_{batch_name}_{frontend_metadata.get('course_code', '')}.pdf"
        )

    except Exception as e:
        print(f"Export Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
# --------------------------------------------------
# Admin/Maintenance Routes
# --------------------------------------------------
@app.route("/api/reset-data", methods=["POST"])
@token_required
def reset_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("DELETE FROM students")
        cur.execute("DELETE FROM uploads")
        cur.execute("DELETE FROM allocations")
        
        cur.execute("DELETE FROM sqlite_sequence WHERE name='students'")
        cur.execute("DELETE FROM sqlite_sequence WHERE name='uploads'")
        cur.execute("DELETE FROM sqlite_sequence WHERE name='allocations'")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "All data has been cleared."
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# DATABASE MANAGEMENT API ROUTES
# Add these routes to app.py after the existing routes
# ============================================================================

# --------------------------------------------------
# Database Overview & Statistics
# --------------------------------------------------
@app.route("/api/database/overview", methods=["GET"])
@token_required
def get_database_overview():
    """Get comprehensive database statistics and overview"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get counts for all tables
        cur.execute("SELECT COUNT(*) as count FROM students")
        students_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM classrooms")
        classrooms_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM uploads")
        uploads_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM allocations")
        allocations_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM feedback")
        feedback_count = cur.fetchone()['count']
        
        # Get batch statistics
        cur.execute("""
            SELECT batch_name, COUNT(*) as count 
            FROM students 
            GROUP BY batch_name 
            ORDER BY count DESC
        """)
        batch_stats = [dict(row) for row in cur.fetchall()]
        
        # Get recent uploads
        cur.execute("""
            SELECT batch_id, batch_name, created_at 
            FROM uploads 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_uploads = [dict(row) for row in cur.fetchall()]
        
        # Database file size
        db_size = DB_PATH.stat().st_size / (1024 * 1024)  # MB
        
        conn.close()
        
        return jsonify({
            "success": True,
            "overview": {
                "tables": {
                    "students": students_count,
                    "classrooms": classrooms_count,
                    "uploads": uploads_count,
                    "allocations": allocations_count,
                    "feedback": feedback_count
                },
                "batch_statistics": batch_stats,
                "recent_uploads": recent_uploads,
                "database_size_mb": round(db_size, 2),
                "database_path": str(DB_PATH)
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --------------------------------------------------
# Generic Table Data Management
# --------------------------------------------------
@app.route("/api/database/table/<table_name>", methods=["GET"])
@token_required
def get_table_data(table_name):
    """Get paginated data from any table"""
    try:
        # Whitelist allowed tables for security
        allowed_tables = ['students', 'classrooms', 'uploads', 'allocations', 'feedback']
        if table_name not in allowed_tables:
            return jsonify({"error": "Invalid table name"}), 400
        
        # Pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'id')
        sort_order = request.args.get('sort_order', 'DESC')
        
        offset = (page - 1) * per_page
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get total count
        if search:
            # Build search condition (search across all text columns)
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = [col['name'] for col in cur.fetchall()]
            search_conditions = ' OR '.join([f"{col} LIKE ?" for col in columns if col != 'id'])
            search_params = [f"%{search}%"] * len([c for c in columns if c != 'id'])
            
            cur.execute(f"SELECT COUNT(*) as count FROM {table_name} WHERE {search_conditions}", search_params)
        else:
            cur.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        
        total_count = cur.fetchone()['count']
        
        # Get paginated data
        if search:
            cur.execute(
                f"SELECT * FROM {table_name} WHERE {search_conditions} ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?",
                search_params + [per_page, offset]
            )
        else:
            cur.execute(
                f"SELECT * FROM {table_name} ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?",
                [per_page, offset]
            )
        
        rows = [dict(row) for row in cur.fetchall()]
        
        # Get column info
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = [
            {
                'name': col['name'],
                'type': col['type'],
                'not_null': bool(col['notnull']),
                'primary_key': bool(col['pk'])
            }
            for col in cur.fetchall()
        ]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "table": table_name,
            "columns": columns,
            "data": rows,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --------------------------------------------------
# Create/Insert Record
# --------------------------------------------------
@app.route("/api/database/table/<table_name>", methods=["POST"])
@token_required
def create_record(table_name):
    """Create a new record in specified table"""
    try:
        allowed_tables = ['students', 'classrooms', 'uploads', 'allocations']
        if table_name not in allowed_tables:
            return jsonify({"error": "Invalid table name"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Build INSERT query
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())
        
        cur.execute(
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
            values
        )
        
        record_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Record created in {table_name}",
            "id": record_id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# --------------------------------------------------
# Update Record
# --------------------------------------------------
@app.route("/api/database/table/<table_name>/<int:record_id>", methods=["PUT"])
@token_required
def update_record(table_name, record_id):
    """Update a record in specified table"""
    try:
        allowed_tables = ['students', 'classrooms', 'uploads', 'allocations']
        if table_name not in allowed_tables:
            return jsonify({"error": "Invalid table name"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Build UPDATE query
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [record_id]
        
        cur.execute(
            f"UPDATE {table_name} SET {set_clause} WHERE id = ?",
            values
        )
        
        if cur.rowcount == 0:
            conn.close()
            return jsonify({"error": "Record not found"}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Record updated in {table_name}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# --------------------------------------------------
# Delete Record
# --------------------------------------------------
@app.route("/api/database/table/<table_name>/<int:record_id>", methods=["DELETE"])
@token_required
def delete_record(table_name, record_id):
    """Delete a record from specified table"""
    try:
        allowed_tables = ['students', 'classrooms', 'uploads', 'allocations', 'feedback']
        if table_name not in allowed_tables:
            return jsonify({"error": "Invalid table name"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute(f"DELETE FROM {table_name} WHERE id = ?", [record_id])
        
        if cur.rowcount == 0:
            conn.close()
            return jsonify({"error": "Record not found"}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Record deleted from {table_name}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# --------------------------------------------------
# Bulk Delete
# --------------------------------------------------
@app.route("/api/database/table/<table_name>/bulk-delete", methods=["POST"])
@token_required
def bulk_delete_records(table_name):
    """Delete multiple records from specified table"""
    try:
        allowed_tables = ['students', 'classrooms', 'uploads', 'allocations', 'feedback']
        if table_name not in allowed_tables:
            return jsonify({"error": "Invalid table name"}), 400
        
        data = request.get_json()
        record_ids = data.get('ids', [])
        
        if not record_ids:
            return jsonify({"error": "No IDs provided"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        placeholders = ','.join(['?' for _ in record_ids])
        cur.execute(f"DELETE FROM {table_name} WHERE id IN ({placeholders})", record_ids)
        
        deleted_count = cur.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Deleted {deleted_count} records from {table_name}",
            "deleted_count": deleted_count
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# --------------------------------------------------
# Export Table to CSV
# --------------------------------------------------
@app.route("/api/database/table/<table_name>/export", methods=["GET"])
@token_required
def export_table_csv(table_name):
    """Export table data as CSV"""
    try:
        allowed_tables = ['students', 'classrooms', 'uploads', 'allocations', 'feedback']
        if table_name not in allowed_tables:
            return jsonify({"error": "Invalid table name"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        
        if not rows:
            conn.close()
            return jsonify({"error": "No data to export"}), 404
        
        # Create CSV
        import csv
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        
        for row in rows:
            writer.writerow(dict(row))
        
        conn.close()
        
        # Create response
        csv_data = output.getvalue()
        response = app.response_class(
            response=csv_data,
            status=200,
            mimetype='text/csv'
        )
        response.headers['Content-Disposition'] = f'attachment; filename={table_name}_export.csv'
        
        return response
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --------------------------------------------------
# Database Backup
# --------------------------------------------------
@app.route("/api/database/backup", methods=["POST"])
@token_required
def backup_database():
    """Create a backup of the database"""
    try:
        backup_dir = BASE_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"backup_{timestamp}.db"
        
        # Copy database file
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        
        return jsonify({
            "success": True,
            "message": "Database backed up successfully",
            "backup_file": backup_path.name,
            "backup_size_mb": round(backup_path.stat().st_size / (1024 * 1024), 2)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --------------------------------------------------
# Get Database Schema
# --------------------------------------------------
@app.route("/api/database/schema", methods=["GET"])
@token_required
def get_database_schema():
    """Get complete database schema"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get all tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row['name'] for row in cur.fetchall()]
        
        schema = {}
        for table in tables:
            cur.execute(f"PRAGMA table_info({table})")
            columns = [dict(row) for row in cur.fetchall()]
            
            cur.execute(f"SELECT COUNT(*) as count FROM {table}")
            row_count = cur.fetchone()['count']
            
            schema[table] = {
                'columns': columns,
                'row_count': row_count
            }
        
        conn.close()
        
        return jsonify({
            "success": True,
            "schema": schema
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --------------------------------------------------
# Search Across All Tables
# --------------------------------------------------
@app.route("/api/database/search", methods=["GET"])
@token_required
def global_search():
    """Search across all tables"""
    try:
        query = request.args.get('q', '')
        if not query or len(query) < 2:
            return jsonify({"error": "Query too short (minimum 2 characters)"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        results = {}
        search_pattern = f"%{query}%"
        
        # Search students
        cur.execute("""
            SELECT * FROM students 
            WHERE enrollment LIKE ? OR name LIKE ? OR batch_name LIKE ?
            LIMIT 20
        """, [search_pattern, search_pattern, search_pattern])
        results['students'] = [dict(row) for row in cur.fetchall()]
        
        # Search classrooms
        cur.execute("SELECT * FROM classrooms WHERE name LIKE ? LIMIT 20", [search_pattern])
        results['classrooms'] = [dict(row) for row in cur.fetchall()]
        
        # Search uploads
        cur.execute("""
            SELECT * FROM uploads 
            WHERE batch_name LIKE ? OR batch_id LIKE ?
            LIMIT 20
        """, [search_pattern, search_pattern])
        results['uploads'] = [dict(row) for row in cur.fetchall()]
        
        conn.close()
        
        total_results = sum(len(v) for v in results.values())
        
        return jsonify({
            "success": True,
            "query": query,
            "total_results": total_results,
            "results": results
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --------------------------------------------------
# Health Check
# --------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "modules": {
            "auth": auth_signup is not None,
            "google_auth": google_auth_handler is not None,
            "pdf": create_seating_pdf is not None,
            "parser": StudentDataParser is not None,
            "algorithm": SeatingAlgorithm is not None
        }
    })

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Flask Server on http://localhost:5000")
    print("=" * 70)
    app.run(debug=True, port=5000)