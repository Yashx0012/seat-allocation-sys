"""
One-time migration script: Merge user_auth.db into demo.db.

This script:
1. Reads all users from algo/user_auth.db
2. Ensures the demo.db users table has the required auth columns
3. Inserts/updates each user into demo.db, preserving IDs where possible
4. Updates all user_id foreign keys in demo.db if any ID mapping changed
5. Creates a backup of both databases before modifying anything

Run from project root:
    python algo/scripts/migrate_to_single_db.py
"""
import sqlite3
import os
import sys
import shutil
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
algo_dir = os.path.join(script_dir, '..')
project_root = os.path.join(algo_dir, '..')

AUTH_DB = os.path.join(algo_dir, 'user_auth.db')
DATA_DB = os.path.join(project_root, 'demo.db')

BACKUP_SUFFIX = datetime.now().strftime('%Y%m%d_%H%M%S')

def backup_databases():
    """Create timestamped backups of both databases."""
    for db_path, label in [(AUTH_DB, 'user_auth'), (DATA_DB, 'demo')]:
        if os.path.exists(db_path):
            backup = f"{db_path}.backup_{BACKUP_SUFFIX}"
            shutil.copy2(db_path, backup)
            print(f"  ✅ Backed up {label}.db -> {os.path.basename(backup)}")
        else:
            print(f"  ⚠️  {label}.db not found at {db_path}")


def ensure_auth_columns(conn):
    """Add auth-related columns to demo.db users table if missing."""
    # Recreate users table with updated CHECK constraint and all auth columns.
    # SQLite doesn't support ALTER CHECK, so we need to recreate the table.
    conn.execute("PRAGMA foreign_keys = OFF")
    
    # Check if table exists and has data
    existing_users = []
    try:
        existing_users = conn.execute("SELECT * FROM users").fetchall()
        col_names = [desc[0] for desc in conn.execute("SELECT * FROM users LIMIT 0").description]
    except sqlite3.OperationalError:
        col_names = []
    
    if existing_users:
        print(f"  Migrating {len(existing_users)} existing user(s) to new schema...")
    
    # Drop old table, create new one
    conn.execute("DROP TABLE IF EXISTS users_old_backup")
    try:
        conn.execute("ALTER TABLE users RENAME TO users_old_backup")
    except sqlite3.OperationalError:
        pass  # Table doesn't exist
    
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            role TEXT NOT NULL DEFAULT 'STUDENT' CHECK(role IN ('STUDENT', 'ADMIN', 'TEACHER', 'FACULTY')),
            full_name TEXT,
            auth_provider TEXT DEFAULT 'local',
            google_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    """)
    
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_google_id 
        ON users(google_id) WHERE google_id IS NOT NULL
    """)
    
    # Copy back any existing users (map old columns to new)
    if existing_users and col_names:
        for row in existing_users:
            row_dict = {col_names[i]: row[i] for i in range(len(col_names))}
            conn.execute("""
                INSERT OR IGNORE INTO users (id, username, email, password_hash, role, full_name, auth_provider, google_id, created_at, updated_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row_dict.get('id'), row_dict.get('username', row_dict.get('email', '').split('@')[0]),
                row_dict.get('email'), row_dict.get('password_hash'),
                row_dict.get('role', 'STUDENT'), row_dict.get('full_name'),
                row_dict.get('auth_provider', 'local'), row_dict.get('google_id'),
                row_dict.get('created_at'), row_dict.get('updated_at'),
                row_dict.get('last_login')
            ))
    
    conn.execute("DROP TABLE IF EXISTS users_old_backup")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    print("  ✅ Users table recreated with unified schema")


def migrate():
    print("=" * 70)
    print("🔄 Database Consolidation: user_auth.db -> demo.db")
    print("=" * 70)

    # ── Validate ──
    if not os.path.exists(AUTH_DB):
        print(f"\n⚠️  user_auth.db not found at {AUTH_DB}")
        print("   Nothing to migrate. If this is a fresh install, you're already on the consolidated schema.")
        return True

    if not os.path.exists(DATA_DB):
        print(f"\n❌ demo.db not found at {DATA_DB}")
        print("   Run the Flask app once to initialize the database, then re-run this script.")
        return False

    # ── Backup ──
    print("\n📦 Step 1: Creating backups...")
    backup_databases()

    # ── Read auth users ──
    print("\n📖 Step 2: Reading users from user_auth.db...")
    auth_conn = sqlite3.connect(AUTH_DB)
    auth_conn.row_factory = sqlite3.Row
    auth_users = auth_conn.execute(
        "SELECT id, username, email, password_hash, role, full_name, auth_provider, google_id, created_at, updated_at FROM users ORDER BY id"
    ).fetchall()
    auth_conn.close()
    print(f"  Found {len(auth_users)} user(s) in user_auth.db")

    if not auth_users:
        print("\n✅ No users to migrate. Done.")
        return True

    for u in auth_users:
        print(f"  #{u['id']} {u['username']} <{u['email']}> [{u['role']}] via {u['auth_provider'] or 'local'}")

    # ── Prepare demo.db ──
    print("\n🔧 Step 3: Preparing demo.db schema...")
    data_conn = sqlite3.connect(DATA_DB)
    data_conn.row_factory = sqlite3.Row
    ensure_auth_columns(data_conn)

    # Read existing demo.db users
    existing = data_conn.execute("SELECT id, email FROM users").fetchall()
    existing_emails = {row['email']: row['id'] for row in existing if row['email']}
    existing_ids = {row['id'] for row in existing}
    print(f"  demo.db currently has {len(existing)} user(s)")

    # ── Merge users ──
    print("\n🔀 Step 4: Merging users...")
    id_map = {}  # old_auth_id -> new_demo_id

    for auth_user in auth_users:
        auth_id = auth_user['id']
        email = auth_user['email']

        if email in existing_emails:
            # User already exists in demo.db by email — update with auth fields
            demo_id = existing_emails[email]
            data_conn.execute("""
                UPDATE users SET 
                    username = ?, password_hash = ?, role = ?, full_name = ?,
                    auth_provider = ?, google_id = ?, updated_at = ?
                WHERE id = ?
            """, (
                auth_user['username'], auth_user['password_hash'], auth_user['role'],
                auth_user['full_name'], auth_user['auth_provider'] or 'local',
                auth_user['google_id'], auth_user['updated_at'] or datetime.now().isoformat(),
                demo_id
            ))
            id_map[auth_id] = demo_id
            action = f"UPDATED (demo id={demo_id})" if demo_id != auth_id else "UPDATED (same id)"
            print(f"  {email}: {action}")

        elif auth_id not in existing_ids:
            # ID slot is free — insert with same ID to preserve FK references
            data_conn.execute("""
                INSERT INTO users (id, username, email, password_hash, role, full_name, auth_provider, google_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                auth_id, auth_user['username'], email, auth_user['password_hash'],
                auth_user['role'], auth_user['full_name'], auth_user['auth_provider'] or 'local',
                auth_user['google_id'], auth_user['created_at'], auth_user['updated_at']
            ))
            id_map[auth_id] = auth_id
            print(f"  {email}: INSERTED (id={auth_id})")

        else:
            # ID collision — insert with new auto-generated ID
            cur = data_conn.execute("""
                INSERT INTO users (username, email, password_hash, role, full_name, auth_provider, google_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                auth_user['username'], email, auth_user['password_hash'],
                auth_user['role'], auth_user['full_name'], auth_user['auth_provider'] or 'local',
                auth_user['google_id'], auth_user['created_at'], auth_user['updated_at']
            ))
            new_id = cur.lastrowid
            id_map[auth_id] = new_id
            print(f"  {email}: INSERTED (id collision: auth={auth_id} -> demo={new_id})")

    data_conn.commit()

    # ── Remap FKs if any IDs changed ──
    remapped = {old: new for old, new in id_map.items() if old != new}
    if remapped:
        print(f"\n🔗 Step 5: Remapping {len(remapped)} changed user ID(s) in FK references...")

        # Tables with user_id foreign key
        fk_tables = [
            ("allocation_sessions", "user_id"),
            ("classrooms", "user_id"),
            ("feedback", "user_id"),
            ("user_activity", "user_id"),
        ]

        for old_id, new_id in remapped.items():
            for table, col in fk_tables:
                try:
                    result = data_conn.execute(
                        f"UPDATE {table} SET {col} = ? WHERE {col} = ?", (new_id, old_id)
                    )
                    if result.rowcount > 0:
                        print(f"  {table}.{col}: {result.rowcount} row(s) updated ({old_id} -> {new_id})")
                except sqlite3.OperationalError:
                    pass  # Table or column doesn't exist yet
        
        data_conn.commit()
    else:
        print("\n🔗 Step 5: No ID remapping needed — all IDs preserved.")

    # ── Verify ──
    print("\n✅ Step 6: Verification...")
    final_users = data_conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
    print(f"  demo.db now has {final_users} user(s)")

    # Quick FK integrity check
    orphaned = data_conn.execute("""
        SELECT COUNT(*) as c FROM allocation_sessions 
        WHERE user_id IS NOT NULL AND user_id NOT IN (SELECT id FROM users)
    """).fetchone()['c']
    if orphaned:
        print(f"  ⚠️  {orphaned} session(s) with orphaned user_id (no matching user)")
    else:
        print(f"  ✅ All session user_id references are valid")

    data_conn.close()

    # ── Rename old auth DB ──
    retired = AUTH_DB + '.retired'
    os.rename(AUTH_DB, retired)
    print(f"\n📁 Renamed user_auth.db -> {os.path.basename(retired)}")
    print("   (Delete it manually once you've verified everything works)")

    print("\n" + "=" * 70)
    print("✅ Migration complete! The app now uses a single database: demo.db")
    print("=" * 70)
    return True


if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
