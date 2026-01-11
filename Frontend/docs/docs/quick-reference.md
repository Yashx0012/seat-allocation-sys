---
sidebar_position: 5
---

# Quick Reference Guide

Fast developer integration and common workflows.

## 5-Minute Setup

### Backend Setup
```bash
cd algo
pip install Flask Flask-CORS
python app.py
# Running on http://localhost:5000
```

### Frontend Setup
```bash
cd Frontend
npm install
npm start
# Running on http://localhost:3000
```

## Simple API Call

### JavaScript/Fetch
```javascript
async function generateSeating() {
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
}
```

### React Hook
```javascript
const [seating, setSeating] = useState(null);

const handleGenerate = async (params) => {
  const response = await fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  const data = await response.json();
  setSeating(data);
};
```

### Vue.js
```javascript
async generateSeating(params) {
  const response = await fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  return response.json();
}
```

### Angular
```typescript
generateSeating(params: any): Observable<any> {
  return this.http.post('/api/generate-seating', params);
}
```

## Access Results

```javascript
const data = await generateSeating();

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

// Validation
data.validation.is_valid                // true/false
data.validation.errors                  // ["error1", "error2"]

// Constraints
data.constraints_status.constraints     // Array of constraint objects
```

## Input/Output Quick Reference

### Minimal Input (Required Only)
```json
{
  "rows": 8,
  "cols": 10,
  "num_batches": 3,
  "block_width": 2
}
```

### Full Input (All Options)
```json
{
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
  "enforce_no_adjacent_batches": false,
  "batch_roll_numbers": {
    "1": ["Student1", "Student2"],
    "2": ["Student3", "Student4"]
  }
}
```

### Output Response
```json
{
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
}
```

## Common Workflows

### Workflow 1: Basic Generation

```javascript
async function basicGeneration() {
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
}

### Workflow 1.5: Generate Attendance
```javascript
async function downloadAttendance(sessionId) {
  const response = await fetch(`/api/generate-attendance`, {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId })
  });
  // Handle blob download
}
```

### Workflow 1.6: Save Manual Changes
```javascript
async function saveManual(allocationData) {
   await fetch('/api/save-room-allocation', {
     method: 'POST',
     body: JSON.stringify(allocationData)
   });
}
```

### Workflow 2: With Student Limits

```javascript
async function generationWithLimits() {
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
}
```

### Workflow 3: With Broken Seats

```javascript
async function generationWithBrokenSeats() {
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
}
```

### Workflow 4: Custom Roll Numbers

```javascript
async function customRollNumbers() {
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
}
```

### Workflow 5: Complete Configuration

```javascript
async function completeConfiguration() {
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
    enforce_no_adjacent_batches: false
  };
  
  return fetch('/api/generate-seating', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  }).then(r => r.json());
}
```

## Component Examples

### React Grid Renderer

```javascript
function SeatingGrid({ seating }) {
  return (
    <div className="grid gap-1 p-4">
      {seating.map((row, rowIdx) => (
        <div key={rowIdx} className="flex gap-1">
          {row.map((seat, colIdx) => (
            <div
              key={`${rowIdx}-${colIdx}`}
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
}
```

### Vue Seating Component

```vue
<template>
  <div class="seating-grid">
    <div v-for="(row, rowIdx) in seating" :key="rowIdx" class="grid-row">
      <div
        v-for="(seat, colIdx) in row"
        :key="`${rowIdx}-${colIdx}`"
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
</script>
```

### Angular Component

```typescript
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-seating-grid',
  template: `
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
  `
})
export class SeatingGridComponent {
  @Input() seating: any[];
}
```

## Color Reference

### Default Batch Colors

```
Batch 1: #DBEAFE (Light Blue)    RGB(219, 234, 254)
Batch 2: #D1FAE5 (Light Green)   RGB(209, 250, 229)
Batch 3: #FEE2E2 (Light Red)     RGB(254, 226, 226)
Batch 4: #FEF3C7 (Light Yellow)  RGB(254, 243, 199)
Batch 5: #F3E8FF (Light Purple)  RGB(243, 232, 255)
```

### Special Statuses

```
Broken Seat:     Border #FF0000 (Red)
Unallocated:     Gray background
Empty:           White background
```

## Debugging Workflow

### Step 1: Verify Input

```javascript
// Check input format
console.log("Input:", params);
// Should have all required fields
// Values should be correct types
```

### Step 2: Make API Call

```javascript
// Log response
const response = await fetch('/api/generate-seating', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(params)
});

console.log("Status:", response.status);
const data = await response.json();
console.log("Response:", data);
```

### Step 3: Check Validation

```javascript
// Check if seating is valid
if (data.validation.is_valid) {
  console.log("✓ Seating is valid");
} else {
  console.error("✗ Validation errors:", data.validation.errors);
}
```

### Step 4: Inspect Constraints

```javascript
// Check constraint details
data.constraints_status.constraints.forEach(c => {
  console.log(`${c.name}: ${c.satisfied ? 'PASS' : 'FAIL'} (${c.priority})`);
});
```

### Step 5: Render and Verify

```javascript
// Render grid and visually verify
// Check for:
// - Correct number of batches
// - Proper roll number formatting
// - Correct colors
// - Broken seats marked properly
```

## Performance Benchmarks

### Response Times

| Grid Size | Time | Notes |
|---|---|---|
| 8×10 | < 10ms | Small classroom |
| 20×20 | < 20ms | Medium classroom |
| 50×50 | < 50ms | Large classroom |
| 100×100 | < 100ms | Extra large |

### Memory Usage

| Grid Size | Memory | Notes |
|---|---|---|
| 8×10 | < 1MB | Small |
| 20×20 | < 2MB | Medium |
| 50×50 | < 5MB | Large |
| 100×100 | < 15MB | Extra large |

## Error Handling

### Common Errors

| Error | Cause | Solution |
|---|---|---|
| 400 Bad Request | Invalid input format | Check JSON syntax |
| 422 Unprocessable | Constraint violation | Review error details |
| 500 Server Error | Backend exception | Check server logs |

### Error Response Example

```json
{
  "success": false,
  "error": "Invalid rows parameter",
  "details": {
    "field": "rows",
    "message": "Must be integer > 0"
  }
}
```

## File Structure Reference

```
seat-allocation-sys/
├── algo/
│   ├── app.py                 # Flask app
│   ├── algo.py               # Algorithm core
│   ├── auth_service.py        # Authentication
│   ├── requirements.txt       # Python dependencies
│   └── ...
├── Backend/
│   ├── database.py           # Database handler
│   └── auth_service.py       # Auth service
├── Frontend/
│   ├── src/
│   │   ├── App.jsx          # Main component
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable components
│   │   └── context/         # Context providers
│   └── package.json         # npm dependencies
└── docs/
    └── docs/               # Documentation
```

---

**Version**: 2.1  
**Last Updated**: January 2026
