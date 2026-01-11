---
sidebar_position: 4
---

import ComplexityCards from '@site/src/components/complexitycards';

# System Architecture

Complete system design and data flow documentation.

## High-Level Architecture

```mermaid
graph TB
    %% Styles matching the reference image explanation
    classDef client fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1,rx:5,ry:5
    classDef api fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20,rx:5,ry:5
    classDef algo fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c,rx:5,ry:5
    classDef router fill:#fff3e0,stroke:#ff6d00,stroke-width:2px,color:#e65100,stroke-dasharray: 5 5,shape:circle
    classDef spacerNode width:0px,height:50px,fill:none,stroke:none;
    %% Label Node Style (White box, clear border, rounded like others)
    classDef labelNode fill:#ffffff,stroke:#333333,stroke-width:1px,rx:5,ry:5,color:#000
    
            classDef transparentBox fill:none,stroke:none;
    %% Orange Thicker Arrows
    linkStyle default stroke:#ff9800,stroke-width:4px,fill:none

    %% CLIENT LAYER (Horizontal)
    subgraph Client[" "]
 direction TB
        style Client fill:transparent,stroke-width:0px,color:#ff9800
        %% --- 1. THE NEW BOX ABOVE ---
        
        %% --- 2. THE ROW BELOW (Nested Subgraph) ---
        subgraph ClientRow[" "]
            direction LR
            style ClientRow fill:none,stroke:none
            %% EXISTING NODES
            HTML["HTML Form Inputs"]:::client
            GRID["Seating Grid Display"]:::client
            SUMMARY["Summary Statistics"]:::client
            MODAL["Constraints Modal"]:::client
            PDF["PDF/Attendance Export"]:::client
            MANUAL["Manual Adjustments"]:::client
            FEEDBACK["Feedback System"]:::client
        end
    end
       
    %% API LAYER (Vertical with Router)
    %% Moved label to side using spaces to avoid arrow overlap
    subgraph API[" "]
        direction TB
        style API fill:transparent,stroke-width:0px,color:#ff9800
        
        ROUTER((" / Flask Router / ")):::router
        
        GET[" GET / "]:::api
        POST1["POST /api/generate-seating"]:::api
        POST2["POST /api/constraints-status"]:::api
        
        %% Internal API Label Nodes
        L_ROUTE1["Route"]:::labelNode
        L_ROUTE2["Route"]:::labelNode
        L_ROUTE3["Route"]:::labelNode

        ROUTER --> L_ROUTE1 --> GET
        ROUTER --> L_ROUTE2 --> POST1
        ROUTER --> L_ROUTE3 --> POST2
    end
    
    %% ALGORITHM LAYER (Bottom)
    %% Shift Left via padding-right
    subgraph Algorithm[" "]
        direction TB
        style Algorithm fill:transparent,stroke-width:0px,color:#ff9800

        
        SA["SeatingAlgorithm"]:::algo
        SC["Seat Class"]:::algo
        PS["PaperSet Enum"]:::algo
        METHODS["20+ Methods"]:::algo
        ATT["Attendance Generator"]:::algo
        LEFT["Leftover Calculator"]:::algo
        
        SA -.-> SC
        SA -.-> PS
        SA -.-> METHODS
        SA -.-> ATT
        SA -.-> LEFT
    end
    
    %% Inter-Layer Connections with Label Nodes
    L_JSON["JSON via HTTP"]:::labelNode
    L_PY["Python Objects"]:::labelNode
    L_STATUS["Status Check"]:::labelNode

    MODAL --> L_JSON --> ROUTER
    POST1 --> L_PY --> SA
    POST2 --> L_STATUS --> SA
```

## Data Flow Diagram

### Generation Flow

```mermaid
flowchart TD
    A["User fills form<br/>rows, cols, batches, etc."]
    B["Frontend validates inputs<br/>client-side"]
    C["Send POST /api/generate-seating<br/>JSON payload"]
    D["Backend receives JSON<br/>Parse & Convert formats"]
    E["Create SeatingAlgorithm instance<br/>Store parameters"]
    F["Call generate_seating"]
    G["Calculate batch distribution"]
    H["For each column<br/>Assign to batch"]
    I["For each row<br/>Create/Assign seat"]
    J["Call validate_constraints<br/>Check all constraints"]
    K["Call get_constraints_status<br/>Detailed info"]
    L["Call _generate_summary<br/>Statistics"]
    M["Convert to_web_format<br/>JSON output"]
    N["Return JSON response"]
    O["Frontend receives response"]
    P["Render seating grid"]
    Q["Display summary"]
    R["Show validation status"]
    S["END - Display seating"]
    
    A --> B --> C --> D --> E --> F
    F --> G --> H --> I
    I --> J --> K --> L --> M --> N
    N --> O --> P --> Q --> R --> S
    
    style A fill:#e1f5ff
    style F fill:#fff9c4
    style J fill:#c8e6c9
    style S fill:#f8bbd0
```

## Seating Generation Algorithm

### Column-Based Batch Assignment

```mermaid
graph TB
    A["10 Columns, 3 Batches"]
    B["Calculate Distribution"]
    C["base_cols = 10 / 3 = 3<br/>remainder = 10 mod 3 = 1"]
    D["Assign columns to batches"]
    E["Batch 1: 3+1=4 cols<br/>Batch 2: 3+0=3 cols<br/>Batch 3: 3+0=3 cols"]
    F["Apply modulo mapping<br/>col_batch = col mod num_batches"]
    G["Fill columns top-to-bottom"]
    H["For each batch column:<br/>Row 0: Roll1<br/>Row 1: Roll2<br/>Row 2: Roll3..."]
    I["Apply constraints"]
    J["Skip broken | Check limits<br/>Assign paper sets | Color coding<br/>Mark unallocated"]
    K["Seating complete"]
    
    A --> B --> C --> D --> E
    E --> F --> G --> H --> I --> J --> K
```

## Input Parsing Flow

```mermaid
graph TB
    A["HTML Form Fields"]
    B["Numeric Parsing<br/>rows, cols, num_batches"]
    C["Boolean Parsing<br/>batch_by_column, enforce_rules"]
    D["CSV Parsing<br/>batch_student_counts"]
    E["Row-Col Parsing<br/>broken_seats"]
    F["Template Parsing<br/>roll_template"]
    G["Consolidated<br/>Python Dictionary"]
    
    A --> B --> G
    A --> C --> G
    A --> D --> G
    A --> E --> G
    A --> F --> G
```

### Input Format Transformations

| Input Type | Format | Example | Parsed As |
|---|---|---|---|
| Rows | Integer | 8 | 8 |
| Columns | Integer | 10 | 10 |
| Batches | Integer | 3 | 3 |
| Block Width | Integer | 2 | 2 |
| Batch Counts | CSV | "1:10,2:8" | Dictionary mapping batch numbers to counts |
| Broken Seats | CSV | "1-1,2-3" | List of coordinate tuples for unavailable seats |
| Start Rolls | CSV | "1:BTCS24O1001" | Dictionary mapping batch numbers to starting roll numbers |
| Batch Prefixes | CSV | "BTCS,BTCD" | List of prefixes for each batch |
| Year | Integer | 2024 | 2024 |
| Template | String | `"{prefix}{year}O{serial}"` | str |
| Serial Width | Integer | 4 | 4 |
| Flags | Checkbox | true/false | Boolean |

## Output Generation Flow

```mermaid
graph TB
    A["Seat Object<br/>row, col, batch,<br/>paper_set, roll"]
    B["Convert to Web Format<br/>to_web_format"]
    C["Add Display Data<br/>position, color, display"]
    D["Build Metadata<br/>rows, cols, blocks"]
    E["Calculate Summary<br/>total_allocated,<br/>batch_distribution"]
    F["Run Validation<br/>All constraints<br/>Priority system"]
    G["Build JSON Response<br/>seating array"]
    H["Add Constraints Status<br/>Detailed info"]
    I["Return to Frontend<br/>HTTP 200"]
    
    A --> B --> C --> D
    D --> E --> F
    E --> G --> H --> I
```

## Constraint Validation Flow

```mermaid
graph TB
    A["Seating Data<br/>All seats allocated"]
    B["Check Constraint 1<br/>Broken Seats"]
    C{Valid?}
    C -->|No| E["Mark Error<br/>HIGH Priority"]
    C -->|Yes| F["Passed"]
    
    F --> G["Check Constraint 2<br/>Batch Limits"]
    H{Valid?}
    H -->|No| I["Mark Error<br/>HIGH Priority"]
    H -->|Yes| J["Passed"]
    
    J --> K["Repeat for<br/>8 Constraints"]
    K --> L["Compile Status<br/>All results"]
    L --> M["Generate Report<br/>Valid/Invalid<br/>Errors/Warnings"]
    
    E --> L
    I --> L
    
    style A fill:#e3f2fd
    style M fill:#c8e6c9
```

## PDF Export Workflow

```mermaid
graph TB
    A["User clicks<br/>Export PDF"]
    B["Collect current<br/>seating data"]
    C["Generate HTML<br/>Responsive grid<br/>Styling"]
    D["Configure PDF<br/>Options"]
    E["html2pdf.js<br/>Convert to PDF"]
    F["Generate filename<br/>seating_TIMESTAMP.pdf"]
    G["Trigger download<br/>Browser"]
    H["PDF Saved<br/>to device"]
    
    A --> B --> C --> D --> E --> F --> G --> H
```

## UML Class Relationships

```mermaid
classDiagram
    class PaperSet {
        <<enumeration>>
        A
        B
    }
    
    class Seat {
        row: int
        col: int
        batch: Optional[int]
        paper_set: Optional[PaperSet]
        block: Optional[int]
        roll_number: Optional[str]
        is_broken: bool
        color: str
        to_web_format()
    }
    
    class SeatingAlgorithm {
        rows: int
        cols: int
        num_batches: int
        seating: List[List[Seat]]
        generate_seating()
        validate_constraints()
        get_constraints_status()
    }
    
    SeatingAlgorithm --> Seat : creates
    Seat --> PaperSet : uses
```

## Seat State Transitions

```mermaid
stateDiagram-v2
    [*] --> EMPTY
    EMPTY --> BROKEN: is_broken == True
    EMPTY --> ALLOCATED: Student assigned
    EMPTY --> UNALLOCATED: Batch limit exceeded
    BROKEN --> BROKEN: Final state
    ALLOCATED --> ALLOCATED: Final state
    UNALLOCATED --> UNALLOCATED: Final state
    
    note right of BROKEN
        No student will occupy
        Marked during initialization
    end note
    
    note right of ALLOCATED
        Student assigned
        Roll number, batch, paper set
    end note
    
    note right of UNALLOCATED
        Available but no student
        Batch limit or insufficient students
    end note
```

## API Request/Response Cycle

### Request Structure
```json
{
  "rows": 8,
  "cols": 10,
  "num_batches": 3,
  "block_width": 2,
  "batch_student_counts": "1:10,2:8,3:7",
  "broken_seats": "1-1,2-2",
  "start_rolls": "1:BTCS24O1001,2:BTCD24O2001",
  "batch_prefixes": "BTCS,BTCD,BTCE",
  "year": 2024,
  "roll_template": "{prefix}{year}O{serial}",
  "serial_width": 4,
  "batch_by_column": true,
  "enforce_no_adjacent_batches": false
}
```

### Response Structure
```json
{
  "success": true,
  "metadata": { /* dimensions and configuration */ },
  "seating": [ /* 2D array of seat objects */ ],
  "summary": { /* statistics */ },
  "validation": { /* validation results */ },
  "constraints_status": { /* detailed constraint info */ }
}
```

## Database Schema

### Authentication System

```mermaid
erDiagram
    USERS ||--o{ SESSIONS : has
    
    USERS {
        int id PK
        string username UK
        string email UK
        string password
        string role
        timestamp created_at
    }
    
    SESSIONS {
        int id PK
        int user_id FK
        string token
        timestamp created_at
    }
```
### System Performance Metrics
<ComplexityCards />

## Extension Points

### Adding New Constraints

```python
# In SeatingAlgorithm class
def validate_custom_constraint(self):
    """Add your constraint logic here"""
    for row in self.seating:
        for seat in row:
            # Validation logic
            pass
```

### Customizing Colors

```python
# Color mapping in SeatingAlgorithm
BATCH_COLORS = {
    1: "#DBEAFE",
    2: "#D1FAE5",
    3: "#FEE2E2",
    # Add more batches
}
```

### Adding Roll Number Formats

```python
# Template variations
"{prefix}{year}O{serial}"      # BTCS24O1001
"{prefix}-{year}-{serial}"     # BTCS-24-1001
"{prefix}{serial}"             # BTCS1001
```

## Testing Strategy

```mermaid
graph TB
    A["Unit Tests"]
    B["Test individual methods"]
    C["Seat creation, batch assignment"]
    
    D["Integration Tests"]
    E["Test algorithm end-to-end"]
    F["Generate seating, validate output"]
    
    G["End-to-End Tests"]
    H["Test complete API flow"]
    I["Form → API → Grid Display"]
    
    A --> C
    D --> F
    G --> I
```

---

**Version**: 2.1  
**Last Updated**: January 2026
