"""
Migration 001: Add Session Management
Adds user activity tracking and session persistence features
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "demo.db"

def migrate():
    """Phase 1: Add session management tables and columns"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        print("=" * 70)
        print("🔄 Running Migration 001: Session Management")
        print("=" * 70)
        
        # 1. Create user_activity table
        print("\n📋 Creating user_activity table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id INTEGER PRIMARY KEY,
                last_activity DATETIME NOT NULL,
                last_endpoint TEXT
            )
        """)
        print("✅ user_activity table created")
        
        # 2. Add columns to allocation_sessions (SQLite safe way)
        print("\n📋 Updating allocation_sessions table...")
        
        # Check which columns exist
        cur.execute("PRAGMA table_info(allocation_sessions)")
        existing_columns = {row[1] for row in cur.fetchall()}
        print(f"   Existing columns: {existing_columns}")
        
        # Add user_id
        if 'user_id' not in existing_columns:
            try:
                cur.execute("ALTER TABLE allocation_sessions ADD COLUMN user_id INTEGER DEFAULT 1")
                print("✅ Added column: user_id")
            except sqlite3.OperationalError as e:
                print(f"⚠️  user_id: {e}")
        else:
            print("⚠️  Column user_id already exists (skipping)")
        
        # Add name
        if 'name' not in existing_columns:
            try:
                cur.execute("ALTER TABLE allocation_sessions ADD COLUMN name TEXT")
                print("✅ Added column: name")
            except sqlite3.OperationalError as e:
                print(f"⚠️  name: {e}")
        else:
            print("⚠️  Column name already exists (skipping)")
        
        # Add last_activity (FIXED: No DEFAULT for ALTER TABLE in SQLite)
        if 'last_activity' not in existing_columns:
            try:
                # Add column without default
                cur.execute("ALTER TABLE allocation_sessions ADD COLUMN last_activity DATETIME")
                print("✅ Added column: last_activity")
                
                # Set default value for existing rows
                cur.execute("""
                    UPDATE allocation_sessions 
                    SET last_activity = created_at 
                    WHERE last_activity IS NULL
                """)
                print("✅ Set default values for existing rows")
            except sqlite3.OperationalError as e:
                print(f"⚠️  last_activity: {e}")
        else:
            print("⚠️  Column last_activity already exists (skipping)")
        
        # 3. Create indexes for performance
        print("\n📋 Creating indexes...")
        
        indexes = [
            ("idx_allocations_session", "allocations", "session_id"),
            ("idx_allocations_student", "allocations", "student_id"),
            ("idx_allocations_classroom", "allocations", "classroom_id"),
            ("idx_allocations_time", "allocations", "allocated_at"),
            ("idx_uploads_session", "uploads", "session_id"),
            ("idx_students_upload", "students", "upload_id"),
        ]
        
        for idx_name, table, column in indexes:
            try:
                cur.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})")
                print(f"✅ Created index: {idx_name}")
            except Exception as e:
                print(f"⚠️  Index {idx_name}: {e}")
        
        # 4. Initialize user_activity for default user
        print("\n📋 Initializing user activity...")
        try:
            cur.execute("""
                INSERT OR IGNORE INTO user_activity (user_id, last_activity, last_endpoint)
                VALUES (1, ?, '/init')
            """, (datetime.now().isoformat(),))
            print(f"✅ Initialized activity for user_id=1")
        except Exception as e:
            print(f"⚠️  Activity init: {e}")
        
        # 5. Update existing sessions with last_activity if missing
        print("\n📋 Updating existing sessions...")
        cur.execute("""
            UPDATE allocation_sessions 
            SET last_activity = COALESCE(last_activity, created_at, datetime('now'))
            WHERE last_activity IS NULL
        """)
        print(f"✅ Updated {cur.rowcount} session(s)")
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print("✅ Migration 001 completed successfully!")
        print("=" * 70)
        
        # Verification
        print("\n📊 Verification:")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]
        print(f"   Total tables: {len(tables)}")
        
        # Verify allocation_sessions structure
        cur.execute("PRAGMA table_info(allocation_sessions)")
        columns = [row[1] for row in cur.fetchall()]
        print(f"   allocation_sessions columns: {', '.join(columns)}")
        
        # Verify user_activity
        cur.execute("SELECT COUNT(*) FROM user_activity")
        activity_count = cur.fetchone()[0]
        print(f"   user_activity records: {activity_count}")
        
    except Exception as e:
        conn.rollback()
        print("\n" + "=" * 70)
        print(f"❌ Migration failed: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
    