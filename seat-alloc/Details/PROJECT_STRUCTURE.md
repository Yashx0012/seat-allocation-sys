# Seat Allocation System - Project Structure

## 🏗️ Definitive Modular Architecture

The system has been restructured from a monolithic design into a clean, service-oriented modular architecture.

### Backend Structure (`algo/`)

```text
algo/
├── api/                     # 📡 Communication Layer
│   └── blueprints/          # Flask Blueprints (Route Handlers)
│       ├── admin.py         # Auth & Admin endpoints
│       ├── allocations.py   # Seating generation endpoints
│       ├── classrooms.py    # Room management
│       ├── dashboard.py     # Analytics & Statistics
│       ├── feedback.py      # User feedback collection 🆕
│       ├── health.py        # System diagnostic checks
│       ├── master_plan_pdf.py # Master plan PDF generation 🆕
│       ├── pdf.py           # PDF export orchestration
│       ├── plans.py         # History & Recent plans
│       ├── sessions.py      # Session lifecycle & Undo
│       ├── students.py      # Student data management
│       ├── templates.py     # Template management 🆕
│       └── database.py      # Database access layer (blueprints)
│
├── core/                    # ⚡ Business Logic Layer
│   ├── algorithm/           # The Engine
│   │   └── seating.py       # SeatingAlgorithm Core logic (v2.4)
│   │                        # - Column-major filling
│   │                        # - Variable block structures
│   │                        # - Adjacent seating control
│   ├── cache/               # Performance Layer
│   │   └── cache_manager.py # Hybrid L1/L2 Cache Engine
│   │                        # - Multi-room snapshots
│   │                        # - Majority-based branch detection
│   │                        # - Dual enrollment format support
│   └── models/              # Shared Definitions
│       ├── allocation.py    # Seat & PaperSet Dataclasses
│       └── ... (other models)
│
├── database/                # 🗄️ Persistence Layer
│   ├── queries/             # Modular SQL repository
│   ├── db.py                # Connection pool & context
│   ├── schema.py            # SQL table definitions
│   └── migrations/          # Schema versioning
│
├── services/                # 🛠️ Orchestration Layer
│   ├── session_service.py   # Transactional session logic
│   ├── student_service.py   # Bulk data handling
│   ├── allocation_service.py # High-level allocation logic
│   └── activity_service.py  # Activity logging
│
├── pdf_gen/                 # 📄 PDF Generation Engine
│   ├── pdf_generation.py    # Seating plan PDF generator
│   ├── template_manager.py  # Template handling & selection
│   ├── database.py          # PDF-related DB queries
│   └── data/                # PDF template resources
│
├── attendence_gen/          # 📋 Attendance Sheet Generator
│   ├── attend_gen.py        # Attendance PDF with branch detection
│   ├── cache/               # Cached attendance templates
│   ├── data/                # Attendance template data
│   └── generated_report/    # Output directory
│
├── utils/                   # 🛠️ Helpers
│   ├── helpers.py           # String/Date utilities
│   └── parser.py            # CSV/Excel parsing
│
├── cache/                   # 💾 JSON Cache Repository
│   ├── PLAN-*.json          # Session snapshots (multi-room)
│   ├── temp_uploads/        # Temporary uploaded files
│   └── previews/            # Preview snapshots
│
├── static/                  # 📦 Static Assets & Templates
│   └── templates/           # HTML template directory
│
├── config/                  # ⚙️ Environment & Settings
│   ├── settings.py          # Configuration management
│   └── __init__.py
│
├── scripts/                 # 🔧 Utility Scripts
│   └── check_users.py       # User validation utilities
│
├── tests/                   # 🧪 Test Suite
│   ├── debug_multi.py       # Multi-room debugging
│   ├── health_check.py      # System health verification
│   ├── test_*.py            # Unit & integration tests
│   └── scripts/             # Test utilities
│
├── app.py                   # 🚀 Flask Entry Point (Main)
├── main.py                  # Factory & Blueprint Registry
├── auth_service.py          # Legacy Auth wrapper (bridging)
├── HYBRID_CACHING_GUIDE.md  # Caching strategy documentation
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (gitignored)
```

### Frontend Structure (`Frontend/`)

```text
Frontend/
├── public/                  # Static Assets
│   ├── index.html          # Application entry point
│   ├── manifest.json       # PWA manifest
│   └── robots.txt
│
├── src/
│   ├── components/         # Reusable UI Atoms/Molecules
│   │   ├── Navbar.jsx      # Global navigation (glassmorphism)
│   │   ├── PillNav.jsx     # GSAP-animated pill navigation
│   │   ├── SeatingGrid.jsx # Interactive seating visualization
│   │   └── ... (other components)
│   ├── pages/              # Top-level Route Components
│   │   ├── Dashboard.jsx
│   │   ├── AllocationPage.jsx
│   │   └── ... (page routes)
│   ├── contexts/           # Global State Management
│   │   ├── AuthContext.jsx
│   │   ├── SessionContext.jsx
│   │   └── ... (global stores)
│   ├── hooks/              # Custom React Hooks
│   ├── services/           # API Client Wrappers
│   │   ├── api.js          # Axios configuration & requests
│   │   └── ... (service modules)
│   ├── utils/              # Formatters & Constants
│   ├── App.jsx
│   ├── index.js
│   ├── App.css
│   └── index.css
│
├── docs/                   # Docusaurus Documentation 🆕 Enhanced
│   ├── docs/               # Doc pages
│   │   ├── intro.md        # Getting started guide
│   │   ├── developers/     # Developer documentation
│   │   │   ├── api-guide.md
│   │   │   ├── architecture.md
│   │   │   └── ...
│   │   └── user-guide/     # End-user documentation
│   │       ├── seating-basics.md
│   │       ├── generating-plans.md
│   │       └── ...
│   ├── blog/               # Blog posts & changelogs
│   ├── src/                # Docusaurus customizations
│   ├── static/             # Static doc assets
│   ├── docusaurus.config.js # Docusaurus configuration
│   ├── sidebars.js         # Navigation structure
│   └── package.json        # Docusaurus dependencies
│
├── package.json            # Frontend dependencies
├── postcss.config.js       # PostCSS configuration (Tailwind)
├── tailwind.config.js      # Tailwind CSS configuration
├── .env                    # Environment variables (gitignored)
├── .env.example            # Example env file
├── .gitignore              # Git ignore rules
└── README.md               # Frontend README
```

### Documentation Index

Detailed documentation is now consolidated at multiple levels:
1. **Details/** (Root-level comprehensive guides)
   - [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md): Structural diagrams and data flow
   - [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md): Complete directory and module documentation
   - [ALGORITHM_SPECIFICATION.md](ALGORITHM_SPECIFICATION.md): Core seating logic and constraints

2. **Frontend/docs/** (Docusaurus site)
   - User guides for administrators and examiners
   - Developer API documentation
   - Architecture deep-dives

3. **algo/** (Module-level documentation)
   - [README.md](../algo/README.md): Backend features and setup
   - [HYBRID_CACHING_GUIDE.md](../algo/HYBRID_CACHING_GUIDE.md): Caching strategy details

---

## 🔄 Data Flow Architecture

### Seating Generation Workflow
```
User Input (UI)
    ↓
[allocations.py] Parse & validate
    ↓
[allocation_service.py] Prepare batch data
    ↓
[seating.py] Run algorithm
    ↓
[cache_manager.py] Save L1 snapshot
    ↓
[Response] Return to UI
    ↓
[SeatingGrid.jsx] Render visualization
```

### PDF Generation Workflow
```
Export Request (UI)
    ↓
[pdf.py] Route request
    ↓
[cache_manager.py] Load from L1 Cache
    ↓
[pdf_generation.py] Render PDF
    ↓
[L2 Cache] Store rendered file (if new)
    ↓
[Response] Return to UI
```

### Master Plan Workflow 🆕
```
Master Plan Request (UI)
    ↓
[master_plan_pdf.py] Aggregate all rooms
    ↓
[cache_manager.py] Load multi-room snapshots
    ↓
[Branch Detection] Determine batch metadata
    ↓
[reportlab] Render A4 document
    ↓
[Response] Return PDF (in-memory)
```

---

## 📦 Dependency Management

### Backend (`algo/requirements.txt`)
- **Flask**: Web framework
- **ReportLab**: PDF generation
- **SQLAlchemy**: ORM (if used)
- **Openpyxl/xlrd**: Excel parsing
- **python-dotenv**: Environment management

### Frontend (`Frontend/package.json`)
- **React 18**: UI framework
- **React Router DOM v6**: Routing
- **Axios**: HTTP client
- **Tailwind CSS**: Styling
- **GSAP**: Animations
- **Framer Motion**: Page transitions

---

## 🆕 New Modules in v2.4

| Module | Purpose | Location |
| :--- | :--- | :--- |
| **master_plan_pdf.py** | Institutional-level reporting | `algo/api/blueprints/` |
| **feedback.py** | User feedback collection | `algo/api/blueprints/` |
| **templates.py** | Template management endpoints | `algo/api/blueprints/` |
| **Branch Detection** | Majority-based identification | `algo/core/cache/cache_manager.py` |
| **Variable Blocks** | Non-uniform column groupings | `algo/core/algorithm/seating.py` |
| **Adjacent Seating** | Single-batch seating mode | `algo/core/algorithm/seating.py` |

---
*Last Updated: February 2026 | Version: v2.4*
