import sqlite3
import os

# Update this path to match your project structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "pdf_templates.db")

def init_database():
    """Initialize the database with required tables"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create user_templates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            template_name TEXT NOT NULL DEFAULT 'default',
            dept_name TEXT,
            exam_details TEXT,
            seating_plan_title TEXT,
            branch_text TEXT,
            room_number TEXT,
            coordinator_name TEXT,
            coordinator_title TEXT,
            banner_image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, template_name)
        )
    ''')
    
    system_banner_path = os.path.join(BASE_DIR, "data", "banner.png")
    
    # Insert system default template if not exists
    cursor.execute('''
        INSERT OR IGNORE INTO user_templates (
            user_id, template_name, dept_name, exam_details,
            seating_plan_title, branch_text, room_number,
            coordinator_name, coordinator_title, banner_image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'system', 'default',
        'Department of Computer Science & Engineering',
        'Minor-II Examination (2025 Admitted), November 2025',
        'Seating Plan',
        'Branch: B.Tech(CSE & CSD Ist year)',
        'Room no. 103A',
        'Dr. Dheeraj K. Dixit',
        'Dept. Exam Coordinator',
        os.path.join(BASE_DIR, 'data', 'banner.png')
    ))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized and repaired successfully")

# Initialize on import
try:
    init_database()
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")
