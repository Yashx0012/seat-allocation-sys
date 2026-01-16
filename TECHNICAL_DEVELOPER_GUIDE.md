# Seat Allocation System - Technical Developer Guide

A comprehensive guide for developers working on the Seat Allocation System, covering API integration, service usage, and database management.

## 🚀 Quick Start

### Backend Service
1. **Navigate**: `cd algo`
2. **Install**: `pip install -r requirements.txt`
3. **Run**: `python app.py` (Default: `http://localhost:5000`)

### Frontend UI
1. **Navigate**: `cd Frontend`
2. **Install**: `npm install`
3. **Run**: `npm start` (Default: `http://localhost:3000`)

---

## 📦 Module Import Reference

Use these standardized imports to interact with the backend services and core logic.

```python
# Core App Factory
from algo.main import create_app

# Services (Business Logic)
from algo.services.session_service import SessionService
from algo.services.student_service import StudentService
from algo.services.allocation_service import AllocationService

# Core Engine & Cache
from algo.core.algorithm.seating import SeatingAlgorithm
from algo.core.cache.cache_manager import CacheManager

# Database Helpers
from algo.database.db import get_db_connection
from algo.database.queries.session_queries import SessionQueries
```

---

## 📡 API Endpoints Reference

### Student Management
- `POST /api/upload`: Parse and preview student data (CSV/Excel).
- `POST /api/commit-upload`: Save previewed data to the Database.
- `GET /api/students`: Retrieve students filtered by batch or upload ID.

### Allocation & Sessions
- `POST /api/sessions/start`: Initialize a new allocation session.
- `POST /api/generate-seating`: Generate a seating plan for a specific room.
- `POST /api/sessions/<id>/undo`: Revert the last allocation step in a session.
- `POST /api/sessions/<id>/finalize`: Commit a session and prune experimental data.

### Reporting & Exports
- `POST /api/generate-pdf`: Generate a seating plan PDF (Uses L2 Cache).
- `POST /api/export-attendance`: Generate attendance sheets for a session.
- `GET /api/plans/recent`: List historical and active sessions.

---

## 🛠️ Service Usage Examples

### 1. Creating a Session
```python
# Create a session and link student batches
session = SessionService.create_session("Morning Exam", user_id=8)
StudentService.add_students_from_batch(batch_id="CSE-A", session_id=session['id'])
```

### 2. Generating Seating (with L1 Cache)
```python
# Generate seating for a specific room
# Result is automatically saved to PLAN-<id>.json
result = AllocationService.allocate_classroom(
    session_id=123,
    classroom={"room_no": "101", "rows": 8, "cols": 10},
    student_distribution={"CSE": 40}
)
```

### 3. Finalizing a Session
```python
# Mark as completed and clean up trial data in L1 cache
SessionService.finalize_session(session_id=123)
```

---

## 💾 Database Schema Overview

The system uses SQLite (`demo.db`) with modular query handlers.

| Table | Purpose |
| :--- | :--- |
| `allocation_sessions` | Stores session metadata and status. |
| `uploads` | Tracks student batch uploads. |
| `students` | Master list of all students/enrollments. |
| `allocations` | Persisted seating placements (Room-Student link). |
| `allocation_history` | Step-by-step history for the Undo system. |
| `classrooms` | Classroom configurations and broken seat lists. |

---

## ⚡ Hybrid Caching (L1 & L2)

### L1 Seating Cache (`/algo/cache/`)
- **Format**: `PLAN-<plan_id>.json`
- **Behavior**: Stores seating matrices, metadata, and room configurations for an entire session.
- **Hit Logic**: Attempts to find identical seating patterns from historical plans to reuse configurations.

### L2 PDF Cache (`/algo/pdf_gen/seat_plan_generated/`)
- **Format**: `seating_plan_<content_hash>.pdf`
- **Behavior**: Rendered PDFs are saved and reused based on a SHA-256 hash of the seating grid contents. This provides sub-10ms responses for repeat downloads.

---
*Documentation State: Modular v2.3*
