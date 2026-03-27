# Seat Allocation System - Backend

This directory contains the core logic, API endpoints, and services for the Seat Allocation System. The backend is built with Flask and follows a modular architecture designed for scalability and maintainability.

**Version:** v2.4 | **Last Updated:** February 2026

## Directory Structure

- **[api/](./api/)**: Contains Flask blueprints and API routing logic with 12+ endpoint modules.
- **[core/](./core/)**: The "brain" of the application, housing the seating algorithm and cache management.
- **[database/](./database/)**: Database schema, initializations, and modular query handlers.
- **[services/](./services/)**: Business logic layer that orchestrates operations between APIs and the core/database layers.
- **[utils/](./utils/)**: General-purpose utilities and parsing logic (e.g., Excel/CSV parsing).
- **[pdf_gen/](./pdf_gen/)**: Specialized modules for generating PDF reports, seating vectors, and attendance sheets.
- **[attendence_gen/](./attendence_gen/)**: Attendance sheet generation with branch detection.
- **[config/](./config/)**: Centralized configuration management and environment settings.
- **[cache/](./cache/)**: JSON-based L1 cache repository for session snapshots.

## Core Features

### Seating Algorithm 🧠
- **Column-Major Allocation**: Vertical batch distribution for better visual separation
- **Variable Block Structures**: Support for non-uniform column groupings (e.g., `[3, 2, 3]`)
- **Paper Set Constraints**: 3-tier priority system (P1-P3) for examination security
- **Adjacent Seating Control** 🆕: Optional same-batch horizontal adjacency for single-batch scenarios
- **Batch Branch Detection** 🆕: Intelligent majority-based identification from enrollment numbers

### Hybrid Caching System 💾
- **L1 (Data Layer)**: JSON snapshots in `algo/cache/` with multi-room support
- **L2 (File Layer)**: Rendered PDF storage with content-hash indexing
- **Session Isolation**: One session = one cache file (no cross-contamination)
- **Smart Pruning**: Trial rooms automatically removed on session finalization

### API Endpoints 📡
Comprehensive RESTful endpoints organized by feature:

| Blueprint | Purpose | Key Endpoints |
| :--- | :--- | :--- |
| **allocations** | Seating generation | POST `/api/generate-seating`, `POST /api/undo-allocation` |
| **pdf** | Single-room PDF export | POST `/api/generate-pdf` |
| **master_plan_pdf** 🆕 | Institutional reports | POST `/api/master-plan-pdf` |
| **sessions** | Session lifecycle | GET `/api/sessions`, POST `/api/sessions/start`, `POST /sessions/finalize` |
| **students** | Student management | POST `/api/students/upload`, GET `/api/students` |
| **classrooms** | Room configuration | POST `/api/classrooms`, GET `/api/classrooms` |
| **dashboard** | Analytics & stats | GET `/api/dashboard/stats`, `/api/dashboard/allocations` |
| **plans** | History & snapshots | GET `/api/plans/recent`, `/api/plans/{plan_id}` |
| **admin** | Auth & permissions | POST `/api/auth/login`, `/api/auth/logout` |
| **feedback** 🆕 | User feedback | POST `/api/feedback` |
| **templates** 🆕 | Template management | GET `/api/templates`, POST `/api/templates/upload` |
| **health** | System diagnostics | GET `/api/health` |

### Modular Services 🛠️
- **AllocationService**: High-level seating orchestration
- **SessionService**: Transactional session management with undo/redo
- **StudentService**: Bulk import and validation
- **ActivityService**: Operation logging and audit trails

### PDF & Reporting 📄
- **Single-Room PDFs**: Seating plans for individual exam halls
- **Master Plan PDFs** 🆕: A4 documents with room-wise roll number ranges
- **Attendance Sheets**: Per-room attendance forms with batch metadata
- **Template System**: Customizable PDF layouts via `template_manager.py`

## Architecture & Flow

### Request-Response Cycle
```
1. User Request (UI)
    ↓
2. API Blueprint (Route Handler)
    ↓
3. Service Layer (Business Logic)
    ↓
4. Core/Cache/Database (Persistence)
    ↓
5. Response (Result or Error)
    ↓
6. Client Rendering (UI Update)
```

### Key Data Flows

#### Seating Generation
```
allocations.py
  → allocation_service.py
    → seating.py (Algorithm)
      → cache_manager.py (L1 Save)
        → Response (JSON)
```

#### PDF Export
```
pdf.py
  → cache_manager.py (L1 Check)
    → pdf_generation.py (Render)
      → L2 Cache (Store)
        → Response (PDF)
```

#### Master Plan Export 🆕
```
master_plan_pdf.py
  → cache_manager.py (Multi-room Load)
    → Branch Detection (Majority Voting)
      → reportlab (A4 Render)
        → Response (In-Memory PDF)
```

## 🆕 New Features in v2.4

### 1. Variable Block Structures
Support for non-uniform column groupings:
```python
# Example: 8 columns with widths [3, 2, 3]
algo = SeatingAlgorithm(
    rows=10, cols=8,
    num_batches=2,
    block_structure=[3, 2, 3]  # Takes precedence over block_width
)
```

### 2. Adjacent Seating Control
Enable horizontal adjacency for single-batch scenarios:
```json
{
  "num_batches": 1,
  "allow_adjacent_same_batch": true,
  "batch_roll_numbers": {1: ["BTCS24O1001", ...]}
}
```

### 3. Branch Detection & Metadata
Intelligent extraction from enrollment numbers:
- **Formats Supported**: 
  - New: `0901CS231067` (Institution + Branch + Year + Roll)
  - Legacy: `BTCS241001` (Degree + Branch + Year + Roll)
- **Majority Voting**: Samples 3-5 students per batch
- **Use Cases**: Attendance sheets, master plans, analytics

### 4. Master Plan PDF Generation
Institutional-level reporting in A4 format:
```bash
POST /api/master-plan-pdf
{
  "plan_id": "PLAN-ABC123",
  "include_branch_info": true
}
```

### 5. Feedback System
Structured user feedback collection:
```bash
POST /api/feedback
{
  "plan_id": "PLAN-ABC123",
  "feedback_type": "constraint_violation",
  "message": "Students found adjacent..."
}
```

### 6. Enhanced Template Management
Dynamic template selection and upload:
```bash
GET /api/templates              # List available templates
POST /api/templates/upload      # Upload custom template
```

## Configuration

### Environment Variables (`.env`)
```bash
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///demo.db
CACHE_DIR=./cache
LOG_LEVEL=DEBUG
```

### Database Initialization
```bash
python -c "from algo.database.db import init_db; init_db()"
```

## Quick Start

### Installation
```bash
cd algo
pip install -r requirements.txt
```

### Running the Backend
```bash
python app.py
# Server runs on http://localhost:5000
```

### Testing Endpoints
```bash
# Generate seating
curl -X POST http://localhost:5000/api/generate-seating \
  -H "Content-Type: application/json" \
  -d '{
    "rows": 10,
    "cols": 6,
    "num_batches": 2,
    "batch_student_counts": {1: 30, 2: 25}
  }'

# Export as PDF
curl -X POST http://localhost:5000/api/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "PLAN-ABC123", "room_no": "M101"}'

# Generate Master Plan (v2.4)
curl -X POST http://localhost:5000/api/master-plan-pdf \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "PLAN-ABC123"}'
```

## API Reference

See [HYBRID_CACHING_GUIDE.md](./HYBRID_CACHING_GUIDE.md) for detailed cache layer documentation.

For complete API specifications, refer to the [Details/SYSTEM_ARCHITECTURE.md](../Details/SYSTEM_ARCHITECTURE.md).

## Performance Benchmarks

| Operation | Time | Notes |
| :--- | :--- | :--- |
| Seating Generation (200 students) | 50-100ms | Includes validation |
| PDF Export (L1 Cache Hit) | 50-100ms | Disk I/O only |
| PDF Export (Database Fallback) | 500-1000ms | Computation + rendering |
| Master Plan PDF (20 rooms) | 1000-2000ms | Aggregation + rendering |

## Troubleshooting

### Cache Issues
If you experience stale cache:
```bash
# Clear cache directory
rm -rf algo/cache/*.json
```

### Database Lock
If database is locked, check for hanging connections:
```python
from algo.database.db import get_db_connection
conn = get_db_connection()
conn.execute("VACUUM")
```

### Memory Usage
For large allocations (500+ students), monitor memory:
```bash
# Monitor Python process
watch -n 1 'ps aux | grep python'
```

---

*Last Updated: February 2026 | Version: v2.4*
