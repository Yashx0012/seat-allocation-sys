"""
app.py - PRODUCTION VERSION v3.0

Seat Allocation System - Flask Backend

FIXED in v3.0:
✅ batch_color support throughout
✅ Session finalization properly updates status
✅ /api/sessions/<id>/uploads endpoint added
✅ Enhanced error handling and logging
✅ Atomic database operations with proper rollbacks
✅ Activity tracking prevents session timeouts
✅ Comprehensive validation on all endpoints

Architecture:
- SQLite database with proper foreign keys
- RESTful API with JWT authentication
- Session-based allocation workflow
- History tracking for undo functionality
- PDF generation and attendance sheets
"""

# Old file: needs to be removed
# This was the monolithic app.py before the backend was restructured into a modular architecture.
import json
import re
import sys
import io
import sqlite3
import uuid
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
from typing import Dict, List, Tuple, Optional, Any

from flask import Flask, jsonify, request, send_file, render_template, session as flask_session
from flask_cors import CORS

# Import local modules
from cache_manager import CacheManager
from leftover_calculator import LeftoverCalculator

# PDF Generation
from pdf_gen.pdf_generation import get_or_create_seating_pdf
from pdf_gen.template_manager import template_manager
from attendence_gen.attend_gen import create_attendance_pdf

# Initialize cache manager
cache_manager = CacheManager()

# ============================================================================
# HYBRID CACHING HELPERS FOR PDF GENERATION
# ============================================================================
def get_seating_from_cache(plan_id: str, room_no: Optional[str] = None) -> Optional[Dict]:
    """
    Retrieve seating data from cache.
    
    Args:
        plan_id: Plan ID to lookup
        room_no: Optional specific room. If None, use latest room.
    
    Returns:
        Dict with 'seating' and 'metadata' or None if not found
    """
    try:
        snapshot = cache_manager.load_snapshot(plan_id)
        if not snapshot:
            return None
        
        # Determine which room to use
        if not room_no:
            room_no = snapshot.get('metadata', {}).get('latest_room')
        
        if not room_no or room_no not in snapshot.get('rooms', {}):
            # Fallback to first available room
            rooms = snapshot.get('rooms', {})
            if rooms:
                room_no = next(iter(rooms.keys()))
            else:
                return None
        
        room_data = snapshot['rooms'][room_no]
        
        return {
            'seating': room_data.get('raw_matrix', []),
            'metadata': snapshot.get('metadata', {}),
            'batches': room_data.get('batches', {}),
            'room_no': room_no,
            'source': 'cache'
        }
    except Exception as e:
        logger.warning(f"⚠️ Cache retrieval failed for plan {plan_id}: {e}")
        return None


def get_seating_from_database(session_id: int) -> Optional[Dict]:
    """
    Retrieve seating data from database allocations.
    Fallback when cache is unavailable.
    
    Args:
        session_id: Session ID to lookup
    
    Returns:
        Dict with seating and metadata or None
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get session info
        cur.execute("""
            SELECT plan_id, total_students, allocated_count
            FROM allocation_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        session_row = cur.fetchone()
        if not session_row:
            conn.close()
            return None
        
        plan_id = session_row['plan_id']
        
        # Try cache first (preferred)
        cached = get_seating_from_cache(plan_id)
        if cached:
            conn.close()
            return cached
        
        # Fallback: Build from database
        cur.execute("""
            SELECT a.seat_position, a.paper_set, a.enrollment, s.name, s.batch_name, c.name as room_name
            FROM allocations a
            JOIN students s ON a.student_id = s.id
            LEFT JOIN classrooms c ON a.classroom_id = c.id
            WHERE a.session_id = ?
            ORDER BY c.name, a.seat_position
        """, (session_id,))
        
        allocations = cur.fetchall()
        
        if not allocations:
            conn.close()
            return None
        
        # Build metadata
        metadata = {
            'plan_id': plan_id,
            'total_students': session_row['total_students'],
            'allocated_count': session_row['allocated_count']
        }
        
        # Build seating matrix from allocations (basic structure)
        seating = []
        for row in allocations:
            seating.append({
                'position': row['seat_position'],
                'roll_number': row['enrollment'],
                'name': row['name'],
                'batch_label': row['batch_name'],
                'room_no': row['room_name']
            })
        
        conn.close()
        
        return {
            'seating': seating,
            'metadata': metadata,
            'source': 'database'
        }
    except Exception as e:
        logger.error(f"❌ Database retrieval failed for session {session_id}: {e}")
        return None


def get_all_room_seating_from_cache(plan_id: str) -> Optional[Dict]:
    """
    Retrieve all rooms' seating data from cache for batch PDF generation.
    
    Args:
        plan_id: Plan ID to lookup
    
    Returns:
        Dict mapping room_no to seating data, or None
    """
    try:
        snapshot = cache_manager.load_snapshot(plan_id)
        if not snapshot or 'rooms' not in snapshot:
            return None
        
        all_rooms = {}
        for room_no, room_data in snapshot['rooms'].items():
            all_rooms[room_no] = {
                'seating': room_data.get('raw_matrix', []),
                'metadata': {**snapshot.get('metadata', {}), 'room_no': room_no},
                'batches': room_data.get('batches', {})
            }
        
        logger.info(f"✅ Loaded {len(all_rooms)} rooms from cache for plan {plan_id}")
        return all_rooms
    except Exception as e:
        logger.warning(f"⚠️ Failed to get all rooms from cache: {e}")
        return None

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, "Backend")

if os.path.exists(BACKEND_DIR):
    sys.path.insert(0, BACKEND_DIR)

# Import auth services (optional)
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
    logger.info("✅ Auth service loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Auth module not available: {e}")

# Import algorithm modules
try:
    from student_parser import StudentDataParser
    from algo import SeatingAlgorithm
    logger.info("✅ Algorithm modules loaded")
except ImportError as e:
    logger.error(f"❌ Core modules not found: {e}")
    StudentDataParser = None
    SeatingAlgorithm = None

# Paths
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "demo.db"

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-prod')
app.config['FEEDBACK_FOLDER'] = BASE_DIR / "feedback_files"
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})



# ============================================================================
# DATABASE INITIALIZATION (ENHANCED)
# ============================================================================
# --------------------------------------------------
# Database Helper
# --------------------------------------------------
def get_db_connection():
    """Establishes a connection to the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def ensure_demo_db():
    """
    Initialize database with all required tables.
    
    ENHANCED: Now includes all missing columns and proper constraints.
    This function is idempotent - safe to run multiple times.
    """
    logger.info("🔧 Initializing database...")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # ====================================================================
        # 1. USER ACTIVITY TABLE
        # ====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id INTEGER PRIMARY KEY,
                last_activity DATETIME NOT NULL,
                last_endpoint TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ====================================================================
        # 2. USERS TABLE
        # ====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT,
                role TEXT DEFAULT 'STUDENT' CHECK(role IN ('STUDENT', 'ADMIN', 'TEACHER')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            );
        """)

        # ====================================================================
        # 3. ALLOCATION SESSIONS TABLE (ENHANCED)
        # ====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS allocation_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT UNIQUE NOT NULL,
                user_id INTEGER DEFAULT 1,
                name TEXT,
                status TEXT CHECK(status IN ('active', 'completed', 'archived', 'draft', 'expired')) DEFAULT 'active',
                total_students INTEGER DEFAULT 0,
                allocated_count INTEGER DEFAULT 0,
                total_capacity INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        # ====================================================================
        # 4. UPLOADS TABLE (ENHANCED WITH BATCH_COLOR)
        # ====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                batch_id TEXT UNIQUE NOT NULL,
                batch_name TEXT NOT NULL,
                batch_color TEXT DEFAULT '#3b82f6',
                original_filename TEXT,
                file_size INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES allocation_sessions(session_id) ON DELETE SET NULL
            );
        """)

        # ====================================================================
        # 5. STUDENTS TABLE (ENHANCED)
        # ====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id INTEGER NOT NULL,
                batch_id TEXT NOT NULL,
                batch_name TEXT NOT NULL,
                batch_color TEXT DEFAULT '#3b82f6',
                enrollment TEXT NOT NULL,
                name TEXT,
                department TEXT,
                inserted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(upload_id, enrollment),
                FOREIGN KEY (upload_id) REFERENCES uploads(id) ON DELETE CASCADE
            );
        """)

        # ====================================================================
        # 6. CLASSROOMS TABLE
        # ====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS classrooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                rows INTEGER NOT NULL CHECK(rows > 0 AND rows <= 50),
                cols INTEGER NOT NULL CHECK(cols > 0 AND cols <= 50),
                broken_seats TEXT DEFAULT '',
                block_width INTEGER DEFAULT 1 CHECK(block_width > 0),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ====================================================================
        # 7. ALLOCATIONS TABLE (ENHANCED)
        # ====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                classroom_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                enrollment TEXT NOT NULL,
                seat_position TEXT,
                batch_name TEXT,
                paper_set TEXT DEFAULT 'A',
                allocated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES allocation_sessions(session_id) ON DELETE CASCADE,
                FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE RESTRICT,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE(session_id, student_id)
            );
        """)

        # Create index for faster queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_allocations_session 
            ON allocations(session_id);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_allocations_classroom 
            ON allocations(classroom_id);
        """)

        # ====================================================================
        # 8. ALLOCATION HISTORY TABLE
        # ====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS allocation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                classroom_id INTEGER,
                action_type TEXT CHECK(action_type IN ('allocate', 'undo', 'reset')) NOT NULL,
                students_affected INTEGER DEFAULT 0,
                snapshot_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES allocation_sessions(session_id) ON DELETE CASCADE,
                UNIQUE(session_id, step_number)
            );
        """)

        # ====================================================================
        # 9. FEEDBACK TABLE
        # ====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                issue_type TEXT NOT NULL,
                priority TEXT NOT NULL CHECK(priority IN ('low', 'medium', 'high', 'critical')),
                description TEXT NOT NULL,
                feature_suggestion TEXT,
                additional_info TEXT,
                file_path TEXT,
                file_name TEXT,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'reviewed', 'resolved', 'closed')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved_at DATETIME,
                admin_response TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        # ====================================================================
        # 10. ENSURE COLUMNS EXIST (FOR MIGRATION FROM OLDER VERSIONS)
        # ====================================================================
        migration_queries = [
            ("ALTER TABLE uploads ADD COLUMN batch_color TEXT DEFAULT '#3b82f6'", "uploads.batch_color"),
            ("ALTER TABLE students ADD COLUMN batch_color TEXT DEFAULT '#3b82f6'", "students.batch_color"),
            ("ALTER TABLE students ADD COLUMN department TEXT", "students.department"),
            ("ALTER TABLE allocation_sessions ADD COLUMN user_id INTEGER DEFAULT 1", "sessions.user_id"),
            ("ALTER TABLE allocation_sessions ADD COLUMN name TEXT", "sessions.name"),
            ("ALTER TABLE allocation_sessions ADD COLUMN last_activity DATETIME DEFAULT CURRENT_TIMESTAMP", "sessions.last_activity"),
            ("ALTER TABLE classrooms ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP", "classrooms.updated_at"),
        ]

        for query, col_name in migration_queries:
            try:
                cur.execute(query)
                logger.debug(f"✅ Added column: {col_name}")
            except sqlite3.OperationalError:
                # Column already exists
                pass

        conn.commit()
        logger.info(f"✅ Database initialized successfully at {DB_PATH}")
        
        # Log table counts
        cur.execute("SELECT COUNT(*) FROM classrooms")
        classroom_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM students")
        student_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM allocation_sessions WHERE status='active'")
        active_sessions = cur.fetchone()[0]
        
        logger.info(f"📊 Database stats: {classroom_count} classrooms, {student_count} students, {active_sessions} active sessions")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

# Initialize database on startup
try:
    ensure_demo_db()
except Exception as e:
    logger.critical(f"💥 FATAL: Database initialization failed: {e}")
    sys.exit(1)

# ============================================================================
# MIDDLEWARE: ACTIVITY TRACKING
# ============================================================================

@app.before_request
def track_user_activity():
    """
    Track user activity globally across ALL endpoints.
    This prevents session expiration while user is active anywhere in app.
    
    Runs before every request (except static files and OPTIONS).
    """
    # Skip for static files and preflight requests
    if request.path.startswith('/static') or request.method == 'OPTIONS':
        return
    
    # Skip for health check (avoid log spam)
    if request.path == '/api/health':
        return
    
    # Get user_id from token or default to 1 (for MVP - single admin)
    user_id = getattr(request, 'user_id', None)
    
    # If no auth, check if there's a token in header
    if not user_id:
        auth_header = request.headers.get('Authorization')
        if auth_header and verify_token:
            try:
                token = auth_header.split(' ')[1]
                payload = verify_token(token)
                if payload:
                    user_id = payload.get('user_id')
            except Exception:
                pass
    
    # Default to user_id=1 for MVP (single admin scenario)
    if not user_id:
        user_id = 1
    
    # Update activity in database
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cur.execute("""
            INSERT INTO user_activity (user_id, last_activity, last_endpoint)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                last_activity = excluded.last_activity,
                last_endpoint = excluded.last_endpoint
        """, (user_id, now, request.path))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"📍 Activity tracked: user={user_id}, endpoint={request.path}")
        
    except Exception as e:
        logger.error(f"❌ Activity tracking error: {e}")
        # Don't fail the request if tracking fails

# ============================================================================
# SESSION EXPIRATION LOGIC
# ============================================================================

def check_session_expiry(session_id: int) -> Tuple[bool, str]:
    """
    Check if session should be expired based on user inactivity.
    
    Args:
        session_id: ID of session to check
    
    Returns:
        (should_expire: bool, reason: str)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get session with user activity
        cur.execute("""
            SELECT s.*, u.last_activity as user_last_activity
            FROM allocation_sessions s
            LEFT JOIN user_activity u ON s.user_id = u.user_id
            WHERE s.session_id = ?
        """, (session_id,))
        
        session = cur.fetchone()
        conn.close()
        
        if not session:
            return True, "Session not found"
        
        # Never expire completed/archived sessions
        if session['status'] in ['completed', 'archived']:
            return False, "Session is completed/archived"
        
        # Check user activity (app-wide, not just session pages)
        if session['user_last_activity']:
            last_activity = datetime.fromisoformat(session['user_last_activity'])
            inactive_duration = datetime.now() - last_activity
            
            # 30-minute threshold
            EXPIRY_THRESHOLD = timedelta(minutes=30)
            
            if inactive_duration > EXPIRY_THRESHOLD:
                minutes_inactive = int(inactive_duration.total_seconds() / 60)
                return True, f"User inactive for {minutes_inactive} minutes"
        else:
            # No activity record - check session creation time
            created_at = datetime.fromisoformat(session['created_at'])
            age = datetime.now() - created_at
            
            if age > timedelta(hours=2):
                return True, "Session older than 2 hours with no activity"
        
        return False, "Session is active"
        
    except Exception as e:
        logger.error(f"❌ Expiry check error for session {session_id}: {e}")
        return False, "Error checking expiry"


def expire_session(session_id: int) -> bool:
    """
    Mark session as expired (soft delete).
    Empty draft sessions are hard deleted.
    
    Args:
        session_id: ID of session to expire
    
    Returns:
        True if successful
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Check if session has any data
        cur.execute("""
            SELECT 
                s.*,
                (SELECT COUNT(*) FROM uploads WHERE session_id = s.session_id) as upload_count,
                (SELECT COUNT(*) FROM allocations WHERE session_id = s.session_id) as allocation_count
            FROM allocation_sessions s
            WHERE s.session_id = ?
        """, (session_id,))
        
        session = cur.fetchone()
        
        if not session:
            conn.close()
            return False
        
        session_dict = dict(session)
        
        # If empty draft, hard delete
        if (session_dict['status'] == 'active' and 
            session_dict['upload_count'] == 0 and 
            session_dict['allocation_count'] == 0):
            
            cur.execute("DELETE FROM allocation_sessions WHERE session_id = ?", (session_id,))
            logger.info(f"🗑️ Hard deleted empty session {session_id}")
        else:
            # Otherwise, soft delete (mark as expired)
            cur.execute("""
                UPDATE allocation_sessions
                SET status = 'expired'
                WHERE session_id = ?
            """, (session_id,))
            logger.info(f"⏰ Soft deleted (expired) session {session_id}")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Expire session error for session {session_id}: {e}")
        return False


def get_session_with_expiry_check(session_id: int) -> Optional[Dict]:
    """
    Get session and check if it should be expired.
    
    Args:
        session_id: ID of session to retrieve
    
    Returns:
        Session dict or None if expired/not found
    """
    should_expire, reason = check_session_expiry(session_id)
    
    if should_expire:
        logger.info(f"⏰ Expiring session {session_id}: {reason}")
        expire_session(session_id)
        return None
    
    # Return session data
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM allocation_sessions WHERE session_id = ?", (session_id,))
        session = cur.fetchone()
        conn.close()
        
        return dict(session) if session else None
        
    except Exception as e:
        logger.error(f"❌ Get session error for session {session_id}: {e}")
        return None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_int_dict(val: Any) -> Dict[int, int]:
    """Parse a value into Dict[int, int]."""
    if isinstance(val, dict):
        return {int(k): int(v) for k, v in val.items()}
    if isinstance(val, str) and val:
        try:
            return json.loads(val)
        except Exception:
            pass
    return {}


def parse_str_dict(val: Any) -> Dict[int, str]:
    """Parse a value into Dict[int, str]."""
    if isinstance(val, dict):
        return {int(k): str(v) for k, v in val.items()}
    if isinstance(val, str) and val:
        try:
            return json.loads(val)
        except Exception:
            pass
    return {}


def get_batch_counts_and_labels_from_db(session_id: Optional[int] = None) -> Tuple[Dict[int, int], Dict[int, str]]:
    """
    Get batch counts and labels, optionally filtered by session.
    
    Args:
        session_id: Optional session ID to filter by
    
    Returns:
        (counts_dict, labels_dict) where keys are 1-indexed batch numbers
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        if session_id:
            cur.execute("""
                SELECT s.batch_name, COUNT(*) as count
                FROM students s
                JOIN uploads u ON s.upload_id = u.id
                WHERE u.session_id = ?
                GROUP BY s.batch_name
                ORDER BY s.batch_name
            """, (session_id,))
        else:
            cur.execute("""
                SELECT batch_name, COUNT(*) as count
                FROM students
                GROUP BY batch_name
                ORDER BY batch_name
            """)
        
        rows = cur.fetchall()
        
        counts = {}
        labels = {}
        for i, (name, count) in enumerate(rows, start=1):
            counts[i] = count
            labels[i] = name
        
        logger.debug(f"📊 Batch counts: {counts}, labels: {labels}")
        
        return counts, labels
        
    finally:
        conn.close()


def get_batch_roll_numbers_from_db(session_id: Optional[int] = None) -> Dict[int, List[Dict]]:
    """
    Get roll numbers by batch, optionally filtered by session.
    
    Args:
        session_id: Optional session ID to filter by
    
    Returns:
        Dict mapping batch number (1-indexed) to list of {"roll": ..., "name": ...}
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        if session_id:
            cur.execute("""
                SELECT s.batch_name, s.enrollment, s.name
                FROM students s
                JOIN uploads u ON s.upload_id = u.id
                WHERE u.session_id = ?
                ORDER BY s.id
            """, (session_id,))
        else:
            cur.execute("""
                SELECT batch_name, enrollment, name
                FROM students
                ORDER BY id
            """)
        
        rows = cur.fetchall()
        
        # Group by batch name
        groups = {}
        for batch_name, enrollment, name in rows:
            if batch_name not in groups:
                groups[batch_name] = []
            groups[batch_name].append({
                "roll": enrollment,
                "name": name if name else ""
            })
        
        # Convert to 1-indexed dict
        result = {i + 1: groups[k] for i, k in enumerate(sorted(groups))}
        
        logger.debug(f"📋 Loaded roll numbers for {len(result)} batches")
        
        return result
        
    finally:
        conn.close()


def get_pending_students(session_id: int) -> List[Dict]:
    """
    Get students not yet allocated in this session.
    
    Args:
        session_id: Session ID to check
    
    Returns:
        List of student dicts with id, enrollment, name, batch_name, batch_id
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    try:
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
        
        logger.debug(f"📝 Found {len(pending)} pending students for session {session_id}")
        
        return pending
        
    except Exception as e:
        logger.error(f"❌ Error fetching pending students for session {session_id}: {e}")
        return []
    finally:
        conn.close()


def save_room_allocation(session_id: int, classroom_id: int, seating_data: Dict, 
                        selected_batch_names: List[str] = None) -> Tuple[int, List[Dict]]:
    """
    Save room allocation to DATABASE and CACHE
    
    Args:
        session_id: Session ID
        classroom_id: Classroom ID  
        seating_data: Generated seating data with 'seating' matrix
        selected_batch_names: List of batch names selected for this room (optional)
    
    Returns:
        (allocated_count, pending_students)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    allocated_students = []
    
    try:
        # ============================================================================
        # 1. GET SESSION AND CLASSROOM INFO
        # ============================================================================
        
        # Get plan_id from session
        cur.execute("""
            SELECT plan_id, total_students, allocated_count
            FROM allocation_sessions
            WHERE session_id = ?
        """, (session_id,))
        session_row = cur.fetchone()
        
        if not session_row:
            raise Exception(f"Session {session_id} not found")
        
        plan_id = session_row['plan_id']
        
        # Get classroom details
        cur.execute("""
            SELECT id, name, rows, cols, broken_seats, block_width
            FROM classrooms
            WHERE id = ?
        """, (classroom_id,))
        classroom_row = cur.fetchone()
        
        if not classroom_row:
            raise Exception(f"Classroom {classroom_id} not found")
        
        room_name = classroom_row['name']
        room_rows = classroom_row['rows']
        room_cols = classroom_row['cols']
        
        # Get current step number
        cur.execute("""
            SELECT COALESCE(MAX(step_number), 0) + 1
            FROM allocation_history
            WHERE session_id = ?
        """, (session_id,))
        step_number = cur.fetchone()[0]
        
        logger.info(f"💾 Saving room allocation: session={session_id}, room={room_name}, selected_batches={selected_batch_names}")
        
        # ============================================================================
        # 2. PROCESS SEATING AND SAVE TO DATABASE
        # ============================================================================
        
        seating_matrix = seating_data.get('seating', [])
        
        for row_idx, row in enumerate(seating_matrix):
            for col_idx, seat in enumerate(row):
                if seat and not seat.get('is_broken') and not seat.get('is_unallocated'):
                    enrollment = seat.get('roll_number')
                    
                    if not enrollment:
                        continue
                    
                    # Find student in database
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
                        
                        # Verify student is in selected batches
                        if selected_batch_names and batch_name not in selected_batch_names:
                            logger.warning(f"⚠️ Skipping {enrollment}: not in selected batches")
                            continue
                        
                        seat_pos = f"{row_idx + 1}-{col_idx + 1}"
                        paper_set = seat.get('paper_set', 'A')
                        
                        # Insert allocation to database
                        cur.execute("""
                            INSERT INTO allocations
                            (session_id, classroom_id, student_id, enrollment,
                             seat_position, batch_name, paper_set)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (session_id, classroom_id, student_id, enrollment,
                              seat_pos, batch_name, paper_set))
                        
                        # ✅ Update seat with position info for cache
                        seat['position'] = seat_pos
                        seat['row'] = row_idx + 1
                        seat['col'] = col_idx + 1
                        
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
        
        if cur.rowcount == 0:
            raise Exception(f"Failed to update session {session_id}")
        
        # Save history
        cur.execute("""
            INSERT INTO allocation_history
            (session_id, step_number, classroom_id, action_type,
             students_affected, snapshot_data)
            VALUES (?, ?, ?, 'allocate', ?, ?)
        """, (session_id, step_number, classroom_id, len(allocated_students),
              json.dumps(allocated_students)))
        
        conn.commit()
        
        # ============================================================================
        # 3. ✅ CRITICAL: SAVE TO CACHE
        # ============================================================================
        
        input_config = {
            'rows': room_rows,
            'cols': room_cols,
            'block_width': seating_data.get('block_width') or classroom_row['block_width'] or 1,
            'broken_seats': seating_data.get('broken_seats') or classroom_row['broken_seats'] or '',
            'session_id': session_id,
            'classroom_id': classroom_id,
            'room_no': room_name
        }
        
        # ✅ THIS IS THE CRITICAL LINE - Save to cache with room name!
        cache_manager.save_or_update(
            plan_id=plan_id,
            input_config=input_config,
            output_data=seating_data,
            room_no=room_name  # ✅ Pass room name so it's stored under rooms[room_name]
        )
        
        logger.info(f"✅ Saved to CACHE: plan={plan_id}, room={room_name}, students={len(allocated_students)}")
        
        # ============================================================================
        # 4. GET PENDING STUDENTS
        # ============================================================================
        
        pending = get_pending_students(session_id)
        
        logger.info(f"✅ Allocation complete: {len(allocated_students)} saved, {len(pending)} pending")
        
        return len(allocated_students), pending
        
    except Exception as e:
        logger.error(f"❌ Error saving room allocation: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return 0, []
    finally:
        conn.close()

        

def undo_last_allocation(session_id: int) -> Tuple[bool, str]:
    """
    Undo last room allocation.
    
    Args:
        session_id: Session ID
    
    Returns:
        (success, message)
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        # Get last allocation step
        cur.execute("""
            SELECT id, classroom_id, students_affected, snapshot_data
            FROM allocation_history
            WHERE session_id = ? AND action_type = 'allocate'
            ORDER BY step_number DESC
            LIMIT 1
        """, (session_id,))
        
        last_step = cur.fetchone()
        if not last_step:
            return False, "No allocations to undo"
        
        history_id, classroom_id, students_affected, snapshot_data = last_step
        
        logger.info(f"↩️ Undoing allocation: session={session_id}, classroom={classroom_id}, students={students_affected}")
        
        # Delete allocations for that classroom in this session
        cur.execute("""
            DELETE FROM allocations
            WHERE session_id = ? AND classroom_id = ?
        """, (session_id, classroom_id))
        
        # Update session totals
        cur.execute("""
            UPDATE allocation_sessions
            SET allocated_count = allocated_count - ?,
                last_activity = ?
            WHERE session_id = ?
        """, (students_affected, datetime.now().isoformat(), session_id))
        
        # Mark history as undone
        cur.execute("""
            INSERT INTO allocation_history
            (session_id, step_number, classroom_id, action_type, students_affected)
            VALUES (?,
                    (SELECT COALESCE(MAX(step_number), 0) + 1 FROM allocation_history WHERE session_id = ?),
                    ?, 'undo', ?)
        """, (session_id, session_id, classroom_id, students_affected))
        
        conn.commit()
        
        logger.info(f"✅ Undid allocation for classroom {classroom_id}")
        
        return True, f"Undid {students_affected} allocations"
        
    except Exception as e:
        logger.error(f"❌ Error undoing allocation: {e}")
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def validate_session_capacity(session_id: int, selected_classrooms: List[int]) -> Tuple[bool, Dict]:
    """
    Validate that selected classrooms can fit all students.
    
    Args:
        session_id: Session ID
        selected_classrooms: List of classroom IDs (empty = use all)
    
    Returns:
        (is_valid, info_dict)
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        # Get total students
        cur.execute("""
            SELECT total_students FROM allocation_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        result = cur.fetchone()
        if not result:
            return False, {"error": "Session not found"}
        
        total_students = result[0]
        
        # Calculate capacity of selected classrooms
        if selected_classrooms:
            placeholders = ','.join(['?' for _ in selected_classrooms])
            cur.execute(f"""
                SELECT SUM(rows * cols) FROM classrooms
                WHERE id IN ({placeholders})
            """, selected_classrooms)
        else:
            cur.execute("SELECT SUM(rows * cols) FROM classrooms")
        
        total_capacity = cur.fetchone()[0] or 0
        
        if total_capacity < total_students:
            return False, {
                "error": "insufficient_capacity",
                "total_students": total_students,
                "total_capacity": total_capacity,
                "shortage": total_students - total_capacity
            }
        
        return True, {
            "total_students": total_students,
            "total_capacity": total_capacity,
            "surplus": total_capacity - total_students
        }
        
    except Exception as e:
        logger.error(f"❌ Capacity validation error: {e}")
        return False, {"error": str(e)}
    finally:
        conn.close()


def finalize_session(session_id: int, plan_id: str) -> bool:
    """
    Mark session as completed.
    
    Args:
        session_id: Session ID
        plan_id: Plan ID for logging
    
    Returns:
        True if successful
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE allocation_sessions
            SET status = 'completed',
                completed_at = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        
        conn.commit()
        
        logger.info(f"🏁 Finalized session {session_id} (plan_id: {plan_id})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error finalizing session {session_id}: {e}")
        return False
    finally:
        conn.close()


def get_session_stats(session_id: int) -> Dict:
    """
    Get allocation statistics for a session.
    
    Args:
        session_id: Session ID
    
    Returns:
        Dictionary with session, room, and batch stats
    """
    conn = sqlite3.connect(DB_PATH)
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
        if session_data['total_students'] > 0:
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
        logger.error(f"❌ Error getting session stats: {e}")
        return {}
    finally:
        conn.close()
# ============================================
# DASHBOARD API ENDPOINTS (FIXED - Uses SQLite)
# ============================================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Get all dashboard statistics - using raw SQLite
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get total students count
        cur.execute("SELECT COUNT(*) FROM students")
        total_students = cur.fetchone()[0] or 0
        
        # Get total classrooms count
        cur.execute("SELECT COUNT(*) FROM classrooms")
        total_classrooms = cur.fetchone()[0] or 0
        
        # Get allocated seats count (from completed sessions)
        cur.execute("""
            SELECT COUNT(*) FROM allocations a
            JOIN allocation_sessions s ON a.session_id = s.session_id
            WHERE s.status IN ('active', 'completed')
        """)
        allocated_seats = cur.fetchone()[0] or 0
        
        # Get completed plans count
        cur.execute("""
            SELECT COUNT(*) FROM allocation_sessions 
            WHERE status = 'completed'
        """)
        completed_plans = cur.fetchone()[0] or 0
        
        # Get reports/snapshots count
        reports_count = completed_plans  # Use completed plans as proxy
        
        # Calculate weekly changes
        one_week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        # Students added this week
        cur.execute("""
            SELECT COUNT(*) FROM students 
            WHERE inserted_at >= ?
        """, (one_week_ago,))
        new_students_this_week = cur.fetchone()[0] or 0
        
        students_change = 0
        if total_students > new_students_this_week and new_students_this_week > 0:
            students_change = round((new_students_this_week / max(total_students - new_students_this_week, 1)) * 100, 1)
        
        # Plans completed this week
        cur.execute("""
            SELECT COUNT(*) FROM allocation_sessions 
            WHERE status = 'completed' AND completed_at >= ?
        """, (one_week_ago,))
        new_plans_this_week = cur.fetchone()[0] or 0
        
        plans_change = 0
        if completed_plans > 0 and new_plans_this_week > 0:
            plans_change = round((new_plans_this_week / max(completed_plans, 1)) * 100, 1)
        
        # Get active sessions count
        cur.execute("""
            SELECT COUNT(*) FROM allocation_sessions 
            WHERE status = 'active'
        """)
        active_sessions = cur.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            "success": True,
            "stats": {
                "total_students": total_students,
                "students_change": students_change,
                "total_classrooms": total_classrooms,
                "classrooms_change": 0,
                "allocated_seats": allocated_seats,
                "allocation_change": plans_change,
                "completed_plans": completed_plans,
                "plans_change": plans_change,
                "reports_generated": reports_count,
                "reports_change": 0
            },
            "summary": {
                "active_sessions": active_sessions,
                "pending_allocations": total_students - allocated_seats
            }
        })
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "error": str(e),
            "stats": {
                "total_students": 0,
                "students_change": 0,
                "total_classrooms": 0,
                "classrooms_change": 0,
                "allocated_seats": 0,
                "allocation_change": 0,
                "completed_plans": 0,
                "plans_change": 0,
                "reports_generated": 0,
                "reports_change": 0
            }
        }), 500


@app.route('/api/dashboard/activity', methods=['GET'])
def get_dashboard_activity():
    """
    Get recent activity logs - using raw SQLite
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        activities = []
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get recent completed allocations
        cur.execute("""
            SELECT plan_id, completed_at, status, allocated_count
            FROM allocation_sessions 
            WHERE status = 'completed' AND completed_at IS NOT NULL
            ORDER BY completed_at DESC 
            LIMIT 5
        """)
        
        for row in cur.fetchall():
            time_ago = get_time_ago(row['completed_at'])
            activities.append({
                "id": f"alloc_{row['plan_id']}",
                "time": time_ago,
                "message": f"Seat allocation completed: {row['plan_id']} ({row['allocated_count']} students)",
                "type": "success",
                "timestamp": row['completed_at']
            })
        
        # Get recent batches/uploads
        cur.execute("""
            SELECT u.id, u.batch_name, u.created_at, COUNT(s.id) as student_count
            FROM uploads u
            LEFT JOIN students s ON u.id = s.upload_id
            GROUP BY u.id
            ORDER BY u.created_at DESC 
            LIMIT 3
        """)
        
        for row in cur.fetchall():
            time_ago = get_time_ago(row['created_at'])
            activities.append({
                "id": f"batch_{row['id']}",
                "time": time_ago,
                "message": f"Batch '{row['batch_name']}' uploaded with {row['student_count']} students",
                "type": "success",
                "timestamp": row['created_at']
            })
        
        # Get active sessions (in progress)
        cur.execute("""
            SELECT plan_id, created_at, allocated_count, total_students
            FROM allocation_sessions 
            WHERE status = 'active'
            ORDER BY created_at DESC 
            LIMIT 2
        """)
        
        for row in cur.fetchall():
            time_ago = get_time_ago(row['created_at'])
            progress = f"{row['allocated_count']}/{row['total_students']}" if row['total_students'] else "0"
            activities.append({
                "id": f"session_{row['plan_id']}",
                "time": time_ago,
                "message": f"Allocation in progress: {row['plan_id']} ({progress})",
                "type": "process",
                "timestamp": row['created_at']
            })
        
        # Get recent classroom additions
        cur.execute("""
            SELECT id, name, rows, cols, created_at
            FROM classrooms
            ORDER BY created_at DESC 
            LIMIT 2
        """)
        
        for row in cur.fetchall():
            time_ago = get_time_ago(row['created_at'])
            activities.append({
                "id": f"room_{row['id']}",
                "time": time_ago,
                "message": f"Classroom '{row['name']}' added ({row['rows']}x{row['cols']})",
                "type": "info",
                "timestamp": row['created_at']
            })
        
        conn.close()
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x.get('timestamp') or '', reverse=True)
        activities = activities[:limit]
        
        # Default message if empty
        if not activities:
            activities.append({
                "id": "default_1",
                "time": "Just now",
                "message": "System ready - No recent activity",
                "type": "info",
                "timestamp": datetime.now().isoformat()
            })
        
        return jsonify({
            "success": True,
            "activities": activities,
            "total_count": len(activities)
        })
        
    except Exception as e:
        logger.error(f"Dashboard activity error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": True,
            "activities": [{
                "id": "error_1",
                "time": "Now",
                "message": "System initializing...",
                "type": "info",
                "timestamp": datetime.now().isoformat()
            }],
            "total_count": 1
        })


@app.route('/api/dashboard/session-info', methods=['GET'])
def get_session_info():
    """
    Get current session and upcoming exam info - using raw SQLite
    """
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
        total_students = 0
        allocated_students = 0
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Check for active allocation (indicates upcoming exam)
        cur.execute("""
            SELECT plan_id, created_at, total_students, allocated_count
            FROM allocation_sessions 
            WHERE status = 'active'
            ORDER BY created_at DESC 
            LIMIT 1
        """)
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
        
        # Get allocated students count (from all active/completed sessions)
        cur.execute("""
            SELECT COUNT(DISTINCT a.student_id) FROM allocations a
            JOIN allocation_sessions s ON a.session_id = s.session_id
            WHERE s.status IN ('active', 'completed')
        """)
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
        logger.error(f"Session info error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return fallback data
        now = datetime.now()
        month = now.month
        year = now.year
        
        if month >= 1 and month <= 5:
            session = f"Spring Semester {year}"
        elif month >= 6 and month <= 7:
            session = f"Summer Session {year}"
        else:
            session = f"Fall Semester {year}"
        
        return jsonify({
            "success": True,
            "current_session": session,
            "next_exam": None,
            "system_status": {
                "total_students": 0,
                "allocated_students": 0,
                "pending_students": 0,
                "health": "empty"
            }
        })


# Helper function - update if not already correct
def get_time_ago(dt_input):
    """Convert datetime string or object to human-readable 'time ago'"""
    if not dt_input:
        return "Unknown"
    
    try:
        # Parse if string
        if isinstance(dt_input, str):
            # Try different formats
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S.%f"]:
                try:
                    dt = datetime.strptime(dt_input.split('.')[0].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
                    break
                except:
                    continue
            else:
                return "Unknown"
        else:
            dt = dt_input
        
        now = datetime.now()
        diff = now - dt
        seconds = diff.total_seconds()
        
        if seconds < 0:
            return "Just now"
        elif seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds // 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif seconds < 2592000:
            weeks = int(seconds // 604800)
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            return dt.strftime("%b %d, %Y")
            
    except Exception as e:
        logger.warning(f"Time ago parse error: {e}")
        return "Unknown"
# ============================================================================
# AUTH DECORATOR
# ============================================================================

def token_required(fn):
    """Decorator to require valid JWT token."""
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
# ============================================================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/sessions/active', methods=['GET'])
def get_active_session():
    """
    Get the active session with all required data.
    
    CRITICAL FIX: Select ALL required columns and handle None values.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get active session - SELECT ALL REQUIRED COLUMNS
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
            WHERE status = 'active' 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        session_row = cursor.fetchone()
        
        if not session_row:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'No active session',
                'session': None
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
        
        # Build allocated_rooms list safely
        allocated_rooms = []
        if allocated_rooms_rows:
            for row in allocated_rooms_rows:
                allocated_rooms.append({
                    'classroom_id': row[0],
                    'classroom_name': row[1] or 'Unknown',
                    'count': row[2] or 0
                })
        
        conn.close()
        
        # Calculate pending count safely
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
        logger.error(f"❌ ERROR in get_active_session: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'session': None
        }), 500

@app.route("/api/sessions/<int:session_id>/heartbeat", methods=["POST"])
def session_heartbeat(session_id):
    """
    Update session activity timestamp.
    Called periodically from frontend to prevent timeout.
    
    Note: The activity tracking middleware already handles this,
    so this endpoint is optional/redundant but kept for explicit updates.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE allocation_sessions
            SET last_activity = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        
        if cur.rowcount == 0:
            conn.close()
            return jsonify({"error": "Session not found"}), 404
        
        conn.commit()
        conn.close()
        
        logger.debug(f"💓 Heartbeat for session {session_id}")
        
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"Heartbeat error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions/recoverable", methods=["GET"])
def get_recoverable_sessions():
    """
    Get sessions that can be recovered (expired < 24 hours ago).
    
    Returns:
        JSON list of recoverable sessions
    """
    try:
        user_id = getattr(request, 'user_id', 1)
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get expired sessions from last 24 hours
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        
        cur.execute("""
            SELECT s.*,
                   (SELECT COUNT(*) FROM uploads WHERE session_id = s.session_id) as upload_count,
                   (SELECT COUNT(*) FROM allocations WHERE session_id = s.session_id) as allocation_count
            FROM allocation_sessions s
            WHERE s.user_id = ?
            AND s.status = 'expired'
            AND s.last_activity > ?
            ORDER BY s.last_activity DESC
        """, (user_id, cutoff))
        
        sessions = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        logger.info(f"Found {len(sessions)} recoverable sessions for user {user_id}")
        
        return jsonify({
            "success": True,
            "sessions": sessions
        })
        
    except Exception as e:
        logger.error(f"Get recoverable sessions error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/sessions/force-new", methods=["POST"])
def force_new_session():
    """
    Force-expire any active sessions and start new one.
    
    USE WITH CAUTION: Only for recovering from stuck states.
    """
    try:
        data = request.get_json()
        upload_ids = data.get('upload_ids', [])
        
        if not upload_ids:
            return jsonify({'error': 'No uploads provided'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Force-expire ALL active sessions
        cursor.execute("""
            UPDATE allocation_sessions
            SET status = 'expired'
            WHERE status = 'active'
        """)
        
        expired_count = cursor.rowcount
        logger.warning(f"⚠️ Force-expired {expired_count} active session(s)")
        
        # Now create new session (same logic as normal start)
        import random
        import string
        plan_id = f"PLAN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        
        # Calculate total students
        placeholders = ','.join('?' * len(upload_ids))
        cursor.execute(f"""
            SELECT COUNT(*) FROM students 
            WHERE upload_id IN ({placeholders})
        """, upload_ids)
        
        total_students = cursor.fetchone()[0] or 0
        
        # Create session
        cursor.execute("""
            INSERT INTO allocation_sessions (plan_id, total_students, allocated_count, status)
            VALUES (?, ?, 0, 'active')
        """, (plan_id, total_students))
        
        session_id = cursor.lastrowid
        
        # Link uploads
        for upload_id in upload_ids:
            cursor.execute("""
                UPDATE uploads
                SET session_id = ?
                WHERE id = ?
            """, (session_id, upload_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Expired {expired_count} old session(s) and started new session',
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
        logger.error(f"Force new session error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/sessions/<int:session_id>/recover", methods=["POST"])
def recover_session(session_id):
    """
    Recover an expired session (restore to 'active' status).
    
    Args:
        session_id: Session ID to recover
    
    Returns:
        Success message or error
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE allocation_sessions
            SET status = 'active',
                last_activity = ?
            WHERE session_id = ?
            AND status = 'expired'
        """, (datetime.now().isoformat(), session_id))
        
        if cur.rowcount == 0:
            conn.close()
            return jsonify({"error": "Session not found or not recoverable"}), 404
        
        conn.commit()
        conn.close()
        
        logger.info(f"🔄 Recovered session {session_id}")
        
        return jsonify({
            "success": True,
            "message": "Session recovered successfully"
        })
        
    except Exception as e:
        logger.error(f"Recover session error: {e}")
        return jsonify({"error": str(e)}), 500
    



@app.route('/api/sessions/start', methods=['POST'])
def start_session():
    try:
        data = request.get_json()
        upload_ids = data.get('upload_ids', [])
        
        if not upload_ids:
            return jsonify({
                'success': False,
                'error': 'No upload IDs provided'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check for existing active session
        # Check for existing active session
        cursor.execute("""
            SELECT session_id, last_activity, allocated_count, total_students
            FROM allocation_sessions 
            WHERE status = 'active'
            ORDER BY last_activity DESC
            LIMIT 1
        """)
        existing = cursor.fetchone()

        if existing:
            existing_id, last_activity, allocated, total = existing
            
            # Check if session is abandoned (no activity in 30 minutes)
            if last_activity:
                last_active = datetime.fromisoformat(last_activity)
                inactive_duration = datetime.now() - last_active
                
                if inactive_duration > timedelta(minutes=30):
                    # Auto-expire abandoned session
                    logger.info(f"⏰ Auto-expiring abandoned session {existing_id}")
                    cursor.execute("""
                        UPDATE allocation_sessions
                        SET status = 'expired'
                        WHERE session_id = ?
                    """, (existing_id,))
                    # Continue to create new session
                else:
                    # Session is legitimately active
                    return jsonify({
                        'success': False,
                        'error': 'An active session already exists',
                        'existing_session': {
                            'session_id': existing_id,
                            'allocated': allocated,
                            'total': total,
                            'last_activity': last_activity
                        }
                    }), 400
        
        # Generate plan_id
        import random
        import string
        plan_id = f"PLAN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        
        # Calculate total students
        placeholders = ','.join('?' * len(upload_ids))
        cursor.execute(f"""
            SELECT COUNT(*) FROM students 
            WHERE upload_id IN ({placeholders})
        """, upload_ids)
        
        total_students = cursor.fetchone()[0] or 0
        
        # Create session
        cursor.execute("""
            INSERT INTO allocation_sessions (plan_id, total_students, allocated_count, status)
            VALUES (?, ?, 0, 'active')
        """, (plan_id, total_students))
        
        session_id = cursor.lastrowid
        
        # Link uploads to session
        # Link uploads to session (use direct foreign key)
        for upload_id in upload_ids:
            cursor.execute("""
                UPDATE uploads
                SET session_id = ?
                WHERE id = ?
            """, (session_id, upload_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'session': {
                'session_id': session_id,
                'plan_id': plan_id,
                'total_students': total_students,
                'allocated_count': 0,
                'pending_count': total_students,
                'allocated_rooms': []  # CRITICAL: Return empty list, not null
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR in start_session: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/sessions/<int:session_id>/allocate-room", methods=["POST"])
def allocate_room_in_session(session_id):
    """Save allocation for ONE room - with batch filtering"""
    try:
        data = request.get_json()
        classroom_id = data.get('classroom_id')
        seating_data = data.get('seating_data')
        selected_batch_names = data.get('selected_batch_names', [])  # NEW: from frontend
        
        if classroom_id is None or seating_data is None:
            return jsonify({"error": "Missing classroom_id or seating_data"}), 400
        
        # Validate session
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT session_id, plan_id, status, total_students, allocated_count
            FROM allocation_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        session_row = cur.fetchone()
        
        if not session_row:
            conn.close()
            return jsonify({"error": "Session not found"}), 404
        
        session_dict = dict(session_row)
        
        if session_dict['status'] != 'active':
            conn.close()
            return jsonify({"error": f"Session is {session_dict['status']}, cannot allocate"}), 400
        
        conn.close()
        
        # Save allocation WITH batch filtering
        allocated_count, pending_students = save_room_allocation(
            session_id,
            int(classroom_id),
            seating_data,
            selected_batch_names=selected_batch_names  # NEW: pass batches
        )
        
        if allocated_count == 0:
            logger.warning(f"⚠️ No students allocated")
            return jsonify({"error": "No students were allocated"}), 400
        
        # Refresh session data
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                session_id, plan_id, total_students, allocated_count,
                status, created_at, last_activity
            FROM allocation_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        fresh_session = cur.fetchone()
        
        if not fresh_session:
            conn.close()
            return jsonify({"error": "Failed to fetch updated session"}), 500
        
        # Get allocated rooms
        cur.execute("""
            SELECT a.classroom_id, c.name as classroom_name, COUNT(a.id) as count
            FROM allocations a
            LEFT JOIN classrooms c ON a.classroom_id = c.id
            WHERE a.session_id = ?
            GROUP BY a.classroom_id, c.name
            ORDER BY c.name
        """, (session_id,))
        
        allocated_rooms = [
            {
                'classroom_id': row[0],
                'classroom_name': row[1] or 'Unknown',
                'count': row[2] or 0
            }
            for row in cur.fetchall()
        ]
        
        conn.close()
        
        # Calculate fresh stats
        fresh_total = fresh_session[2] or 0
        fresh_allocated = fresh_session[3] or 0
        fresh_pending = max(0, fresh_total - fresh_allocated)
        
        return jsonify({
            "success": True,
            "message": f"Allocated {allocated_count} students",
            "allocated_count": allocated_count,
            "session": {
                "session_id": fresh_session[0],
                "plan_id": fresh_session[1],
                "total_students": fresh_total,
                "allocated_count": fresh_allocated,
                "pending_count": fresh_pending,
                "status": fresh_session[4],
                "allocated_rooms": allocated_rooms
            },
            "remaining_count": fresh_pending,
            "pending_count": fresh_pending,
            "can_finalize": fresh_pending == 0,
            "pending_students": pending_students[:5]
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Room allocation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/sessions/<int:session_id>/undo", methods=["POST"])
def undo_allocation(session_id):
    """
    Undo last room allocation in session.
    
    Returns:
        Success status with updated pending list
    """
    try:
        # Validate session
        session = get_session_with_expiry_check(session_id)
        if not session:
            return jsonify({"error": "Session not found or expired"}), 404
        
        success, message = undo_last_allocation(session_id)
        
        if success:
            pending = get_pending_students(session_id)
            
            logger.info(f"↩️ Undo successful: {message}")
            
            return jsonify({
                "success": True,
                "message": message,
                "pending_count": len(pending),
                "pending_students": pending
            })
        else:
            return jsonify({"error": message}), 400
        
    except Exception as e:
        logger.error(f"Undo error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions/<int:session_id>/stats", methods=["GET"])
def get_session_statistics(session_id):
    """
    Get allocation statistics for session.
    
    Returns:
        JSON with session, room, and batch stats
    """
    try:
        stats = get_session_stats(session_id)
        
        if not stats:
            return jsonify({"error": "Session not found or no stats available"}), 404
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions/<int:session_id>/finalize', methods=['POST'])
def finalize_session(session_id):
    """Finalize session - mark complete and clean cache"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get session info
        cur.execute("""
            SELECT plan_id, total_students, allocated_count, status
            FROM allocation_sessions
            WHERE session_id = ?
        """, (session_id,))
        
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
        
        logger.info(f"🏁 Finalizing session {session_id}, rooms: {allocated_rooms}")
        
        # Update session status
        cur.execute("""
            UPDATE allocation_sessions
            SET status = 'completed',
                last_activity = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
        
        # ✅ CRITICAL: Finalize cache - remove experimental rooms
        if allocated_rooms:
            cache_manager.finalize_rooms(plan_id, allocated_rooms)
            logger.info(f"✅ Cache finalized with rooms: {allocated_rooms}")
        
        return jsonify({
            "success": True,
            "message": "Session finalized successfully",
            "plan_id": plan_id,
            "rooms": allocated_rooms
        })
        
    except Exception as e:
        logger.error(f"❌ Finalize error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/sessions/<int:session_id>/pending", methods=["GET"])
def get_session_pending(session_id):
    """
    Get pending (unallocated) students for session.
    
    Returns:
        JSON list of pending students
    """
    try:
        pending = get_pending_students(session_id)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "pending_count": len(pending),
            "pending_students": pending
        })
        
    except Exception as e:
        logger.error(f"Get pending error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions/<int:session_id>/uploads", methods=["GET"])
def get_session_uploads(session_id):
    """
    Get all uploads for a specific session.
    
    CRITICAL: Required by Upload page to show existing batches.
    
    Returns:
        JSON list of uploads with student counts
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get uploads with student counts
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
        
        logger.debug(f"📤 Found {len(uploads)} uploads for session {session_id}")
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "uploads": uploads
        })
        
    except Exception as e:
        logger.error(f"Get session uploads error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CLASSROOM ROUTES
# ============================================================================

@app.route("/api/classrooms", methods=["GET"])
def get_classrooms():
    """
    Get all classrooms.
    
    Returns:
        JSON list of classrooms
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM classrooms
            ORDER BY name ASC
        """)
        
        rooms = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        logger.debug(f"📋 Retrieved {len(rooms)} classrooms")
        
        return jsonify(rooms)
        
    except Exception as e:
        logger.error(f"Get classrooms error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/classrooms", methods=["POST"])
def save_classroom():
    """
    Create or update a classroom.
    
    Request JSON:
        {
            "id": 1 (optional, for update),
            "name": "Room 101",
            "rows": 10,
            "cols": 8,
            "broken_seats": "1-1,2-3",
            "block_width": 2
        }
    
    Returns:
        Success message
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Classroom name is required"}), 400
        
        rows = int(data.get('rows', 8))
        cols = int(data.get('cols', 10))
        
        if rows <= 0 or rows > 50:
            return jsonify({"error": "Rows must be between 1 and 50"}), 400
        
        if cols <= 0 or cols > 50:
            return jsonify({"error": "Columns must be between 1 and 50"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        try:
            if data.get('id'):
                # Update existing
                cur.execute("""
                    UPDATE classrooms
                    SET name = ?, rows = ?, cols = ?, broken_seats = ?, block_width = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    data['name'],
                    rows,
                    cols,
                    data.get('broken_seats', ''),
                    int(data.get('block_width', 1)),
                    datetime.now().isoformat(),
                    data['id']
                ))
                
                if cur.rowcount == 0:
                    conn.close()
                    return jsonify({"error": "Classroom not found"}), 404
                
                logger.info(f"✏️ Updated classroom {data['id']}: {data['name']}")
                message = f"Classroom '{data['name']}' updated successfully"
            else:
                # Create new
                cur.execute("""
                    INSERT INTO classrooms (name, rows, cols, broken_seats, block_width)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    data['name'],
                    rows,
                    cols,
                    data.get('broken_seats', ''),
                    int(data.get('block_width', 1))
                ))
                
                logger.info(f"➕ Created classroom: {data['name']} ({rows}x{cols})")
                message = f"Classroom '{data['name']}' created successfully"
            
            conn.commit()
            conn.close()
            
            return jsonify({
                "success": True,
                "message": message
            }), 201
            
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"error": f"Classroom '{data['name']}' already exists"}), 400
        
    except Exception as e:
        logger.error(f"Save classroom error: {e}")
        return jsonify({"error": str(e)}), 400


@app.route("/api/classrooms/<int:room_id>", methods=["DELETE"])
def delete_classroom(room_id):
    """
    Delete a classroom.
    
    Returns:
        Success message or error
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check if classroom is used in any allocations
        cur.execute("""
            SELECT COUNT(*) FROM allocations
            WHERE classroom_id = ?
        """, (room_id,))
        
        usage_count = cur.fetchone()[0]
        
        if usage_count > 0:
            conn.close()
            return jsonify({
                "error": f"Cannot delete: Classroom is used in {usage_count} allocation(s)"
            }), 400
        
        # Delete classroom
        cur.execute("DELETE FROM classrooms WHERE id = ?", (room_id,))
        
        if cur.rowcount == 0:
            conn.close()
            return jsonify({"error": "Classroom not found"}), 404
        
        conn.commit()
        conn.close()
        
        logger.info(f"🗑️ Deleted classroom {room_id}")
        
        return jsonify({
            "success": True,
            "message": "Classroom deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Delete classroom error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# UPLOAD ROUTES (FIXED WITH BATCH_COLOR SUPPORT)
# ============================================================================

@app.route("/api/upload-preview", methods=["POST"])
def api_upload_preview():
    """
    Preview file before uploading (show columns and sample data).
    
    Returns:
        JSON with columns, detected columns, and sample rows
    """
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
        
        logger.info(f"📄 Preview generated for {file.filename}: {preview_data.get('totalRows', 0)} rows")
        
        return jsonify({"success": True, **preview_data}), 200
        
    except Exception as e:
        logger.error(f"Upload preview error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """
    Parse and cache uploaded file.
    
    Form Data:
        - file: File to upload
        - mode: 1 or 2 (enrollment only vs name+enrollment)
        - batch_name: Label for this batch
        - nameColumn: (optional) Override name column
        - enrollmentColumn: (optional) Override enrollment column
    
    Returns:
        JSON with batch_id, preview, and sample data
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        if StudentDataParser is None:
            return jsonify({"error": "Parser module not available"}), 500
        
        file = request.files["file"]
        mode = int(request.form.get("mode", 2))
        batch_name = request.form.get("batch_name", "BATCH1").strip()
        name_col = request.form.get("nameColumn", None)
        enrollment_col = request.form.get("enrollmentColumn", None)
        
        if not batch_name:
            return jsonify({"error": "Batch name is required"}), 400
        
        # Read file content
        file_content = file.read()
        
        logger.info(f"📤 Parsing upload: {file.filename} (mode={mode}, batch={batch_name})")
        
        # Parse file
        parser = StudentDataParser()
        pr = parser.parse_file(
            io.BytesIO(file_content),
            mode=mode,
            batch_name=batch_name,
            name_col=name_col if name_col else None,
            enrollment_col=enrollment_col if enrollment_col else None
        )
        
        # Cache result for commit step
        if not hasattr(app, 'config'):
            app.config = {}
        if 'UPLOAD_CACHE' not in app.config:
            app.config['UPLOAD_CACHE'] = {}
        
        app.config['UPLOAD_CACHE'][pr.batch_id] = {
            'data': pr,
            'filename': file.filename,
            'filesize': len(file_content)
        }
        
        # Prepare response
        sample_data = pr.data.get(pr.batch_name, [])[:10]
        
        preview_columns = []
        if pr.mode == 2 and sample_data:
            if isinstance(sample_data[0], dict):
                preview_columns = list(sample_data[0].keys())
        
        logger.info(f"✅ Upload parsed: {pr.rows_extracted} students, batch_id={pr.batch_id}, color={pr.batch_color}")
        
        return jsonify({
            "success": True,
            "batch_id": pr.batch_id,
            "batch_name": pr.batch_name,
            "batch_color": pr.batch_color,
            "rows_extracted": pr.rows_extracted,
            "rows_total": pr.rows_total,
            "sample": sample_data,
            "warnings": pr.warnings,
            "preview": {
                "columns": preview_columns,
                "totalRows": pr.rows_total,
                "extractedRows": pr.rows_extracted
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/commit-upload", methods=["POST"])
def commit_upload():
    """
    Commit uploaded data to database.
    
    CRITICAL FIX: Now handles batch_color properly from ParseResult.
    
    Request JSON:
        {
            "batch_id": "uuid-from-upload",
            "session_id": 123 (optional)
        }
    
    Returns:
        JSON with upload_id, inserted count, skipped count
    """
    try:
        body = request.get_json(force=True)
        batch_id = body.get("batch_id")
        
        if not batch_id:
            return jsonify({"error": "batch_id is required"}), 400
        
        # Get cached data
        cache = app.config.get("UPLOAD_CACHE", {})
        cached_data = cache.get(batch_id)
        
        if not cached_data:
            logger.error(f"❌ Preview expired or not found for batch_id: {batch_id}")
            return jsonify({
                "error": "Preview expired or not found. Please re-upload the file."
            }), 400
        
        pr = cached_data.get('data')
        if not pr:
            return jsonify({"error": "Invalid cache data"}), 400
        
        filename = cached_data.get('filename', 'unknown')
        filesize = cached_data.get('filesize', 0)
        
        # Get session_id if provided
        session_id = body.get("session_id")
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        try:
            # CRITICAL FIX: Get batch_color from ParseResult
            batch_color = pr.batch_color
            
            logger.info(f"💾 Committing upload: batch_name={pr.batch_name}, color={batch_color}, session_id={session_id}")
            
            # Insert upload record
            cur.execute("""
                INSERT INTO uploads (batch_id, batch_name, batch_color, original_filename, file_size, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (pr.batch_id, pr.batch_name, batch_color, filename, filesize, session_id))
            
            upload_id = cur.lastrowid
            
            if not upload_id:
                raise Exception("Failed to create upload record")
            
            logger.info(f"✅ Created upload record: ID={upload_id}, batch={pr.batch_name}")
            
            # Insert students
            inserted, skipped = 0, 0
            batch_data = pr.data.get(pr.batch_name, [])
            
            if not batch_data:
                conn.rollback()
                conn.close()
                return jsonify({"error": "No student data found in batch"}), 400
            
            for row in batch_data:
                try:
                    # Handle both dict (mode 2) and string (mode 1) formats
                    if isinstance(row, dict):
                        enr = row.get("enrollmentNo") or row.get("enrollment")
                        name = row.get("name", "")
                        department = row.get("department", "")
                    else:
                        enr = str(row)
                        name = ""
                        department = ""
                    
                    if not enr or not str(enr).strip():
                        skipped += 1
                        continue
                    
                    enr = str(enr).strip()
                    
                    # Insert student with batch_color
                    cur.execute("""
                        INSERT INTO students (upload_id, batch_id, batch_name, batch_color, enrollment, name, department)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (upload_id, pr.batch_id, pr.batch_name, batch_color, enr, name, department))
                    
                    inserted += 1
                    
                except sqlite3.IntegrityError:
                    logger.debug(f"Duplicate enrollment skipped: {enr}")
                    skipped += 1
                except Exception as e:
                    logger.error(f"Error inserting student {enr}: {e}")
                    skipped += 1
            
            if inserted == 0:
                conn.rollback()
                conn.close()
                return jsonify({
                    "error": "No students were inserted. Check for duplicates or invalid data."
                }), 400
            
            # Update session total_students if session_id provided
            if session_id:
                cur.execute("""
                    UPDATE allocation_sessions
                    SET total_students = (
                        SELECT COUNT(DISTINCT s.id)
                        FROM students s
                        JOIN uploads u ON s.upload_id = u.id
                        WHERE u.session_id = ?
                    ),
                    last_activity = ?
                    WHERE session_id = ?
                """, (session_id, datetime.now().isoformat(), session_id))
            
            conn.commit()
            
            logger.info(f"✅ Committed {inserted} students (skipped {skipped})")
            
            conn.close()
            
            # Clear cache
            if batch_id in app.config.get('UPLOAD_CACHE', {}):
                del app.config['UPLOAD_CACHE'][batch_id]
            
            return jsonify({
                "success": True,
                "upload_id": upload_id,
                "batch_id": pr.batch_id,
                "batch_name": pr.batch_name,
                "batch_color": batch_color,
                "inserted": inserted,
                "skipped": skipped
            }), 200
            
        except Exception as e:
            conn.rollback()
            conn.close()
            logger.error(f"Database error during commit: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Commit upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Failed to commit data: {str(e)}"
        }), 500


@app.route("/api/students", methods=["GET"])
def api_students():
    """
    Get all students (limited to last 1000 for performance).
    
    Returns:
        JSON list of students
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM students
            ORDER BY id DESC
            LIMIT 1000
        """)
        
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        logger.debug(f"📋 Retrieved {len(rows)} students")
        
        return jsonify(rows)
        
    except Exception as e:
        logger.error(f"Get students error: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/plans/recent", methods=["GET"])
def get_recent_plans():
    """
    Get recent allocation plans (all statuses except deleted).
    
    FIXED: Shows last 20 sessions regardless of status.
    """
    try:
        user_id = getattr(request, 'user_id', 1)
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get all sessions (except maybe very old expired ones)
        cur.execute("""
            SELECT 
                s.session_id,
                s.plan_id,
                s.total_students,
                s.allocated_count,
                s.status,
                s.created_at,
                s.completed_at,
                s.last_activity,
                COUNT(DISTINCT a.classroom_id) as room_count
            FROM allocation_sessions s
            LEFT JOIN allocations a ON s.session_id = a.session_id
            WHERE (s.user_id = ? OR s.user_id IS NULL)
            AND s.status != 'deleted'
            GROUP BY s.session_id
            ORDER BY 
                CASE 
                    WHEN s.status = 'active' THEN 0
                    WHEN s.status = 'completed' THEN 1
                    ELSE 2
                END,
                s.last_activity DESC,
                s.created_at DESC
            LIMIT 20
        """, (user_id,))
        
        plans = []
        for row in cur.fetchall():
            plan = dict(row)
            
            # Get batch info for this session
            cur.execute("""
                SELECT DISTINCT u.batch_name, u.batch_color
                FROM uploads u
                WHERE u.session_id = ?
                ORDER BY u.created_at
            """, (plan['session_id'],))
            
            batches = []
            for batch_row in cur.fetchall():
                batches.append({
                    'name': batch_row[0],
                    'color': batch_row[1] or '#3b82f6'
                })
            
            plan['batches'] = batches
            plans.append(plan)
        
        conn.close()
        
        logger.info(f"📋 Retrieved {len(plans)} recent plans for user {user_id}")
        
        return jsonify({
            "success": True,
            "plans": plans,
            "total": len(plans)
        })
        
    except Exception as e:
        logger.error(f"❌ Get recent plans error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "plans": []
        }), 500
# ============================================================================
# ALLOCATION/SEATING GENERATION ROUTES
# ============================================================================

@app.route("/api/generate-seating", methods=["POST"])
def generate_seating():
    """Generate seating - FILTER by selected batches only"""
    if SeatingAlgorithm is None:
        return jsonify({"error": "SeatingAlgorithm module not available"}), 500
    
    try:
        data = request.get_json(force=True)
        
        plan_id = data.get("plan_id")
        session_id = data.get("session_id")
        
        if not plan_id:
            plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        use_db = bool(data.get("use_demo_db", True))
        
        # CRITICAL: Get batch info from payload
        batch_labels = data.get("batch_labels", {})  # {1: "Batch A", 2: "Batch B"}
        selected_batch_names = list(batch_labels.values()) if batch_labels else []
        
        counts = {}
        labels = {}
        rolls = {}
        colors = {}
        num_batches = 0
        
        if use_db and session_id:
            logger.info(f"🔍 Selected batches: {selected_batch_names}")
            
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
            
            logger.info(f"📋 Filtered: {len(filtered_students)} / {len(pending_students)} pending")
            
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
            
            # Convert to algorithm format (1-indexed, respecting order)
            for idx, batch_name in enumerate(selected_batch_names, start=1):
                if batch_name in batch_groups:
                    students_list = batch_groups[batch_name]['students']
                    counts[idx] = len(students_list)
                    labels[idx] = batch_name
                    rolls[idx] = students_list
                    colors[idx] = batch_groups[batch_name]['color']
                else:
                    logger.warning(f"⚠️ Batch '{batch_name}' has no pending students")
                    counts[idx] = 0
                    labels[idx] = batch_name
                    rolls[idx] = []
                    colors[idx] = data.get("batch_colors", {}).get(idx, '#3b82f6')
            
            num_batches = len(selected_batch_names)
            
            logger.info(f"📊 Batch counts: {counts}")
            logger.info(f"🎨 Batch colors: {colors}")
        
        else:
            # Fallback for non-session mode
            counts = parse_int_dict(data.get("batch_student_counts"))
            labels = parse_str_dict(data.get("batch_labels"))
            rolls = data.get("batch_roll_numbers") or {}
            colors = parse_str_dict(data.get("batch_colors"))
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
                            logger.warning(f"Invalid seat format: {seat_str}")
            elif isinstance(broken_str, list):
                for seat in broken_str:
                    if isinstance(seat, (list, tuple)) and len(seat) == 2:
                        broken_seats.append((int(seat[0]), int(seat[1])))
        
        total_pending = sum(counts.values())
        logger.info(f"🎯 Generating: {total_pending} students, {num_batches} batches")
        
        # Initialize algorithm
        algo = SeatingAlgorithm(
            rows=int(data.get("rows", 10)),
            cols=int(data.get("cols", 6)),
            num_batches=num_batches,
            block_width=int(data.get("block_width", 2)),
            batch_by_column=bool(data.get("batch_by_column", True)),
            enforce_no_adjacent_batches=bool(data.get("enforce_no_adjacent_batches", False)),
            broken_seats=broken_seats,
            batch_student_counts=counts,
            batch_roll_numbers=rolls,  # ONLY selected batches
            batch_labels=labels,
            start_rolls=parse_str_dict(data.get("start_rolls")),
            batch_colors=colors,
            serial_mode=data.get("serial_mode", "per_batch"),
            serial_width=int(data.get("serial_width", 0))
        )
        
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
        web["validation"] = {"is_valid": ok, "errors": errors}
        
        # Cache result
        room_name = data.get('room_no') or data.get('room_name') or "N/A"
        # UPDATE THIS LINE:
        cache_manager.save_or_update(
          plan_id=plan_id, 
          input_config=data, 
          output_data=web, 
        room_no=room_name  # Add this argument
        )
        
        logger.info(f"✅ Seating generated for: {selected_batch_names}")
        
        return jsonify(web)
        
    except Exception as e:
        logger.error(f"❌ Seating generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to generate seating: {str(e)}"}), 500
@app.route("/api/constraints-status", methods=["POST"])
def constraints_status():
    """
    Get constraint validation status for seating arrangement.
    
    Returns:
        JSON with constraint validation results
    """
    if SeatingAlgorithm is None:
        return jsonify({"error": "Algorithm module not available"}), 500
    
    try:
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
    except Exception as e:
        logger.error(f"Constraints status error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# MANUAL SEATING GENERATION 
# ============================================================================
@app.route("/api/manual-generate-seating", methods=["POST"])
def manual_generate_seating():
    """API endpoint to generate manual seating arrangement (no database dependency, user input only)"""
    if SeatingAlgorithm is None:
        return jsonify({"error": "SeatingAlgorithm module not available"}), 500
    
    data = request.get_json(force=True)
    
    # Extract settings for the Algorithm - NO DATABASE USAGE
    # All values come directly from frontend/user input
    num_batches = int(data.get("num_batches", 3))
    
    # Parse batch student counts (format: "1:30, 2:30, 3:30")
    batch_student_counts_str = data.get("batch_student_counts", "")
    counts = {}
    if batch_student_counts_str:
        parts = [p.strip() for p in batch_student_counts_str.split(',') if p.strip()]
        for part in parts:
            if ':' in part:
                try:
                    k, v = part.split(':', 1)
                    counts[int(k.strip())] = int(v.strip())
                except Exception:
                    pass
    
    # Parse batch names (format: "1:CS, 2:IT, 3:ME")
    batch_names_str = data.get("batch_names", "")
    labels = {}
    if batch_names_str:
        parts = [p.strip() for p in batch_names_str.split(',') if p.strip()]
        for part in parts:
            if ':' in part:
                try:
                    k, v = part.split(':', 1)
                    labels[int(k.strip())] = v.strip()
                except Exception:
                    pass
    
    # Parse start_serials (format: "1:1, 2:101, 3:201")
    start_serials_str = data.get("start_serials", "")
    start_serials = {}
    if start_serials_str:
        parts = [p.strip() for p in start_serials_str.split(',') if p.strip()]
        for part in parts:
            if ':' in part:
                try:
                    k, v = part.split(':', 1)
                    start_serials[int(k.strip())] = int(v.strip())
                except Exception:
                    pass
    
    # Parse start_rolls (custom roll format override - format: "1:BTCS001, 2:BTIT001")
    start_rolls_str = data.get("start_rolls", "")
    start_rolls = {}
    if start_rolls_str:
        parts = [p.strip() for p in start_rolls_str.split(',') if p.strip()]
        for part in parts:
            if ':' in part:
                try:
                    k, v = part.split(':', 1)
                    start_rolls[int(k.strip())] = v.strip()
                except Exception:
                    pass
    
    # If no start_rolls provided, generate default sequential rolls using start_serials
    if not start_rolls:
        for i in range(1, num_batches + 1):
            batch_name = labels.get(i, f"BATCH{i}")
            serial_start = start_serials.get(i, (i - 1) * 100 + 1)
            # Generate simple numeric roll numbers starting from the serial
            start_rolls[i] = f"{batch_name}_{serial_start:04d}"

    # Parse broken seats
    broken_str = data.get("broken_seats", "")
    broken_seats = []
    if isinstance(broken_str, str) and "-" in broken_str:
        parts = [p.strip() for p in broken_str.split(',') if p.strip()]
        for part in parts:
            if '-' in part:
                try:
                    row_col = part.split('-')
                    row = int(row_col[0].strip()) - 1
                    col = int(row_col[1].strip()) - 1
                    broken_seats.append((row, col))
                except (ValueError, IndexError):
                    pass
    elif isinstance(broken_str, list):
        broken_seats = broken_str

    # Run the Algorithm with user-provided data only
    algo = SeatingAlgorithm(
        rows=int(data.get("rows", 10)),
        cols=int(data.get("cols", 10)),
        num_batches=num_batches,
        block_width=int(data.get("block_width", 3)),
        batch_by_column=bool(data.get("batch_by_column", True)),
        enforce_no_adjacent_batches=bool(data.get("enforce_no_adjacent_batches", False)),
        broken_seats=broken_seats,
        batch_student_counts=counts,
        batch_roll_numbers={},  # Empty dict, let algorithm generate
        batch_labels=labels,
        start_rolls=start_rolls,
        batch_colors=parse_str_dict(data.get("batch_colors")),
        serial_mode=data.get("serial_mode", "per_batch"),
        serial_width=int(data.get("serial_width", 0))
    )

    algo.generate_seating()
    web = algo.to_web_format()
    
    # Prepare response object
    web.setdefault("metadata", {})
    
    # Validate constraints
    ok, errors = algo.validate_constraints()
    web["validation"] = {"is_valid": ok, "errors": errors}
    
    # Save to single static cache file for manual seating (always override)
    MANUAL_CACHE_FILE = "manual_seating_current"
    cache_manager.save_or_update(MANUAL_CACHE_FILE, data, web)
    
    print(f"✅ Manual seating generated (no database used) - Batches: {num_batches}, Start Serials: {start_serials}")
    print(f"💾 Saved to static cache: {MANUAL_CACHE_FILE}")

    return jsonify(web)

        
    


# ============================================================================
# PDF GENERATION ROUTES
# ============================================================================

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from seating arrangement.
    
    HYBRID CACHING ARCHITECTURE:
    =============================
    Two-layer caching:
    
    Layer 1 (app.py - THIS LEVEL):
    - Cache seating data retrieval
    - Avoid repeated algorithm execution
    - Priority: Cache > Database
    
    Layer 2 (pdf_generation.py - PDF LEVEL):
    - Cache PDF file generation
    - Uses content hash to avoid duplicate PDFs
    - Handles all PDF rendering caching
    
    This endpoint ONLY manages seating data caching.
    PDF file caching is handled transparently by get_or_create_seating_pdf().
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get identifiers - support both naming conventions
        plan_id = data.get('plan_id') or data.get('snapshot_id')
        room_name = data.get('room_name') or data.get('room_no')  # Support both!
        
        seating_payload = None
        
        logger.info(f"📄 PDF Request - plan_id: {plan_id}, room_name: {room_name}")
        
        # ============================================================================
        # LAYER 1: Get Seating Data from Cache
        # ============================================================================
        if plan_id:
            logger.info(f"🔍 Loading from cache: {plan_id}" + (f", room: {room_name}" if room_name else " (all rooms)"))
            
            if room_name:
                # Get specific room
                cached_seating = get_seating_from_cache(plan_id, room_name)
                
                if cached_seating and cached_seating.get('seating'):
                    seating_payload = cached_seating
                    logger.info(f"✅ Loaded room '{room_name}' from cache")
                else:
                    logger.error(f"❌ Room '{room_name}' not found in cache")
                    
                    # Debug: Show available rooms
                    snapshot = cache_manager.load_snapshot(plan_id)
                    if snapshot:
                        available = list(snapshot.get('rooms', {}).keys())
                        logger.info(f"📁 Available rooms: {available}")
                        return jsonify({
                            "error": f"Room '{room_name}' not found",
                            "available_rooms": available
                        }), 404
                    else:
                        return jsonify({"error": "Plan not found in cache"}), 404
            else:
                # Get first room or all rooms
                cached_seating = get_seating_from_cache(plan_id)
                
                if cached_seating:
                    seating_payload = cached_seating
                    logger.info(f"✅ Loaded default room from cache")
        
        # Fallback: Direct seating data in request
        if not seating_payload and 'seating' in data:
            seating_payload = {
                'seating': data['seating'],
                'metadata': data.get('metadata', {}),
                'batches': data.get('batches', {})
            }
            logger.info("📄 Using seating from request payload")
        
        if not seating_payload or not seating_payload.get('seating'):
            return jsonify({
                "error": "No seating data available",
                "hint": "Provide plan_id with room_name, or seating data directly"
            }), 400
        
        # ============================================================================
        # LAYER 2: Generate PDF
        # ============================================================================
        user_id = data.get('user_id', 'test_user')
        template_name = data.get('template_name', 'default')
        
        try:
            pdf_path = get_or_create_seating_pdf(
                seating_payload,
                user_id=user_id,
                template_name=template_name
            )
        except Exception as pdf_err:
            logger.error(f"❌ PDF generation failed: {str(pdf_err)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"PDF generation failed: {str(pdf_err)}"}), 500
        
        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF file not created"}), 500
        
        # Generate filename
        room_suffix = f"_{room_name.replace(' ', '_')}" if room_name else ""
        download_name = f"seating_plan{room_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        logger.info(f"✅ PDF generated: {pdf_path}")
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"❌ PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-pdf/batch', methods=['POST'])
def generate_pdf_batch():
    """
    Generate PDFs for all rooms in a plan (BATCH MODE).
    
    TWO-LAYER CACHING:
    Layer 1: Get all seating data from cache (very fast - O(1))
    Layer 2: Let pdf_generation.py cache PDF files (by content hash)
    
    Request:
        {
            "plan_id": "PLAN-XXXXX",
            "user_id": "test_user",
            "template_name": "default"
        }
    
    Response:
        {
            "success": true,
            "plan_id": "PLAN-XXXXX",
            "rooms": {
                "M101": {"status": "success", "path": "...pdf"},
                "M102": {"status": "success", "path": "...pdf"}
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        plan_id = data.get('plan_id')
        if not plan_id:
            return jsonify({"error": "plan_id required"}), 400
        
        user_id = data.get('user_id', 'test_user')
        template_name = data.get('template_name', 'default')
        
        logger.info(f"📦 [BATCH L1] Starting batch PDF for plan: {plan_id}")
        
        # LAYER 1: Get all seating from cache (avoid re-running algorithm for each room)
        all_rooms = get_all_room_seating_from_cache(plan_id)
        
        if not all_rooms:
            logger.warning(f"❌ No rooms found in cache for plan {plan_id}")
            return jsonify({
                "error": "Plan not found or no rooms cached",
                "plan_id": plan_id
            }), 404
        
        logger.info(f"⚡ [BATCH L1] Loaded {len(all_rooms)} rooms from cache")
        
        results = {}
        successful_count = 0
        
        # LAYER 2: For each room, pass to pdf_generation.py (handles PDF caching)
        for room_no, room_seating in all_rooms.items():
            try:
                logger.info(f"  📄 [BATCH L2] Processing room: {room_no}")
                
                # pdf_generation.py will:
                # - Check if PDF already exists (by hash)
                # - Reuse if exists, generate if not
                pdf_path = get_or_create_seating_pdf(
                    room_seating,
                    user_id=user_id,
                    template_name=template_name
                )
                
                if os.path.exists(pdf_path):
                    results[room_no] = {
                        'status': 'success',
                        'path': pdf_path,
                        'students': room_seating.get('metadata', {}).get('total_students', 0)
                    }
                    successful_count += 1
                    logger.info(f"  ✅ [BATCH L2] PDF ready for {room_no}")
                else:
                    results[room_no] = {
                        'status': 'error',
                        'reason': 'PDF file not created'
                    }
                    logger.warning(f"  ⚠️ PDF file missing for {room_no}")
                    
            except Exception as room_err:
                results[room_no] = {
                    'status': 'error',
                    'reason': str(room_err)
                }
                logger.error(f"  ❌ Failed to generate PDF for {room_no}: {room_err}")
        
        logger.info(f"📦 [BATCH COMPLETE] Generated {successful_count}/{len(all_rooms)} PDFs")
        
        return jsonify({
            'success': successful_count > 0,
            'plan_id': plan_id,
            'total_rooms': len(all_rooms),
            'successful': successful_count,
            'rooms': results
        }), 200 if successful_count > 0 else 206  # 206 = Partial Content
        
    except Exception as e:
        logger.error(f"❌ Batch PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/allocations', methods=['GET'])
def get_all_allocations():
    """
    Get all allocation batches (for attendance generation).
    
    Returns:
        JSON list of batches
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT batch_id, batch_name, created_at
            FROM uploads
            ORDER BY created_at DESC
        """)
        
        rows = cur.fetchall()
        conn.close()
        
        return jsonify([
            {
                "id": r[0],
                "batch_name": r[1],
                "date": r[2]
            }
            for r in rows
        ])
        
    except Exception as e:
        logger.error(f"Get allocations error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/plan-batches/<plan_id>', methods=['GET'])
def get_plan_batches(plan_id):
    """
    Get batch information for ALL rooms in a plan.
    Returns the complete rooms structure for the frontend.
    """
    try:
        cache_data = cache_manager.load_snapshot(plan_id)
        if not cache_data:
            return jsonify({"error": "Plan not found"}), 404
        
        # ✅ Return ALL rooms, not just one
        all_rooms = cache_data.get('rooms', {})
        
        # Log for debugging
        logger.info(f"📋 Plan {plan_id} has {len(all_rooms)} rooms: {list(all_rooms.keys())}")
        
        for room_name, room_data in all_rooms.items():
            batches = room_data.get('batches', {})
            student_count = sum(len(b.get('students', [])) for b in batches.values())
            logger.info(f"   🏠 Room '{room_name}': {len(batches)} batches, {student_count} students")
        
        # ✅ Return the complete structure
        return jsonify({
            "plan_id": plan_id,
            "rooms": all_rooms,  # ✅ ALL rooms with their batches
            "metadata": cache_data.get('metadata', {}),
            "inputs": cache_data.get('inputs', {})
        })
        
    except Exception as e:
        logger.error(f"Get plan batches error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
# ============================================================================
# GET: Retrieve user's template configuration
# ============================================================================

@app.route("/api/template/config", methods=["GET"])
@token_required
def get_template_config():
    """Get user's current template configuration"""
    try:
        user_id = request.user_id
        template_name = request.args.get('template_name', 'default')
        
        # Get template
        template = template_manager.get_user_template(user_id, template_name)
        
        if not template:
            return jsonify({
                "success": False,
                "error": "Template not found"
            }), 404
        
        # Get hash for caching
        template_hash = template_manager.get_template_hash(user_id, template_name)
        
        logger.info(f"📋 Template config retrieved for user {user_id}")
        
        return jsonify({
            "success": True,
            "template": template,
            "template_hash": template_hash,
            "message": "Template loaded successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Template config error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# POST: Update user's template configuration (with optional file upload)
# ============================================================================

@app.route("/api/template/config", methods=["POST"])
@token_required
def update_template_config():
    """
    Update user's template configuration.
    Supports both JSON and FormData (for banner uploads).
    """
    try:
        user_id = request.user_id
        
        # Check if it's FormData (with file) or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle FormData (from React component)
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
            
            # Handle banner image upload if provided
            banner_path = None
            if 'bannerImage' in request.files:
                file = request.files['bannerImage']
                if file and file.filename:
                    # Check file size (max 5MB)
                    file.seek(0, os.SEEK_END)
                    file_length = file.tell()
                    file.seek(0)
                    
                    if file_length > 5 * 1024 * 1024:  # 5MB
                        return jsonify({
                            "success": False,
                            "error": "File too large (max 5MB)"
                        }), 400
                    
                    banner_path = template_manager.save_user_banner(user_id, file, template_name)
                    if banner_path:
                        template_data['banner_image_path'] = banner_path
                    else:
                        return jsonify({
                            "success": False,
                            "error": "Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP"
                        }), 400
            
            # If no new banner, keep existing path
            if not banner_path:
                existing_template = template_manager.get_user_template(user_id, template_name)
                template_data['banner_image_path'] = existing_template.get('banner_image_path', '')
        
        else:
            # Handle JSON (for API calls)
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No data provided"
                }), 400
            
            template_name = data.pop('template_name', 'default')
            template_data = data
            
            # Validate input fields
            allowed_fields = {
                'dept_name', 'exam_details', 'seating_plan_title',
                'branch_text', 'room_number', 'coordinator_name',
                'coordinator_title', 'banner_image_path'
            }
            
            invalid_fields = set(template_data.keys()) - allowed_fields
            if invalid_fields:
                return jsonify({
                    "success": False,
                    "error": f"Invalid fields: {', '.join(invalid_fields)}"
                }), 400
        
        # Validate field lengths
        string_fields = {
            'dept_name': 200,
            'exam_details': 200,
            'seating_plan_title': 100,
            'branch_text': 100,
            'room_number': 50,
            'coordinator_name': 100,
            'coordinator_title': 100,
            'banner_image_path': 500
        }
        
        for field, max_len in string_fields.items():
            if field in template_data and len(str(template_data.get(field, ''))) > max_len:
                return jsonify({
                    "success": False,
                    "error": f"Field '{field}' exceeds maximum length of {max_len}"
                }), 400
        
        # Save template
        success = template_manager.save_user_template(user_id, template_data, template_name)
        
        if not success:
            return jsonify({
                "success": False,
                "error": "Failed to save template"
            }), 500
        
        # Clean up old banners (keep only latest 3)
        template_manager.delete_old_banners(user_id, keep_latest=3)
        
        # Get updated template and hash
        updated_template = template_manager.get_user_template(user_id, template_name)
        new_hash = template_manager.get_template_hash(user_id, template_name)
        
        logger.info(f"📝 Template config updated for user {user_id}")
        
        return jsonify({
            "success": True,
            "message": "Template saved successfully!",
            "template": updated_template,
            "template_hash": new_hash
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Template update error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# POST: Upload banner image separately (alternative endpoint)
# ============================================================================

@app.route("/api/template/banner", methods=["POST"])
@token_required
def upload_template_banner():
    """Upload custom banner image for PDF template"""
    try:
        user_id = request.user_id
        template_name = request.args.get('template_name', 'default')
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        # Check file size (max 5MB)
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > 5 * 1024 * 1024:  # 5MB
            return jsonify({
                "success": False,
                "error": "File too large (max 5MB)"
            }), 400
        
        # Save banner
        banner_path = template_manager.save_user_banner(user_id, file, template_name)
        
        if not banner_path:
            return jsonify({
                "success": False,
                "error": "Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP"
            }), 400
        
        # Update template with banner path
        template = template_manager.get_user_template(user_id, template_name)
        template['banner_image_path'] = banner_path
        template_manager.save_user_template(user_id, template, template_name)
        
        # Clean up old banners
        template_manager.delete_old_banners(user_id, keep_latest=3)
        
        logger.info(f"🖼️ Banner uploaded for user {user_id}: {banner_path}")
        
        return jsonify({
            "success": True,
            "message": "Banner uploaded successfully",
            "banner_path": banner_path
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Banner upload error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# GET: Generate test PDF with current template
# ============================================================================

@app.route("/api/test-pdf", methods=["GET"])
@token_required
def generate_test_pdf():
    """Generate a test PDF with sample data using current template"""
    try:
        user_id = request.user_id
        template_name = request.args.get('template_name', 'default')
        
        # Create sample student data
        # Mimic the structure of a real seating allocation (2D array)
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

        # WRAP IT IN A DICTIONARY
        seating_payload = {
            'seating': sample_seating_matrix,
            'metadata': {
                'rows': 2, 
                'cols': 4, 
                'blocks': 1,
                'total_students': 8
            }
        }
        
        # Generate PDF
        pdf_path = get_or_create_seating_pdf(
            seating_payload,  # Pass the DICT, not the LIST
            user_id=str(user_id),
            template_name=template_name
        )
        
        logger.info(f"📄 Test PDF generated for user {user_id}")
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'test_seating_plan_{datetime.now().strftime("%H%M%S")}.pdf'
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating test PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f'Failed to generate test PDF: {str(e)}'
        }), 500


# ============================================================================
# GET: Serve banner images
# ============================================================================

@app.route("/api/template/banner/<path:filename>", methods=["GET"])
@token_required
def serve_banner_image(filename):
    """Serve uploaded banner images"""
    try:
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


# ============================================================================
# DELETE: Reset template to system default
# ============================================================================

@app.route("/api/template/config", methods=["DELETE"])
@token_required
def reset_template_config():
    """Reset user's template to system default"""
    try:
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
        
        logger.info(f"🔄 Template reset to default for user {user_id}")
        
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


# ============================================================================
# GET: Get template preview (HTML)
# ============================================================================

@app.route("/api/template/preview", methods=["GET"])
@token_required
def get_template_preview():
    """Get HTML preview of user's template configuration"""
    try:
        user_id = request.user_id
        template_name = request.args.get('template_name', 'default')
        
        template = template_manager.get_user_template(user_id, template_name)
        
        # Generate preview HTML
        preview_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    background-color: #f5f5f5;
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .banner {{ 
                    width: 100%; 
                    max-height: 200px; 
                    margin-bottom: 20px;
                    object-fit: contain;
                }}
                .field {{ 
                    margin: 15px 0; 
                    padding: 10px;
                    background: #f9f9f9;
                    border-radius: 5px;
                }}
                .label {{ 
                    font-weight: bold; 
                    color: #333; 
                    font-size: 14px;
                }}
                .value {{ 
                    color: #666; 
                    margin-top: 5px; 
                    font-size: 16px;
                }}
                hr {{ 
                    border: none;
                    border-top: 2px solid #e0e0e0;
                    margin: 25px 0;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Template Preview</h1>
                
                {f'<img src="{template.get("banner_image_path")}" class="banner" alt="Banner" />' if template.get('banner_image_path') else '<p style="color: #999;">No banner image set</p>'}
                
                <div class="field">
                    <div class="label">Department Name:</div>
                    <div class="value">{template.get('dept_name') or 'Not set'}</div>
                </div>
                
                <div class="field">
                    <div class="label">Exam Details:</div>
                    <div class="value">{template.get('exam_details') or 'Not set'}</div>
                </div>
                
                <div class="field">
                    <div class="label">Seating Plan Title:</div>
                    <div class="value">{template.get('seating_plan_title') or 'Not set'}</div>
                </div>
                
                <div class="field">
                    <div class="label">Branch:</div>
                    <div class="value">{template.get('branch_text') or 'Not set'}</div>
                </div>
                
                <div class="field">
                    <div class="label">Room Number:</div>
                    <div class="value">{template.get('room_number') or 'Not set'}</div>
                </div>
                
                <hr>
                
                <div class="field">
                    <div class="label">Coordinator Name:</div>
                    <div class="value">{template.get('coordinator_name') or 'Not set'}</div>
                </div>
                
                <div class="field">
                    <div class="label">Coordinator Title:</div>
                    <div class="value">{template.get('coordinator_title') or 'Not set'}</div>
                </div>
            </div>
        </body>
        </html>
        """
        
        logger.info(f"👁️ Template preview generated for user {user_id}")
        
        return preview_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        logger.error(f"❌ Template preview error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# GET: List available templates
# ============================================================================

@app.route("/api/template/list", methods=["GET"])
@token_required
def list_templates():
    """List all available templates for user"""
    try:
        user_id = request.user_id
        
        templates = [
            {
                "name": "default",
                "label": "Default Template",
                "is_custom": False,
                "description": "Standard seating plan template"
            }
        ]
        
        logger.info(f"📋 Templates listed for user {user_id}")
        
        return jsonify({
            "success": True,
            "templates": templates
        }), 200
        
    except Exception as e:
        logger.error(f"❌ List templates error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/export-attendance', methods=['POST'])
def export_attendance():
    """Export attendance sheet with correct metadata field mapping."""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        batch_or_room = data.get('batch_name')
        frontend_metadata = data.get('metadata', {})
        room_no = frontend_metadata.get('room_no') or frontend_metadata.get('room_name')

        logger.info(f"📋 Attendance request: plan={plan_id}, batch_or_room={batch_or_room}, room_no={room_no}")
        logger.info(f"📋 Frontend metadata received: {frontend_metadata}")

        # Load cached seating plan
        cache_data = cache_manager.load_snapshot(plan_id)
        if not cache_data:
            return jsonify({"error": "Seating plan cache not found"}), 404

        rooms = cache_data.get('rooms', {})
        
        # Find the room and batch data
        room_data = None
        target_room_name = None
        target_batch_name = None
        all_students = []
        batch_info = {}
        
        # Case 1: batch_or_room is a room name
        if batch_or_room in rooms:
            target_room_name = batch_or_room
            room_data = rooms[batch_or_room]
            
            for b_name, b_data in room_data.get('batches', {}).items():
                students = b_data.get('students', [])
                all_students.extend(students)
                if not batch_info:
                    batch_info = b_data.get('info', {})
            
            target_batch_name = target_room_name
            logger.info(f"✅ Found room '{target_room_name}' with {len(all_students)} students")
        
        # Case 2: room_no specified, batch_or_room is a batch name
        elif room_no and room_no in rooms:
            target_room_name = room_no
            room_data = rooms[room_no]
            target_batch_name = batch_or_room
            
            b_data = room_data.get('batches', {}).get(target_batch_name)
            if b_data:
                all_students = b_data.get('students', [])
                batch_info = b_data.get('info', {})
            else:
                # Search all rooms for the batch
                for r_name, r_data in rooms.items():
                    if target_batch_name in r_data.get('batches', {}):
                        target_room_name = r_name
                        room_data = r_data
                        b_data = r_data['batches'][target_batch_name]
                        all_students = b_data.get('students', [])
                        batch_info = b_data.get('info', {})
                        break
        
        # Case 3: Search all rooms
        else:
            for r_name, r_data in rooms.items():
                if batch_or_room in r_data.get('batches', {}):
                    target_room_name = r_name
                    room_data = r_data
                    target_batch_name = batch_or_room
                    b_data = r_data['batches'][batch_or_room]
                    all_students = b_data.get('students', [])
                    batch_info = b_data.get('info', {})
                    break
        
        if not all_students:
            return jsonify({
                "error": f"No students found for '{batch_or_room}'",
                "available_rooms": list(rooms.keys())
            }), 404

        # ============================================================================
        # ✅ FIXED: Map metadata to EXACT field names that create_attendance_pdf expects
        # ============================================================================
        complete_metadata = {
            # PDF expects 'exam_title', not 'exam_name'
            'exam_title': frontend_metadata.get('exam_title') or frontend_metadata.get('exam_name') or 'EXAMINATION-ATTENDANCE SHEET',
            
            # PDF expects 'course_name'
            'course_name': frontend_metadata.get('course_name') or frontend_metadata.get('department') or 'N/A',
            
            # PDF expects 'course_code'
            'course_code': frontend_metadata.get('course_code') or 'N/A',
            
            # PDF expects 'date', not 'exam_date'
            'date': frontend_metadata.get('date') or frontend_metadata.get('exam_date') or '',
            
            # PDF expects 'time'
            'time': frontend_metadata.get('time') or '',
            
            # PDF expects 'year'
            'year': frontend_metadata.get('year') or str(datetime.now().year),
            
            # PDF expects 'room_no'
            'room_no': target_room_name or room_no or 'N/A',
        }

        logger.info(f"📋 Complete metadata for PDF: {complete_metadata}")
        logger.info(f"📋 Generating attendance: room={target_room_name}, batch={target_batch_name}, students={len(all_students)}")

        # Generate PDF
        timestamp = int(time.time())
        safe_name = (target_batch_name or target_room_name or 'attendance').replace(' ', '_').replace('/', '-')
        temp_filename = f"temp_attendance_{safe_name}_{timestamp}.pdf"
        
        # ✅ Call with correct positional arguments
        create_attendance_pdf(
            temp_filename,                                    # filename
            all_students,                                     # student_list
            target_batch_name or target_room_name or 'All',   # batch_label
            complete_metadata,                                # metadata
            batch_info                                        # extracted_info
        )

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
    
# ============================================================================
# AUTH ROUTES (OPTIONAL - IF AUTH MODULE AVAILABLE)
# ============================================================================

@app.route("/api/auth/signup", methods=["POST"])
def signup_route():
    """User registration endpoint."""
    if auth_signup is None:
        return jsonify({"error": "Auth module not available"}), 501
    
    try:
        data = request.get_json(force=True)
        ok, user_data, token = auth_signup(  # ✅ Get all 3 return values
            data.get("username"),
            data.get("email"),
            data.get("password"),
            data.get("role", "STUDENT"),
        )
        
        if ok:
            # ✅ Return proper structure with 'data' wrapper
            return jsonify({
                "success": True,
                "message": "Signup successful",
                "data": {
                    "token": token,
                    "user": user_data
                }
            }), 201
        else:
            # user_data contains error message on failure
            return jsonify({
                "success": False,
                "error": user_data,  # Error message from backend
                "message": user_data
            }), 400
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/auth/login", methods=["POST"])
def login_route():
    """User login endpoint."""
    if auth_login is None:
        return jsonify({"error": "Auth module not available"}), 501
    
    try:
        data = request.get_json(force=True)
        ok, user, token = auth_login(data.get("email"), data.get("password"))
        
        if not ok:
            return jsonify({"error": token}), 401
        
        return jsonify({"token": token, "user": user})
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/google", methods=["POST"])
def google_auth_route():
    """Google OAuth login endpoint."""
    if google_auth_handler is None:
        return jsonify({"error": "Google auth not available"}), 501
    
    try:
        data = request.get_json(force=True)
        token = data.get("token")
        
        if not token:
            return jsonify({"error": "No token provided"}), 400
        
        ok, user, auth_token = google_auth_handler(token)
        
        if not ok:
            return jsonify({"error": user}), 401
        
        return jsonify({"token": auth_token, "user": user})
        
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/profile", methods=["GET"])
@token_required
def get_profile_route():
    """Get user profile (requires auth token)."""
    if get_user_by_token is None:
        return jsonify({"error": "Auth module not available"}), 501
    
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Missing token"}), 401
        
        token = auth_header.split(" ")[1]
        user = get_user_by_token(token)
        
        if not user:
            return jsonify({"error": "User not found or token invalid"}), 404
        
        return jsonify({"success": True, "user": user})
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/profile", methods=["PUT"])
@token_required
def update_profile_route():
    """Update user profile (requires auth token)."""
    if update_user_profile is None:
        return jsonify({"error": "Auth module not available"}), 501
    
    try:
        data = request.get_json(force=True)
        username = data.get("username")
        email = data.get("email")
        
        ok, msg = update_user_profile(request.user_id, username, email)
        
        if ok:
            auth_header = request.headers.get("Authorization")
            token = auth_header.split(" ")[1]
            user = get_user_by_token(token)
            return jsonify({"success": True, "message": msg, "user": user})
        else:
            return jsonify({"success": False, "error": msg}), 400
            
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/logout", methods=["POST"])
def logout_route():
    """Logout endpoint (stateless - just confirmation)."""
    return jsonify({"success": True, "message": "Logged out successfully"})


# ============================================================================
# FEEDBACK ROUTES
# ============================================================================

@app.route("/api/feedback", methods=["POST"])
@token_required
def submit_feedback():
    """
    Submit user feedback with optional file attachment.
    
    Form Data:
        - issueType: Type of issue
        - priority: low/medium/high/critical
        - description: Description of issue
        - featureSuggestion: (optional)
        - additionalInfo: (optional)
        - file: (optional) Attachment
    
    Returns:
        JSON with feedback_id
    """
    try:
        issue_type = request.form.get('issueType')
        priority = request.form.get('priority')
        description = request.form.get('description')
        feature_suggestion = request.form.get('featureSuggestion', '')
        additional_info = request.form.get('additionalInfo', '')
        
        if not all([issue_type, priority, description]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Handle file upload
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
                except Exception as file_error:
                    logger.error(f"File upload error: {file_error}")
        
        user_id = getattr(request, 'user_id', 1)
        
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
        
        logger.info(f"📝 Feedback submitted: ID={feedback_id}, User={user_id}, Priority={priority}")
        
        return jsonify({
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id
        }), 201
        
    except Exception as e:
        logger.error(f"Feedback submission error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/feedback", methods=["GET"])
@token_required
def get_user_feedback():
    """
    Get feedback submitted by current user.
    
    Returns:
        JSON list of feedback entries
    """
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
        
        return jsonify({
            "success": True,
            "feedback": feedback_list
        })
        
    except Exception as e:
        logger.error(f"Get feedback error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ADMIN & MAINTENANCE ROUTES
# ============================================================================

@app.route("/api/reset-data", methods=["POST"])
@token_required
def reset_data():
    """
    Reset all student data and allocations.
    
    WARNING: Destructive operation - cannot be undone.
    
    Returns:
        Success confirmation
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Delete data (cascading will handle related records)
        cur.execute("DELETE FROM students")
        cur.execute("DELETE FROM uploads")
        cur.execute("DELETE FROM allocations")
        cur.execute("DELETE FROM allocation_sessions")
        cur.execute("DELETE FROM allocation_history")
        
        # Reset auto-increment counters
        cur.execute("DELETE FROM sqlite_sequence WHERE name IN ('students', 'uploads', 'allocations', 'allocation_sessions', 'allocation_history')")
        
        conn.commit()
        conn.close()
        
        logger.warning("⚠️ DATABASE RESET COMPLETED - All student data cleared")
        
        return jsonify({
            "success": True,
            "message": "All data has been cleared successfully."
        })
        
    except Exception as e:
        logger.error(f"Reset error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        JSON with system status
    """
    try:
        # Check database connectivity
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM classrooms")
        classroom_count = cur.fetchone()[0]
        conn.close()
        
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "modules": {
                "auth": auth_signup is not None,
                "google_auth": google_auth_handler is not None,
                "parser": StudentDataParser is not None,
                "algorithm": SeatingAlgorithm is not None
            },
            "stats": {
                "classrooms": classroom_count
            }
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route("/api/debug/cache", methods=["GET"])
def debug_cache():
    """
    Debug endpoint to view cache statistics and hybrid caching status.
    Shows current cache utilization and which plans have cached seating data.
    """
    try:
        cache_snapshots = cache_manager.list_snapshots()
        
        # Calculate cache stats
        total_students_cached = sum(s.get('total_students', 0) for s in cache_snapshots)
        total_rooms = sum(len(s.get('rooms', [])) for s in cache_snapshots)
        
        # Get cache directory size
        cache_dir = CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
        cache_size_mb = 0
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                filepath = os.path.join(cache_dir, file)
                if os.path.isfile(filepath):
                    cache_size_mb += os.path.getsize(filepath) / (1024 * 1024)
        
        return jsonify({
            "success": True,
            "hybrid_caching": {
                "strategy": "cache_first",
                "fallback": "database",
                "cache_dir": cache_dir,
                "cache_size_mb": round(cache_size_mb, 2)
            },
            "statistics": {
                "total_plans_cached": len(cache_snapshots),
                "total_students_allocated": total_students_cached,
                "total_rooms_cached": total_rooms,
                "avg_students_per_plan": round(total_students_cached / len(cache_snapshots), 1) if cache_snapshots else 0
            },
            "cached_plans": [
                {
                    "plan_id": s.get('plan_id'),
                    "rooms": s.get('rooms', []),
                    "total_students": s.get('total_students', 0),
                    "last_updated": s.get('last_updated'),
                    "status": s.get('status', 'active')
                }
                for s in cache_snapshots[:10]  # Show last 10
            ]
        }), 200
    except Exception as e:
        logger.error(f"Cache debug error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# DATABASE MANAGER ENDPOINTS
# ============================================================================

ALLOWED_TABLES = ['students', 'classrooms', 'uploads', 'allocations', 'feedback']

TABLE_CONFIG = {
    'students': {'primary_key': 'id', 'searchable': ['enrollment', 'name', 'batch_name'], 'editable': ['name', 'batch_name', 'department']},
    'classrooms': {'primary_key': 'id', 'searchable': ['name'], 'editable': ['name', 'rows', 'cols', 'broken_seats', 'block_width']},
    'uploads': {'primary_key': 'id', 'searchable': ['batch_name', 'original_filename'], 'editable': ['batch_name', 'batch_color']},
    'allocations': {'primary_key': 'id', 'searchable': ['enrollment', 'batch_name'], 'editable': ['seat_position', 'paper_set']},
    'feedback': {'primary_key': 'id', 'searchable': ['issue_type', 'description'], 'editable': ['status', 'admin_response']}
}


@app.route("/api/database/overview", methods=["GET"])
def get_database_overview():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        tables = {}
        for table in ALLOWED_TABLES:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                tables[table] = cur.fetchone()[0]
            except:
                tables[table] = 0
        conn.close()
        return jsonify({"success": True, "overview": {"tables": tables}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/database/hierarchy", methods=["GET"])
def get_database_hierarchy():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("""
            SELECT s.session_id, s.plan_id, s.total_students, s.allocated_count, s.status, s.created_at,
                   u.batch_name, u.batch_color, u.batch_id, u.id as upload_id, COUNT(st.id) as batch_student_count
            FROM allocation_sessions s
            LEFT JOIN uploads u ON s.session_id = u.session_id
            LEFT JOIN students st ON u.id = st.upload_id
            GROUP BY s.session_id, u.batch_id
            ORDER BY s.created_at DESC, u.batch_name
        """)
        rows = cur.fetchall()
        
        hierarchy = {}
        for row in rows:
            sid = row['session_id']
            if sid not in hierarchy:
                hierarchy[sid] = {
                    'session_id': sid, 'plan_id': row['plan_id'], 'total_students': row['total_students'],
                    'allocated_count': row['allocated_count'], 'status': row['status'], 'created_at': row['created_at'], 'batches': {}
                }
            if row['batch_name']:
                hierarchy[sid]['batches'][row['batch_name']] = {
                    'batch_name': row['batch_name'], 'batch_id': row['batch_id'], 'upload_id': row['upload_id'],
                    'batch_color': row['batch_color'], 'student_count': row['batch_student_count'] or 0
                }
        
        for sid in hierarchy:
            for bn in hierarchy[sid]['batches']:
                bid = hierarchy[sid]['batches'][bn]['batch_id']
                cur.execute("SELECT id, enrollment, name, department, batch_color FROM students WHERE batch_id = ? ORDER BY enrollment", (bid,))
                hierarchy[sid]['batches'][bn]['students'] = [dict(r) for r in cur.fetchall()]
        
        conn.close()
        return jsonify({"success": True, "hierarchy": list(hierarchy.values())})
    except Exception as e:
        logger.error(f"Hierarchy error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/database/table/<table_name>", methods=["GET"])
def get_table_data(table_name):
    if table_name not in ALLOWED_TABLES:
        return jsonify({"success": False, "error": "Table not allowed"}), 403
    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 50))))
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'id')
        sort_order = 'DESC' if request.args.get('sort_order', 'DESC').upper() == 'DESC' else 'ASC'
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = [{'name': c[1], 'type': c[2], 'nullable': not c[3], 'primary_key': bool(c[5])} for c in cur.fetchall()]
        col_names = [c['name'] for c in columns]
        
        if sort_by not in col_names:
            sort_by = col_names[0]
        
        searchable = TABLE_CONFIG.get(table_name, {}).get('searchable', col_names[:3])
        base_query = f"SELECT * FROM {table_name}"
        count_query = f"SELECT COUNT(*) FROM {table_name}"
        params = []
        
        if search and searchable:
            conditions = [f"{c} LIKE ?" for c in searchable if c in col_names]
            if conditions:
                where = " OR ".join(conditions)
                base_query += f" WHERE ({where})"
                count_query += f" WHERE ({where})"
                params = [f"%{search}%" for _ in conditions]
        
        cur.execute(count_query, params)
        total = cur.fetchone()[0]
        
        base_query += f" ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        cur.execute(base_query, params)
        data = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        return jsonify({
            "success": True, "columns": columns, "data": data,
            "pagination": {"page": page, "per_page": per_page, "total": total, "pages": (total + per_page - 1) // per_page}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/database/table/<table_name>/<int:record_id>", methods=["PUT"])
def update_record(table_name, record_id):
    if table_name not in ALLOWED_TABLES:
        return jsonify({"success": False, "error": "Table not allowed"}), 403
    try:
        data = request.get_json()
        editable = TABLE_CONFIG.get(table_name, {}).get('editable', [])
        update_data = {k: v for k, v in data.items() if k in editable}
        if not update_data:
            return jsonify({"success": False, "error": "No editable fields"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in update_data])
        cur.execute(f"UPDATE {table_name} SET {set_clause} WHERE id = ?", list(update_data.values()) + [record_id])
        if cur.rowcount == 0:
            conn.close()
            return jsonify({"success": False, "error": "Not found"}), 404
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Updated"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/database/table/<table_name>/<int:record_id>", methods=["DELETE"])
def delete_record(table_name, record_id):
    if table_name not in ALLOWED_TABLES:
        return jsonify({"success": False, "error": "Table not allowed"}), 403
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
        if cur.rowcount == 0:
            conn.close()
            return jsonify({"success": False, "error": "Not found"}), 404
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Deleted"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/database/table/<table_name>/bulk-delete", methods=["POST"])
def bulk_delete_records(table_name):
    if table_name not in ALLOWED_TABLES:
        return jsonify({"success": False, "error": "Table not allowed"}), 403
    try:
        ids = request.get_json().get('ids', [])
        if not ids:
            return jsonify({"success": False, "error": "No IDs"}), 400
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        placeholders = ','.join(['?' for _ in ids])
        cur.execute(f"DELETE FROM {table_name} WHERE id IN ({placeholders})", ids)
        deleted = cur.rowcount
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Deleted {deleted} records"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/database/table/<table_name>/export", methods=["GET"])
def export_table(table_name):
    if table_name not in ALLOWED_TABLES:
        return jsonify({"success": False, "error": "Table not allowed"}), 403
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        if not rows:
            conn.close()
            return jsonify({"success": False, "error": "No data"}), 404
        cols = [d[0] for d in cur.description]
        conn.close()
        
        output = io.StringIO()
        output.write(','.join(cols) + '\n')
        for row in rows:
            vals = []
            for c in cols:
                v = row[c]
                if v is None:
                    vals.append('')
                elif isinstance(v, str) and (',' in v or '"' in v):
                    vals.append(f'"{v.replace(chr(34), chr(34)+chr(34))}"')
                else:
                    vals.append(str(v))
            output.write(','.join(vals) + '\n')
        output.seek(0)
        
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name=f"{table_name}_export.csv")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/database/batch/<int:batch_id>/delete", methods=["DELETE"])
def delete_batch(batch_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("SELECT batch_name, session_id FROM uploads WHERE id = ?", (batch_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"success": False, "error": "Batch not found"}), 404
        
        batch_name, session_id = row
        cur.execute("SELECT id FROM students WHERE upload_id = ?", (batch_id,))
        student_ids = [r[0] for r in cur.fetchall()]
        
        if student_ids:
            placeholders = ','.join(['?' for _ in student_ids])
            cur.execute(f"DELETE FROM allocations WHERE student_id IN ({placeholders})", student_ids)
        
        cur.execute("DELETE FROM students WHERE upload_id = ?", (batch_id,))
        deleted_students = cur.rowcount
        cur.execute("DELETE FROM uploads WHERE id = ?", (batch_id,))
        
        if session_id:
            cur.execute("""
                UPDATE allocation_sessions SET
                    total_students = (SELECT COUNT(*) FROM students s JOIN uploads u ON s.upload_id = u.id WHERE u.session_id = ?),
                    allocated_count = (SELECT COUNT(*) FROM allocations WHERE session_id = ?),
                    last_activity = ?
                WHERE session_id = ?
            """, (session_id, session_id, datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Deleted batch '{batch_name}' with {deleted_students} students"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/database/session/<int:session_id>/delete", methods=["DELETE"])
def delete_session_endpoint(session_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("SELECT plan_id FROM allocation_sessions WHERE session_id = ?", (session_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        plan_id = row[0]
        cur.execute("SELECT id FROM uploads WHERE session_id = ?", (session_id,))
        upload_ids = [r[0] for r in cur.fetchall()]
        
        cur.execute("DELETE FROM allocations WHERE session_id = ?", (session_id,))
        
        if upload_ids:
            placeholders = ','.join(['?' for _ in upload_ids])
            cur.execute(f"DELETE FROM students WHERE upload_id IN ({placeholders})", upload_ids)
        
        cur.execute("DELETE FROM uploads WHERE session_id = ?", (session_id,))
        cur.execute("DELETE FROM allocation_history WHERE session_id = ?", (session_id,))
        cur.execute("DELETE FROM allocation_sessions WHERE session_id = ?", (session_id,))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Deleted session '{plan_id}'"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/database/backup", methods=["POST"])
def create_backup():
    try:
        import shutil
        backup_dir = BASE_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_{timestamp}.db"
        shutil.copy2(DB_PATH, backup_dir / backup_file)
        
        # Keep only last 10 backups
        backups = sorted(backup_dir.glob("backup_*.db"), key=os.path.getmtime, reverse=True)
        for old in backups[10:]:
            old.unlink()
        
        return jsonify({"success": True, "backup_file": backup_file})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    return jsonify({
        "error": "File too large",
        "max_size": "50MB"
    }), 413


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🚀 Starting Seat Allocation System - Flask Backend")
    logger.info("=" * 70)
    logger.info(f"📁 Database: {DB_PATH}")
    logger.info(f"🔧 Environment: {os.getenv('FLASK_ENV', 'production')}")
    logger.info(f"🌐 CORS enabled for: http://localhost:5173")
    logger.info("=" * 70)
    
    # Start server
    app.run(
        debug=True,
        port=5000,
        host='0.0.0.0'  # Allow external connections
    )