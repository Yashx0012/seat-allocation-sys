import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "demo.db"

def migrate():
    """Fix missing columns and ensure proper schema"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        print("🔄 Running migration: Fix session integration...")
        
        # 1. Ensure uploads table has session_id
        try:
            cur.execute("ALTER TABLE uploads ADD COLUMN session_id TEXT")
            print("✅ Added session_id to uploads")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️ session_id already exists in uploads")
            else:
                raise
        
        # 2. Ensure allocations has allocated_at timestamp
        try:
            cur.execute("ALTER TABLE allocations ADD COLUMN allocated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            print("✅ Added allocated_at to allocations")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️ allocated_at already exists in allocations")
            else:
                raise
        
        # 3. Ensure allocation_sessions has all required columns
        required_columns = [
            ("user_id", "INTEGER DEFAULT 1"),
            ("name", "TEXT"),
            ("last_activity", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("status", "TEXT DEFAULT 'active'"),
            ("total_students", "INTEGER DEFAULT 0"),
            ("total_allocated", "INTEGER DEFAULT 0"),
            ("total_capacity", "INTEGER DEFAULT 0")
        ]
        
        for col_name, col_type in required_columns:
            try:
                cur.execute(f"ALTER TABLE allocation_sessions ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added {col_name} to allocation_sessions")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"⚠️ {col_name} already exists")
                else:
                    raise
        
        # 4. Create user_activity if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id INTEGER PRIMARY KEY,
                last_activity DATETIME NOT NULL,
                last_endpoint TEXT
            )
        """)
        print("✅ Ensured user_activity table exists")
        
        # 5. Create indexes if not exist
        indexes = [
            ("idx_uploads_session", "uploads", "session_id"),
            ("idx_allocations_session", "allocations", "session_id"),
            ("idx_allocations_time", "allocations", "allocated_at")
        ]
        
        for idx_name, table, column in indexes:
            try:
                cur.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})")
                print(f"✅ Created index {idx_name}")
            except Exception as e:
                print(f"⚠️ Index {idx_name}: {e}")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()