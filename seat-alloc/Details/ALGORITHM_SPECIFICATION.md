# Seat Allocation System - Algorithm Specification

This document details the core logic, constraints, and optimization strategies utilized by the Seat Allocation System's seating engine.

## 🧠 Core Algorithm Logic

The `SeatingAlgorithm` (located in `algo/core/algorithm/seating.py`) utilizes a **Column-Major Filling Strategy**. This ensures that batches are distributed vertically in columns, providing better visual separation than row-wise allocation.

### Allocation Phases
1. **Initialization**: Parse broken seats, batch limits, roll number templates, and variable block structures.
2. **Batch Distribution**: Assign classroom columns to batches based on student counts and column modulo logic.
3. **Seat Mapping**: Iterate through columns (top-to-bottom) to place students, respecting "broken" status.
4. **Paper Set Assignment**: Dynamically assign "A" or "B" paper sets using a multi-tier priority system.
5. **Constraint Validation**: Apply P1-P3 priority checks and optional adjacent seating controls.

### Block Structure Support 🆕
**New in v2.4**: Non-uniform column groupings for irregular classroom layouts:
- **Uniform Mode**: Default `block_width` parameter (e.g., 3 columns per block)
- **Variable Mode**: `block_structure` list (e.g., `[3, 2, 3]` for 8 columns with different widths)
- **Precedence**: Variable block structures take priority over uniform block_width
- **Use Cases**: 
  - Classroom seating zones with physical dividers
  - Accessibility row layouts (separate wider rows)
  - Flexible exam hall configurations

**Implementation**:
```python
# Variable blocks example
algo = SeatingAlgorithm(
    rows=10, cols=8,
    num_batches=2,
    block_structure=[3, 2, 3]  # Takes precedence over block_width
)

# Uniform blocks (legacy)
algo = SeatingAlgorithm(
    rows=10, cols=9,
    num_batches=3,
    block_width=3  # Used if block_structure is None
)
```

---

## 🛡️ Constraint & Priority System

The algorithm enforces **10+ primary constraints** during the generation process, with conditional application based on configuration.

### Paper Set Alternation (3-Tier Priority)
To ensure examination integrity, paper sets alternate based on the following priority list:

| Priority | Level | Logic |
| :--- | :--- | :--- |
| **P1** | **Highest** | **Vertical Batch Check**: If the student immediately above belongs to the *same batch*, they MUST receive the alternate paper set. |
| **P2** | **Medium** | **Horizontal Batch Check**: If the student to the left belongs to the *same batch*, they MUST receive the alternate paper set. |
| **P3** | **Lowest** | **Standard Alternation**: If no same-batch adjacency is detected, apply standard checkerboard alternation (A → B → A). |

### Adjacent Seating Control 🆕
**New in v2.4**: For single-batch scenarios, administrators can optionally enable adjacent seating:

**Feature Toggle**: `allow_adjacent_same_batch` parameter (boolean, default: `false`)

| Setting | Behavior | Use Case |
| :--- | :--- | :--- |
| `false` (Default) | Gap columns inserted between batches | Standard exam seating, prevents cheat collaboration |
| `true` | Same-batch students sit adjacent | Single-batch scenarios, minimizes empty seats |

**Key Characteristics**:
- Only applies when `num_batches == 1`
- Paper set alternation (P1-P3) remains enforced regardless
- Useful for specialized examination scenarios or single-major cohorts

**API Integration**:
```python
# Request payload
{
  "num_batches": 1,
  "batch_roll_numbers": {1: ["BTCS24O1001", ...]},
  "allow_adjacent_same_batch": true,  # Enable adjacent seating
  "rows": 10,
  "cols": 6
}
```

### Constraint Validation Summary
1. **Batch Count Validation**: Ensures batches don't exceed total columns
2. **Broken Seat Handling**: Excludes marked seats from allocation
3. **Student Count Matching**: Validates enrollment doesn't exceed capacity
4. **Paper Set P1-P3**: Enforced at all times for examination security
5. **Duplicate Prevention**: No student seated twice
6. **Adjacency Rules**: Applied based on `allow_adjacent_same_batch` flag
7. **Block Structure Integrity**: Validates structure sums equal total columns
8. **Roll Number Consistency**: Ensures all batches use compatible ID formats
9. **Grid Bounds**: Prevents seating outside room dimensions
10. **Batch Column Mapping**: Validates sufficient columns for all batches

---

## 📊 Batch & Student Management

### Column-Based Assignment
Batches are mapped to columns using a distribution formula:
- **Columns per Batch** = `(Total Columns // Total Batches)`
- **Remainders** are distributed to the first `N` batches.
- **Seat Order**: Column 0 (top-to-bottom) → Column 1 (top-to-bottom) → ...
- **Block Respect**: Variable block structures maintain boundaries during allocation

### Roll Number Formatting
The engine supports multiple modes for student IDs:

| Mode | Example | Format |
| :--- | :--- | :--- |
| **Numeric** | 1001, 1002, 1003 | Sequential integers with configurable start and width |
| **Templated** | BTCS2024O1001 | Prefix + year + separator + serial (pattern-based) |
| **Manual Enrollment** | From uploaded CSV | Direct mapping from student data (most accurate) |

**New Format Support** 🆕:
- **New Enrollment Format**: `0901CS231067` (Institution code + Branch + Year + Roll)
- **Legacy Format**: `BTCS241001` (Degree + Branch + Year + Roll)
- **Auto-Detection**: System intelligently detects and parses both formats

### Batch Branch Detection 🆕
**New in v2.4**: Intelligent majority-based branch identification:

```python
# Extraction Logic
def _determine_batch_branch(students, sample_size=5):
    """
    - Samples first N students (deterministic, no randomness)
    - Extracts branch code from enrollment number
    - Uses Counter() to find most common branch
    - Returns academic info of majority branch representative
    
    Result: {
        'degree': 'B.Tech',
        'branch': 'CS',
        'joining_year': '2024'
    }
    """
```

**Use Cases**:
- Attendance sheet generation (branch-specific metadata)
- Master plan PDF labeling (institutional reporting)
- Analytics and statistics (branch-wise distribution)

---

## 🛑 Error Handling & Validation

Every generated plan undergoes a final validation pass that checks for:
- **Duplicate Enrollments**: Ensures no student is seated twice
- **Batch Overflows**: Verifies allocation counts don't exceed uploaded totals
- **Configuration Mismatches**: Validates room dimensions match grid data
- **Block Structure Validity**: Sum of block widths equals total columns
- **Enrollment Format**: Detects and reports unsupported ID formats
- **Constraint Violations**: Reports P1-P3 failures or adjacency breaches
- **Seat Availability**: Confirms sufficient seats after broken seat deductions

**Validation Output**:
```json
{
  "status": "success",
  "validations": [
    {"constraint": "P1", "applied": true, "satisfied": true},
    {"constraint": "P2", "applied": true, "satisfied": true},
    {"constraint": "No Adjacent Same-Batch", "applied": false, "satisfied": true}
  ],
  "error_count": 0,
  "warnings": []
}
```

---
*Algorithm Specification: v2.4 | Last Updated: February 2026*
