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
│       ├── health.py        # System diagnostic checks
│       ├── pdf.py           # PDF export orchestration
│       ├── plans.py         # History & Recent plans
│       ├── sessions.py      # Session lifecycle & Undo
│       └── students.py      # Student data management
│
├── core/                    # ⚡ Business Logic Layer
│   ├── algorithm/           # The Engine
│   │   └── seating.py       # SeatingAlgorithm Core logic
│   ├── cache/               # Performance Layer
│   │   └── cache_manager.py # Hybrid L1/L2 Cache Engine
│   └── models/              # Shared Definitions
│       └── models.py        # Seat & PaperSet Dataclasses
│
├── database/                # 🗄️ Persistence Layer
│   ├── queries/             # Modular SQL repository
│   ├── db.py                # Connection pool & context
│   └── schema.py            # SQL table definitions
│
├── services/                # 🛠️ Orchestration Layer
│   ├── session_service.py   # Transactional session logic
│   ├── student_service.py   # Bulk data handling
│   └── allocation_service.py# High-level allocation logic
│
├── pdf_gen/                 # 📄 PDF Generation Engine
│   └── pdf_gen.py           # Reportlab implementation
│
├── utils/                   # 🛠️ Helpers
│   ├── helpers.py           # String/Date utilities
│   └── parser.py            # CSV/Excel parsing
│
├── app.py                   # 🚀 Flask Entry Point (Main)
├── main.py                  # Factory & Blueprint Registry
└── auth_service.py          # Legacy Auth wrapper (bridging)
```

### Frontend Structure (`Frontend/`)

```text
Frontend/
├── src/
│   ├── components/          # Reusable UI Atoms/Molecules
│   ├── context/             # Global Store (Auth, Session)
│   ├── hooks/               # Custom React Hooks
│   ├── pages/               # Top-level Route Components
│   ├── services/            # API Client (Axios wrappers)
│   └── utils/               # Formatters & Constants
└── public/                  # Static Assets
```

### Documentation Index

Detailed documentation is now consolidated into three root-level files:
1. [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md): Structural diagrams and data flow.
2. [TECHNICAL_DEVELOPER_GUIDE.md](TECHNICAL_DEVELOPER_GUIDE.md): API specs and service usage.
3. [ALGORITHM_SPECIFICATION.md](ALGORITHM_SPECIFICATION.md): Core seating logic and constraints.

---
*Last Updated: January 2026*
