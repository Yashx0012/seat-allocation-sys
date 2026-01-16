# Seat Allocation System - System Architecture

This document provides the authoritative overview of the Seat Allocation System's modernized, modular architecture, detailing its layers, data flow, and core components.

## 🏗️ High-Level Architecture

The system follows a highly decoupled model consisting of four distinct layers, promoting separation of concerns and scalability.

```mermaid
graph TB
    subgraph Layer1["Layer 1: PRESENTATION (Frontend)"]
        HTML["React/JS Components"]
        GRID["Seating Grid Display"]
        PDF_BTN["Export/Reporting UI"]
    end
    
    subgraph Layer2["Layer 2: API (Flask Blueprints)"]
        A1["POST /api/generate-seating"]
        A2["POST /api/generate-pdf"]
        A3["GET /api/sessions/active"]
    end
    
    subgraph Layer3["Layer 3: BUSINESS LOGIC (Services)"]
        B1["SeatingAlgorithm Engine"]
        B2["Session & Student Services"]
        B3["PDF & Attendance Generators"]
    end
    
    subgraph Layer4["Layer 4: DATA (Persistence & Cache)"]
        D1["SQLite (Main DB)"]
        D2["L1 JSON Cache (Snapshots)"]
        D3["L2 PDF Cache (Renderings)"]
    end
    
    Layer1 -->|HTTP/JSON| Layer2
    Layer2 -->|Orchestrates| Layer3
    Layer3 -->|Persists/Retrieves| Layer4
    Layer4 -->|Returns Data| Layer3
    Layer3 -->|Returns Result| Layer2
    Layer2 -->|Response| Layer1
```

---

## 📂 Project Directory Map

```text
.
├── algo/                    # 🧠 Main Modular Backend
│   ├── api/                 # 📡 Communication Layer (Flask Blueprints)
│   │   └── blueprints/      # sessions, allocations, pdf, classrooms, dashboard, etc.
│   ├── core/                # ⚡ Business Logic Layer
│   │   ├── algorithm/       # Core Seating Optimization Algorithm
│   │   ├── cache/           # Hybrid L1 Cache Manager
│   │   └── models/          # Shared Dataclasses (Seat, PaperSet)
│   ├── database/            # 🗄️ Persistence Layer (Queries & Schema)
│   ├── services/            # 🛠️ Orchestration Layer (SessionService, etc.)
│   ├── config/              # ⚙️ Environment Configuration
│   ├── cache/               # 💾 JSON Cache Repository (PLAN-XXXX.json)
│   ├── pdf_gen/             # 📄 PDF Generation Engine
│   ├── utils/               # 🛠️ Helpers & Data Parsers
│   ├── app.py               # 🚀 Main Entry Point (Port 5000)
│   └── main.py              # 🏭 Flask App Factory System
├── Frontend/                # 💻 React User Interface (Port 3000)
└── demo.db                  # 📊 Main SQLite Data Store
```

---

## 🔄 Core Data Flows

### 1. Seating Generation Flow
The process of transforming student batches and classroom configurations into a validated seating plan.

```mermaid
flowchart TD
    A["👤 User Input<br/>Rows, Cols, Batches"] --> B["📤 POST /api/generate-seating"]
    B --> C["📥 Parse & Convert<br/>Input Data"]
    C --> D["🔧 Instantiate SeatingAlgorithm"]
    D --> E["🎲 Run Allocation Engine"]
    E --> F["📊 Calculate Distribution"]
    F --> G["🔄 Assign Columns to Batches"]
    G --> H["📝 Map Students to Seats"]
    H --> I["✔️ Validate Constraints<br/>P1-P3 Priority Checks"]
    I --> J["💾 Save Snapshot to L1 Cache"]
    J --> K["📥 Return JSON Result"]
    K --> L["🎨 Render Grid in UI"]
```

### 2. PDF Reporting Flow (L2 Caching)
How the system efficiently converts seating snapshots into printable reports.

```mermaid
flowchart TD
    A["📥 Trigger PDF Export"] --> B["🔍 Check L1 Cache<br/>(PLAN-ID.json)"]
    B -- Found --> C["📋 Pass Data to PDF Engine"]
    B -- Not Found --> D["🗄️ Fallback to Database"]
    D --> C
    C --> E["🧪 Generate Content Hash"]
    E --> F{"🔍 Check L2 Cache<br/>(Generated PDF?)"}
    F -- Hit --> G["⚡ Instant Return (L2 Cache)"]
    F -- Miss --> H["🎨 Render New PDF Layout"]
    H --> I["💾 Save to L2 Cache"]
    I --> G
```

---

## 🛠️ Key Architectural Components

### Hybrid Caching (Dual-Layer)
- **L1 (Data Layer)**: Located in `algo/core/cache/`. Manages JSON seating snapshots within `PLAN-<session_id>.json`. This avoids re-running the algorithm for every view/PDF request.
- **L2 (File Layer)**: Located in `algo/pdf_gen/`. Stores rendered PDF files indexed by a hash of their content and template.

### Session Lifecycle Management
- **One Session, One File**: Active sessions isolate their trial allocations in a single JSON file.
- **Experimental Pruning**: "Trial" rooms are stored during a session but automatically pruned by the `finalize_rooms` engine upon session completion, keeping the file system lean.

### Domain Models
```mermaid
classDiagram
    class PaperSet {
        <<enum>>
        A
        B
    }
    class Seat {
        +int row
        +int col
        +int batch
        +PaperSet paper_set
        +str roll_number
        +bool is_broken
    }
    class SeatingAlgorithm {
        +generate_seating()
        +validate_constraints()
        +to_web_format()
    }
    SeatingAlgorithm *-- Seat
    Seat o-- PaperSet
```

---
*Documentation State: Modular v2.3*
