# SQL schema definitions and database initialization logic.
# Includes table creation, primary keys, foreign key constraints, and initial system data setup.
import sqlite3
import logging
import sys
from algo.config.settings import Config

logger = logging.getLogger(__name__)

def ensure_demo_db():
    """
    Initialize database with all required tables.
    
    ENHANCED: Now includes all missing columns and proper constraints.
    This function is idempotent - safe to run multiple times.
    """
    logger.info("🔧 Initializing database...")
    
    conn = sqlite3.connect(Config.DB_PATH)
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
        logger.info(f"✅ Database initialized successfully at {Config.DB_PATH}")
        
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
