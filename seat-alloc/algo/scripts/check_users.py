"""
Script to check registered users and their data ownership.
Run from project root: python algo/scripts/check_users.py
"""
import sqlite3
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
algo_dir = os.path.join(script_dir, '..')
project_root = os.path.join(algo_dir, '..')

# Consolidated database at project root
db_path = os.path.join(project_root, 'demo.db')

print(f"📂 Database: {os.path.abspath(db_path)} (exists: {os.path.exists(db_path)})")

if not os.path.exists(db_path):
    print("❌ Database not found!")
    sys.exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# ── USERS ──
print("\n" + "=" * 80)
print("📋 REGISTERED USERS")
print("=" * 80)

cur = conn.execute("SELECT id, username, email, role, auth_provider, created_at FROM users ORDER BY id")
users = cur.fetchall()

if not users:
    print("No users found!")
else:
    print(f"{'ID':<6} {'Username':<20} {'Email':<35} {'Role':<10} {'Auth':<8} {'Created'}")
    print("-" * 90)
    for user in users:
        created = user['created_at'] or 'N/A'
        auth = user['auth_provider'] or 'local'
        print(f"{user['id']:<6} {user['username']:<20} {user['email']:<35} {user['role']:<10} {auth:<8} {created}")

print(f"\nTotal Users: {len(users)}")

# ── DATA OWNERSHIP ──
print("\n" + "=" * 80)
print("📊 DATA OWNERSHIP SUMMARY")
print("=" * 80)

for user in users:
    uid = user['id']
    uname = user['username']
    print(f"\n👤 User: {uname} (ID: {uid}, Email: {user['email']})")
    print("-" * 50)
    
    # Sessions by status
    cur = conn.execute("""
        SELECT status, COUNT(*) as count 
        FROM allocation_sessions 
        WHERE user_id = ? 
        GROUP BY status
    """, (uid,))
    sessions = cur.fetchall()
    if sessions:
        for s in sessions:
            print(f"  Sessions ({s['status']}): {s['count']}")
    else:
        print("  Sessions: 0")
    
    # Classrooms
    try:
        cur = conn.execute("SELECT COUNT(*) as count FROM classrooms WHERE user_id = ?", (uid,))
        print(f"  Classrooms: {cur.fetchone()['count']}")
    except sqlite3.OperationalError:
        print("  Classrooms: (user_id column not yet added)")
    
    # Uploads
    cur = conn.execute("""
        SELECT COUNT(*) as count FROM uploads u
        JOIN allocation_sessions s ON u.session_id = s.session_id
        WHERE s.user_id = ?
    """, (uid,))
    print(f"  Uploads: {cur.fetchone()['count']}")
    
    # Students
    cur = conn.execute("""
        SELECT COUNT(*) as count FROM students st
        JOIN uploads u ON st.upload_id = u.id
        JOIN allocation_sessions s ON u.session_id = s.session_id
        WHERE s.user_id = ?
    """, (uid,))
    print(f"  Students: {cur.fetchone()['count']}")
    
    # Allocations
    cur = conn.execute("""
        SELECT COUNT(*) as count FROM allocations a
        JOIN allocation_sessions s ON a.session_id = s.session_id
        WHERE s.user_id = ?
    """, (uid,))
    print(f"  Allocations: {cur.fetchone()['count']}")

# Check orphaned data
print("\n" + "=" * 80)
print("⚠️  ORPHANED DATA (user_id IS NULL)")
print("=" * 80)

cur = conn.execute("SELECT COUNT(*) as count FROM allocation_sessions WHERE user_id IS NULL")
print(f"  Sessions with NULL user_id: {cur.fetchone()['count']}")

try:
    cur = conn.execute("SELECT COUNT(*) as count FROM classrooms WHERE user_id IS NULL")
    print(f"  Classrooms with NULL user_id: {cur.fetchone()['count']}")
except sqlite3.OperationalError:
    print("  Classrooms: (user_id column not yet added)")

# Check all sessions
print("\n" + "=" * 80)
print("🔍 ALL SESSIONS (showing user ownership)")
print("=" * 80)

cur = conn.execute("""
    SELECT session_id, user_id, plan_id, status, total_students, allocated_count, created_at
    FROM allocation_sessions 
    ORDER BY created_at DESC
    LIMIT 30
""")
sessions = cur.fetchall()
if sessions:
    print(f"{'SessID':<8} {'UserID':<8} {'Plan ID':<18} {'Status':<12} {'Students':<10} {'Alloc':<8} {'Created'}")
    print("-" * 90)
    for s in sessions:
        uid_str = str(s['user_id']) if s['user_id'] else 'NULL'
        plan = (s['plan_id'] or 'N/A')[:16]
        created = (s['created_at'] or 'N/A')[:19]
        print(f"{s['session_id']:<8} {uid_str:<8} {plan:<18} {s['status']:<12} {s['total_students'] or 0:<10} {s['allocated_count'] or 0:<8} {created}")
else:
    print("  No sessions found")

conn.close()

print("\n" + "=" * 80)
print("✅ Report complete")
print("=" * 80)
