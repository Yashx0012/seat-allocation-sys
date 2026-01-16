# ============================================================================
# SHORT SUMMARY: HOW RECENT PLANS ARE STORED & GENERATED
# ============================================================================

"""
FLOW DIAGRAM:

1. CREATE PLAN (User uploads batches)
   └─ POST /api/sessions/start
      └─ Generate plan_id (PLAN-XXXXX)
      └─ Create allocation_sessions row
      └─ Link uploads to session_id
      └─ Store in DATABASE

2. GENERATE SEATING
   └─ POST /api/generate-seating
      └─ Get pending students from DATABASE
      └─ Run SeatingAlgorithm (CPU intensive)
      └─ Save result in CACHE (/cache/PLAN-XXXXX.json)
      └─ Structure:
         {
           "metadata": {plan_id, total_students, room_no},
           "rooms": {
             "M101": {raw_matrix, batches, student_count},
             "M102": {raw_matrix, batches, student_count}
           }
         }

3. GENERATE PDF
   └─ POST /api/generate-pdf
      └─ LAYER 1 (app.py - Seating Cache):
         Get seating from CACHE (/cache/PLAN-XXXXX.json) → FAST
         If not found → Get from DATABASE → SLOW
      └─ LAYER 2 (pdf_generation.py - PDF Cache):
         Check if PDF exists (by content hash)
         If exists → Reuse → INSTANT
         If not → Generate new → SLOW
      └─ Return PDF to frontend

4. GENERATE ATTENDANCE
   └─ POST /api/export-attendance
      └─ Load plan from CACHE
      └─ Extract batch students: cache['rooms'][room_no]['batches'][batch_name]
      └─ Pass metadata (course_code, dept_name, etc.)
      └─ Call create_attendance_pdf() 
      └─ Return PDF

5. FINALIZE SESSION
   └─ POST /api/sessions/<id>/finalize
      └─ Mark session as 'completed' in DATABASE
      └─ Extract allocated rooms from allocations table
      └─ Call cache_manager.finalize_rooms()
      └─ Prune CACHE: Remove unused experimental rooms
      └─ Keep only: rooms with actual students

============================================================================
KEY STORAGE LOCATIONS:
============================================================================

DATABASE (SQLite): /demo.db
├─ allocation_sessions (plan_id, status, total_students)
├─ uploads (batch_name, batch_color, session_id)
├─ students (enrollment, batch_name, batch_color)
└─ allocations (student_id, classroom_id, seat_position)

CACHE (JSON Files): /algo/cache/
├─ PLAN-XXXXX.json (seating matrices for all rooms)
│  └─ Structure: {metadata, rooms: {M101: {raw_matrix, batches}}}
└─ Contains pre-computed seating to avoid re-running algorithm

PDF CACHE: /pdf_gen/seat_plan_generated/
├─ user_id/ (folder per user)
│  └─ seating_plan_[hash].pdf (generated PDFs, cached by content hash)
└─ Reused if same seating + template

ATTENDANCE CACHE: /attendence_gen/generated_report/
├─ Attendance_[batch]_[timestamp].pdf
└─ Temporary files, deleted after download

============================================================================
WHAT HAPPENS IN EACH OPERATION:
============================================================================

CREATE PLAN:
  Input: Upload files (CSV/Excel)
  Step 1: Parse file → Get batch_name, student count
  Step 2: INSERT into uploads table
  Step 3: INSERT students into students table
  Step 4: CREATE allocation_sessions row
  Output: plan_id, session_id (stored in DATABASE)

GENERATE SEATING:
  Input: plan_id, room_config, selected_batches
  Step 1: Get pending students from DATABASE
  Step 2: Run algorithm (2-3 seconds for 500 students)
  Step 3: SAVE to CACHE (/cache/PLAN-XXXXX.json)
  Step 4: INSERT allocations into DATABASE
  Output: Seating matrix (2D array of students)

GENERATE PDF:
  Input: plan_id, room_no, user_id, template
  Step 1: GET seating from CACHE (0.1s) ← HYBRID L1
  Step 2: COMPUTE content hash
  Step 3: CHECK if PDF exists (by hash)
  Step 4a: REUSE existing PDF (instant) ← HYBRID L2
  Step 4b: OR generate new PDF (1-2s)
  Output: PDF file path

GENERATE ATTENDANCE:
  Input: plan_id, batch_name, room_no, metadata
  Step 1: LOAD plan from CACHE
  Step 2: EXTRACT: cache['rooms'][room_no]['batches'][batch_name]['students']
  Step 3: FORMAT attendance sheet (name, enrollment, blank lines)
  Step 4: PASS metadata (course_code, coordinator, room_no)
  Step 5: RENDER to PDF
  Output: Attendance PDF

FINALIZE PLAN:
  Input: session_id
  Step 1: CHECK all students allocated (no pending)
  Step 2: GET list of rooms with allocations from DATABASE
  Step 3: CALL cache_manager.finalize_rooms(plan_id, room_list)
  Step 4: PRUNE cache.json - remove unused rooms
  Step 5: UPDATE session status = 'completed'
  Output: Cleaned cache.json (only allocated rooms remain)

============================================================================
HYBRID CACHING SUMMARY:
============================================================================

TWO-LAYER CACHING FOR SPEED:

Layer 1 - Seating Data Caching (app.py):
  ├─ Purpose: Avoid re-running algorithm
  ├─ Source: /cache/PLAN-XXXXX.json
  ├─ Hit Time: 0.1 seconds
  ├─ Miss Time: 2-3 seconds (algorithm runs)
  └─ Used by: PDF generation, batch operations

Layer 2 - PDF File Caching (pdf_generation.py):
  ├─ Purpose: Avoid re-rendering PDF
  ├─ Source: /pdf_gen/seat_plan_generated/[hash].pdf
  ├─ Hit Time: 0.01 seconds (file copy)
  ├─ Miss Time: 1-2 seconds (PDF rendered)
  └─ Used by: PDF requests

SPEEDUP COMPARISON:
├─ First seating generation: 2.5 seconds
├─ Repeat same seating: 0.1 seconds (30x faster) ✅
├─ First PDF: 2.5s (seating) + 1.5s (PDF) = 4.0s
├─ Repeat same config: 0.1s (seating) + 0.01s (PDF) = 0.11s (36x faster) ✅
└─ Batch 10 rooms: 3-4 seconds (vs 25 seconds) ✅

============================================================================
RECENT PLANS LIST:
============================================================================

GET /api/plans/recent
  └─ Query allocation_sessions WHERE status != 'deleted'
  └─ For each session:
     ├─ Get plan_id, total_students, allocated_count, status
     ├─ Get batch list (batches uploaded for this plan)
     └─ Order by: active first, then by last_activity
  └─ Return: Last 20 plans with status indicators

Status indicators:
  ├─ active: Currently being allocated
  ├─ completed: Finalized, cache pruned
  ├─ expired: Inactive > 30 minutes
  └─ archived: Old completed plans

"""

# ============================================================================
# CODE EXAMPLE: Full flow in action
# ============================================================================

# 1. USER CREATES PLAN
# POST /api/sessions/start with upload_ids=[1, 2, 3]

plan_id = "PLAN-ABC123XYZ"
session_id = 42
# Stored: allocation_sessions(session_id=42, plan_id='PLAN-ABC123XYZ', total_students=500)
# Stored: uploads linked to session_id=42

# 2. USER GENERATES SEATING (Room M101)
# POST /api/generate-seating with batches=[Batch A, Batch B]

# Internally:
# - Get pending students from DATABASE
# - Run algorithm (CPU work)
# - Save to CACHE: /cache/PLAN-ABC123XYZ.json
cache_file_content = {
    "metadata": {"plan_id": "PLAN-ABC123XYZ", "total_students": 500},
    "rooms": {
        "M101": {
            "raw_matrix": [[student, student, ...], ...],  # 2D array
            "batches": {
                "Batch A": {"students": [...], "info": {...}},
                "Batch B": {"students": [...], "info": {...}}
            }
        }
    }
}
# Stored in: /algo/cache/PLAN-ABC123XYZ.json

# 3. USER GENERATES PDF
# POST /api/generate-pdf with plan_id='PLAN-ABC123XYZ'

# HYBRID LAYER 1 (app.py):
seating = get_seating_from_cache('PLAN-ABC123XYZ', 'M101')  # Fast: 0.1s
# Returns: {'seating': [...], 'batches': {...}}

# HYBRID LAYER 2 (pdf_generation.py):
pdf_path = get_or_create_seating_pdf(seating)  # Fast: 0.01s if cached
# Returns: /pdf_gen/seat_plan_generated/test_user/seating_plan_[hash].pdf

# 4. USER GENERATES ATTENDANCE SHEET
# POST /api/export-attendance with batch_name='Batch A'

# Load from cache:
batch_students = cache['rooms']['M101']['batches']['Batch A']['students']
# Create PDF with: name, enrollment, blank lines
# Pass metadata: course_code, dept_name, coordinator_name, room_no

# 5. USER FINALIZES PLAN
# POST /api/sessions/42/finalize

# Check: all 500 students allocated ✓
# Get rooms: ['M101', 'M102', 'M103'] from database
# Call: cache_manager.finalize_rooms('PLAN-ABC123XYZ', ['M101', 'M102', 'M103'])
# Result: /cache/PLAN-ABC123XYZ.json now only has M101, M102, M103 (no experimental rooms)
# Update: allocation_sessions.status = 'completed'
