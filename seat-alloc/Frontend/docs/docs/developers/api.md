---
sidebar_position: 5
---

import CodeHeader from '@site/src/components/filetypeheaderstyle';

import ComplexityCards from '@site/src/components/complexitycards';

# 🔌 API Technical Reference

<ComplexityCards />

Fast developer integration and comprehensive REST API workflows.

**Version: v2.4 | Updated: February 2026**

## 5-Minute Setup

### Backend Setup
<CodeHeader title="BASH">
{`cd algo
pip install -r requirements.txt
python app.py
# Running on http://localhost:5000`}
</CodeHeader>

### Frontend Setup
<CodeHeader title="BASH">
{`cd Frontend
npm install
npm start
# Running on http://localhost:3000`}
</CodeHeader>

## Simple API Call

### JavaScript/Fetch
<CodeHeader title="JAVASCRIPT">
{`async function generateSeating() {
  const response = await fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      rows: 8,
      cols: 10,
      num_batches: 3,
      block_width: 2
    })
  });
  return await response.json();
}`}
</CodeHeader>

### React Hook
<CodeHeader title="REACT HOOK">
{`const [seating, setSeating] = useState(null);

const handleGenerate = async (params) => {
  const response = await fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  const data = await response.json();
  setSeating(data);
};`}
</CodeHeader>

### Vue.js
<CodeHeader title="VUE.JS">
{`async generateSeating(params) {
  const response = await fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  return response.json();
}`}
</CodeHeader>

### Angular
<CodeHeader title="TYPESCRIPT">
{`generateSeating(params: any): Observable<any> {
  return this.http.post('/api/generate-seating', params);
}`}
</CodeHeader>

## Access Results

<CodeHeader title="JAVASCRIPT">
{`const data = await generateSeating();

// Seating grid (2D array)
data.seating[row][col] 
// Output: {
//   position: "A1",
//   batch: 1,
//   roll_number: "BTCS24O1001",
//   color: "#DBEAFE",
//   ...
// }

// Summary stats
data.summary.total_available_seats      // 78
data.summary.total_allocated_students   // 25
data.summary.batch_distribution         // {1: 10, 2: 8, 3: 7}

// Validation <span style={{ backgroundColor: '#f97316', color: 'white', padding: '1px 6px', borderRadius: '4px', fontSize: '0.6rem' }}>PRAGMATIC MODEL</span>
data.validation.is_valid                // true/false
data.validation.errors                  // ["physical collision at ..."]
data.validation.warnings                // ["paper set sequence gap at ..."]

// Constraints
data.constraints_status.constraints     // Array of constraint objects`}
</CodeHeader>

## Input/Output Quick Reference

### Minimal Input (Required Only)
<CodeHeader title="JSON">
{`{
  "rows": 8,
  "cols": 10,
  "num_batches": 3,
  "block_width": 2
}`}
</CodeHeader>

### Full Input (All Options)
<CodeHeader title="JSON">
{`{
  "rows": 8,
  "cols": 10,
  "num_batches": 3,
  "block_width": 2,
  
  "batch_student_counts": "1:10,2:8,3:7",
  "broken_seats": "1-1,1-2,2-3",
  "start_rolls": "1:BTCS24O1001,2:BTCD24O2001",
  "batch_prefixes": "BTCS,BTCD,BTCE",
  "year": 2024,
  "roll_template": "{prefix}{year}O{serial}",
  "serial_width": 4,
  
  "batch_by_column": true,
  "allow_adjacent_same_batch": false,
  "batch_roll_numbers": {
    "1": ["Student1", "Student2"],
    "2": ["Student3", "Student4"]
  }
}`}
</CodeHeader>

### Output Response
<CodeHeader title="JSON">
{`{
  "success": true,
  "metadata": {
    "rows": 8,
    "cols": 10,
    "num_batches": 3,
    "blocks": 5,
    "block_width": 2
  },
  "seating": [
    [
      {
        "position": "A1",
        "batch": 1,
        "paper_set": "A",
        "block": 0,
        "roll_number": "BTCS24O1001",
        "is_broken": false,
        "is_unallocated": false,
        "display": "BTCS24O1001A",
        "color": "#DBEAFE"
      },
      // ... more seats
    ]
    // ... more rows
  ],
  "summary": {
    "total_available_seats": 78,
    "total_allocated_students": 25,
    "total_unallocated_seats": 53,
    "batch_distribution": {
      "1": 10,
      "2": 8,
      "3": 7
    }
  },
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  },
  "constraints_status": {
    "constraints": [
      {
        "name": "broken_seats",
        "priority": "high",
        "satisfied": true,
        "message": "All broken seats properly marked"
      }
      // ... more constraints
    ]
  }
}`}
</CodeHeader>

## Common Workflows

### Workflow 1: Basic Generation

<CodeHeader title="JAVASCRIPT">
{`async function basicGeneration() {
  const params = {
    rows: 8,
    cols: 10,
    num_batches: 3,
    block_width: 2
  };
  
  const result = await fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  }).then(r => r.json());
  
  return result;
}`}
</CodeHeader>

### Workflow 1.5: Generate Attendance
<CodeHeader title="JAVASCRIPT">
{`async function downloadAttendance(sessionId) {
  const response = await fetch(\`/api/generate-attendance\`, {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId })
  });
  // Handle blob download
}`}
</CodeHeader>

### Workflow 1.6: Save Manual Changes
<CodeHeader title="JAVASCRIPT">
{`async function saveManual(allocationData) {
   await fetch('/api/save-room-allocation', {
     method: 'POST',
     body: JSON.stringify(allocationData)
   });
}`}
</CodeHeader>

### Workflow 2: With Student Limits

<CodeHeader title="JAVASCRIPT">
{`async function generationWithLimits() {
  const params = {
    rows: 8,
    cols: 10,
    num_batches: 3,
    block_width: 2,
    batch_student_counts: "1:20,2:15,3:12"
  };
  
  return fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  }).then(r => r.json());
}`}
</CodeHeader>

### Workflow 3: With Broken Seats

<CodeHeader title="JAVASCRIPT">
{`async function generationWithBrokenSeats() {
  const params = {
    rows: 8,
    cols: 10,
    num_batches: 3,
    block_width: 2,
    broken_seats: "0-1,0-2,3-5,7-9"
  };
  
  return fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  }).then(r => r.json());
}`}
</CodeHeader>

### Workflow 4: Custom Roll Numbers

<CodeHeader title="JAVASCRIPT">
{`async function customRollNumbers() {
  const params = {
    rows: 8,
    cols: 10,
    num_batches: 2,
    block_width: 2,
    batch_prefixes: "CS,EC",
    year: 2024,
    start_rolls: "1:CS24O1001,2:EC24O2001",
    roll_template: "{prefix}{year}O{serial}",
    serial_width: 4
  };
  
  return fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  }).then(r => r.json());
}`}
</CodeHeader>

### Workflow 5: Complete Configuration

<CodeHeader title="JAVASCRIPT">
{`async function completeConfiguration() {
  const params = {
    rows: 10,
    cols: 12,
    num_batches: 4,
    block_width: 3,
    batch_student_counts: "1:25,2:20,3:18,4:15",
    broken_seats: "0-1,2-5,5-11",
    start_rolls: "1:BTCS24O1001,2:BTCD24O2001,3:BTCE24O3001,4:BTCM24O4001",
    batch_prefixes: "BTCS,BTCD,BTCE,BTCM",
    year: 2024,
    roll_template: "{prefix}{year}O{serial}",
    serial_width: 4,
    batch_by_column: true,
    allow_adjacent_same_batch: false  // NEW v2.4: Enable for single-batch adjacent seating
  };
  
  return fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  }).then(r => r.json());
}`}
</CodeHeader>

## Component Examples

### React Grid Renderer

<CodeHeader title="REACT">
{`function SeatingGrid({ seating }) {
  return (
    <div className="grid gap-1 p-4">
      {seating.map((row, rowIdx) => (
        <div key={rowIdx} className="flex gap-1">
          {row.map((seat, colIdx) => (
            <div
              key={\`\${rowIdx}-\${colIdx}\`}
              style={{
                backgroundColor: seat.color,
                border: seat.is_broken ? '2px solid red' : '1px solid black',
                padding: '8px',
                minWidth: '80px',
                textAlign: 'center'
              }}
            >
              {seat.is_broken ? '✗' : seat.roll_number || '-'}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}`}
</CodeHeader>

### Vue Seating Component

<CodeHeader title="VUE.JS">
{`<template>
  <div class="seating-grid">
    <div v-for="(row, rowIdx) in seating" :key="rowIdx" class="grid-row">
      <div
        v-for="(seat, colIdx) in row"
        :key="\`\${rowIdx}-\${colIdx}\`"
        :style="{ backgroundColor: seat.color }"
        :class="{ broken: seat.is_broken }"
      >
        {{ seat.is_broken ? '✗' : seat.roll_number || '-' }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    seating: Array
  }
};
</script>`}
</CodeHeader>

### Angular Component

<CodeHeader title="ANGULAR">
{`import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-seating-grid',
  template: \`
    <div class="seating-grid">
      <div *ngFor="let row of seating; let i = index" class="grid-row">
        <div
          *ngFor="let seat of row; let j = index"
          [style.backgroundColor]="seat.color"
          [class.broken]="seat.is_broken"
        >
          {{ seat.is_broken ? '✗' : seat.roll_number || '-' }}
        </div>
      </div>
    </div>
  \`
})
export class SeatingGridComponent {
  @Input() seating: any[];
}`}
</CodeHeader>

## Color Reference

### Default Batch Colors

<CodeHeader title="TEXT">
{`Batch 1: #DBEAFE (Light Blue)    RGB(219, 234, 254)
Batch 2: #D1FAE5 (Light Green)   RGB(209, 250, 229)
Batch 3: #FEE2E2 (Light Red)     RGB(254, 226, 226)
Batch 4: #FEF3C7 (Light Yellow)  RGB(254, 243, 199)
Batch 5: #F3E8FF (Light Purple)  RGB(243, 232, 255)`}
</CodeHeader>

### Special Statuses

<CodeHeader title="TEXT">
{`Broken Seat:     Border #FF0000 (Red)
Unallocated:     Gray background
Empty:           White background`}
</CodeHeader>

## Debugging Workflow

### Step 1: Verify Input

<CodeHeader title="JAVASCRIPT">
{`// Check input format
console.log("Input:", params);
// Should have all required fields
// Values should be correct types`}
</CodeHeader>

### Step 2: Make API Call

<CodeHeader title="JAVASCRIPT">
{`// Log response
const response = await fetch('/api/generate-seating', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(params)
});

console.log("Status:", response.status);
const data = await response.json();
console.log("Response:", data);`}
</CodeHeader>

### Step 3: Check Validation

<CodeHeader title="JAVASCRIPT">
{`// Check if seating is valid
if (data.validation.is_valid) {
  console.log("✓ Seating is valid");
} else {
  console.error("✗ Validation errors:", data.validation.errors);
}`}
</CodeHeader>

### Step 4: Inspect Constraints

<CodeHeader title="JAVASCRIPT">
{`// Check constraint details
data.constraints_status.constraints.forEach(c => {
  console.log(\`\${c.name}: \${c.satisfied ? 'PASS' : 'FAIL'} (\${c.priority})\`);
});`}
</CodeHeader>

### Step 5: Render and Verify

<CodeHeader title="JAVASCRIPT">
{`// Render grid and visually verify
// Check for:
// - Correct number of batches
// - Proper roll number formatting
// - Correct colors
// - Broken seats marked properly`}
</CodeHeader>


## Error Handling

### Common Errors

| Error | Cause | Solution |
|---|---|---|
| 400 Bad Request | Invalid input format | Check JSON syntax |
| 422 Unprocessable | Constraint violation | Review error details |
| 500 Server Error | Backend exception | Check server logs |

### Error Response Example

<CodeHeader title="JSON">
{`{
  "success": false,
  "error": "Invalid rows parameter",
  "details": {
    "field": "rows",
    "message": "Must be integer > 0"
  }
}`}
</CodeHeader>

## File Structure Reference

<CodeHeader title="FILE STRUCTURE">
{`seat-allocation-sys/
├── algo/
│   ├── app.py                 # Flask app
│   ├── core/algorithm/seating.py  # Algorithm core
│   ├── auth_service.py        # Authentication
│   ├── requirements.txt       # Python dependencies
│   └── ...
├── Frontend/
│   ├── src/
│   │   ├── App.jsx          # Main component
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable components
│   │   └── context/         # Context providers
│   └── package.json         # npm dependencies
└── docs/
    └── docs/               # Documentation`}
</CodeHeader>

---

## New in v2.4

### Master Plan PDF Endpoint

<CodeHeader title="POST /api/generate-master-plan">
{`// Request (Full Form with All Options)
{
  "plan_id": "PLAN-ABC123",
  "dept_name": "Department of Computer Science & Engineering",
  "exam_name": "Minor-II Examination, November 2025",
  "date_text": "15th February 2026",
  "title": "Master Seating Plan",
  "left_sign_name": "Coordinator Name",
  "left_sign_title": "Course Coordinator",
  "right_sign_name": "HOD Name",
  "right_sign_title": "Head of Department"
}

// Response: Binary PDF (Content-Type: application/pdf)
// Features:
// - A4 format with institutional branding
// - Multi-room aggregation
// - Auto-detected branch metadata
// - Roll number ranges per room
// - Grand totals with branch segregation
// - In-memory rendering (no disk cache)
// - Signature fields for authorization`}
</CodeHeader>

**Endpoint Details:**
- **Path**: `POST /api/generate-master-plan`
- **Auth**: Required (JWT token)
- **Response Type**: Binary PDF
- **Cache Status**: In-memory only (no L2 caching)
- **Latency**: 1000-2000ms for 20 rooms

**Master Plan Content:**
- Table with columns: Branch | Semester | Room No | From Roll | To Roll | Total | Grand Total
- Signature section with date and officer details
- Department header with exam name
- Footer with generation metadata

### GET /api/plan-batches/{plan_id}

<CodeHeader title="Endpoint Details">
{`// Retrieve plan metadata and room-wise batch information
GET /api/plan-batches/PLAN-ABC123

// Response
{
  "metadata": {
    "plan_id": "PLAN-ABC123",
    "total_students": 240,
    "room_count": 3,
    "batch_count": 4,
    "status": "FINALIZED",
    "active_rooms": ["M101", "M102", "M103"],
    "created_at": "2026-02-23T10:00:00Z"
  },
  "rooms": {
    "M101": {
      "batches": {
        "Batch A": {
          "info": {
            "branch": "CS",
            "degree": "B.Tech",
            "joining_year": "2024"
          },
          "students": [
            {
              "roll_number": "BTCS24O1001",
              "name": "Student Name",
              "position": "A1",
              "paper_set": "A"
            }
          ],
          "count": 75
        }
      }
    }
  }
}`}
</CodeHeader>

### GET /api/template/config

<CodeHeader title="Load Template Configuration">
{`// Retrieve template configuration for pre-filling master plan form
GET /api/template/config

// Response
{
  "success": true,
  "template": {
    "dept_name": "Department of Computer Science & Engineering",
    "exam_details": "Minor-II Examination",
    "coordinator_name": "Dr. John Doe",
    "coordinator_title": "Course Coordinator",
    "hod_name": "Prof. Jane Smith",
    "hod_title": "Head of Department"
  }
}`}
</CodeHeader>

## 🆕 New in v2.4

### Variable Block Structures

<CodeHeader title="JSON - New Parameter">
{`{
  "block_width": 3,          // Legacy: uniform width
  "block_structure": [3, 2, 3] // 🆕 Variable widths (takes precedence)
}

// Result: 8 columns grouped as [3], [2], [3]
// Use case: Irregular classroom layouts`}
</CodeHeader>

### Adjacent Seating Control

<CodeHeader title="JSON - New Parameter">
{`{
  "num_batches": 1,
  "allow_adjacent_same_batch": true  // 🆕 Enable horizontal adjacency
}

// When true:
// - Gap columns NOT inserted
// - Same-batch students sit horizontally adjacent
// - P1-P3 paper set constraints still enforced
// - Only for single-batch scenarios`}
</CodeHeader>

### Branch Detection

<CodeHeader title="AUTOMATIC METADATA">
{`// Input enrollments:
"BTCS24O1001"  → Branch: CS
"0901CD231067" → Branch: CD (new format)

// Output in cache:
{
  "batches": {
    "Batch A": {
      "info": {
        "degree": "B.Tech",
        "branch": "CS",     // 🆕 Auto-detected
        "joining_year": "2024"
      }
    }
  }
}

// Used by:
// - Attendance sheet generation
// - Master plan PDF labeling
// - Analytics & reporting`}
</CodeHeader>

### Feedback System

<CodeHeader title="POST /api/feedback">
{`// Request
{
  "plan_id": "PLAN-ABC123",
  "feedback_type": "constraint_violation|seating_conflict|other",
  "message": "Students found adjacent with same batch",
  "severity": "high|medium|low"
}

// Response
{
  "success": true,
  "feedback_id": "FB-12345",
  "timestamp": "2026-02-23T14:30:00Z"
}`}
</CodeHeader>

### Template Management

<CodeHeader title="GET /api/templates">
{`// Response
{
  "templates": [
    {
      "name": "default",
      "description": "Standard seating plan",
      "format": "landscape"
    },
    {
      "name": "compact",
      "description": "Condensed layout",
      "format": "portrait"
    }
  ]
}`}
</CodeHeader>
