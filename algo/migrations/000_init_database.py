import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "demo.db"

def init_database():
    """Initialize complete database schema from scratch"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        print("🔄 Initializing complete database schema...\n")
        
        # =====================================================================
        # 1. USERS TABLE
        # =====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created users table")
        
        # =====================================================================
        # 2. USER ACTIVITY TABLE (for session expiry tracking)
        # =====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id INTEGER PRIMARY KEY,
                last_activity DATETIME NOT NULL,
                last_endpoint TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("✅ Created user_activity table")
        
        # =====================================================================
        # 3. ALLOCATION SESSIONS TABLE
        # =====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS allocation_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT UNIQUE NOT NULL,
                user_id INTEGER DEFAULT 1,
                name TEXT,
                status TEXT DEFAULT 'active',
                total_students INTEGER DEFAULT 0,
                total_allocated INTEGER DEFAULT 0,
                total_capacity INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("✅ Created allocation_sessions table")
        
        # =====================================================================
        # 4. UPLOADS TABLE
        # =====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT UNIQUE NOT NULL,
                batch_name TEXT NOT NULL,
                batch_color TEXT NOT NULL,
                original_filename TEXT,
                file_size INTEGER,
                session_id INTEGER,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES allocation_sessions(session_id) ON DELETE CASCADE
            )
        """)
        print("✅ Created uploads table")
        
        # =====================================================================
        # 5. STUDENTS TABLE
        # =====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id INTEGER NOT NULL,
                batch_id TEXT NOT NULL,
                batch_name TEXT NOT NULL,
                batch_color TEXT,
                enrollment TEXT NOT NULL UNIQUE,
                name TEXT,
                department TEXT,
                FOREIGN KEY (upload_id) REFERENCES uploads(id) ON DELETE CASCADE
            )
        """)
        print("✅ Created students table")
        
        # =====================================================================
        # 6. CLASSROOMS TABLE
        # =====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS classrooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                rows INTEGER NOT NULL,
                cols INTEGER NOT NULL,
                broken_seats TEXT,
                block_width INTEGER DEFAULT 2,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created classrooms table")
        
        # =====================================================================
        # 7. ALLOCATIONS TABLE
        # =====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                classroom_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                seat_row INTEGER NOT NULL,
                seat_col INTEGER NOT NULL,
                allocated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES allocation_sessions(session_id) ON DELETE CASCADE,
                FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE RESTRICT,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE(session_id, student_id),
                UNIQUE(session_id, classroom_id, seat_row, seat_col)
            )
        """)
        print("✅ Created allocations table")
        
        # =====================================================================
        # 8. STAGED UPLOADS TABLE (for preview before commit)
        # =====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS staged_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT UNIQUE NOT NULL,
                batch_name TEXT NOT NULL,
                batch_color TEXT NOT NULL,
                original_filename TEXT,
                file_size INTEGER,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created staged_uploads table")
        
        # =====================================================================
        # 9. STAGED STUDENTS TABLE
        # =====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS staged_students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                batch_name TEXT NOT NULL,
                batch_color TEXT,
                enrollment TEXT NOT NULL,
                name TEXT,
                department TEXT,
                FOREIGN KEY (batch_id) REFERENCES staged_uploads(batch_id) ON DELETE CASCADE
            )
        """)
        print("✅ Created staged_students table")
        
        # =====================================================================
        # 10. FEEDBACK TABLE
        # =====================================================================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT NOT NULL,
                message TEXT NOT NULL,
                rating INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        print("✅ Created feedback table")
        
        # =====================================================================
        # 11. CREATE INDEXES FOR PERFORMANCE
        # =====================================================================
        indexes = [
            ("idx_students_enrollment", "students", "enrollment"),
            ("idx_students_upload", "students", "upload_id"),
            ("idx_uploads_session", "uploads", "session_id"),
            ("idx_uploads_batch", "uploads", "batch_id"),
            ("idx_allocations_session", "allocations", "session_id"),
            ("idx_allocations_student", "allocations", "student_id"),
            ("idx_allocations_classroom", "allocations", "classroom_id"),
            ("idx_allocations_time", "allocations", "allocated_at"),
            ("idx_sessions_status", "allocation_sessions", "status"),
            ("idx_sessions_user", "allocation_sessions", "user_id"),
        ]
        
        print("\n📊 Creating indexes...")
        for idx_name, table, column in indexes:
            cur.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})")
            print(f"   ✅ {idx_name}")
        
        # =====================================================================
        # 12. INSERT DEFAULT ADMIN USER (for testing)
        # =====================================================================
        cur.execute("""
            INSERT OR IGNORE INTO users (id, username, email, password)
            VALUES (1, 'admin', 'admin@example.com', 'hashed_password_here')
        """)
        print("\n✅ Created default admin user (id=1)")
        
        # =====================================================================
        # 13. INSERT SAMPLE CLASSROOMS (optional)
        # =====================================================================
        sample_classrooms = [
            ("Main Hall", 10, 10, "", 2),
            ("Lab A", 8, 6, "", 2),
            ("Auditorium", 15, 12, "", 3),
        ]
        
        print("\n🏫 Adding sample classrooms...")
        for name, rows, cols, broken, block in sample_classrooms:
            try:
                cur.execute("""
                    INSERT INTO classrooms (name, rows, cols, broken_seats, block_width)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, rows, cols, broken, block))
                print(f"   ✅ {name} ({rows}x{cols})")
            except sqlite3.IntegrityError:
                print(f"   ⚠️ {name} already exists")
        
        conn.commit()
        
        # =====================================================================
        # VERIFY TABLES
        # =====================================================================
        print("\n🔍 Verifying database structure...")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]
        
        expected_tables = [
            'users', 'user_activity', 'allocation_sessions', 'uploads', 
            'students', 'classrooms', 'allocations', 'staged_uploads', 
            'staged_students', 'feedback'
        ]
        
        for table in expected_tables:
            if table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"   ✅ {table:<20} ({count} rows)")
            else:
                print(f"   ❌ {table:<20} MISSING!")
        
        print("\n" + "="*60)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("="*60)
        print(f"\nDatabase location: {DB_PATH}")
        print(f"Total tables created: {len(tables)}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ INITIALIZATION FAILED: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    # Check if database already exists
    if DB_PATH.exists():
        response = input(f"⚠️  Database already exists at {DB_PATH}\nDelete and recreate? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Aborted. No changes made.")
            sys.exit(0)
        else:
            DB_PATH.unlink()
            print("🗑️  Deleted existing database\n")
    
    init_database()