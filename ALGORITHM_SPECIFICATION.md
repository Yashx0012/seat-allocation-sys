# Seat Allocation System - Algorithm Specification

This document details the core logic, constraints, and optimization strategies utilized by the Seat Allocation System's seating engine.

## 🧠 Core Algorithm Logic

The `SeatingAlgorithm` (located in `algo/core/algorithm/seating.py`) utilizes a **Column-Major Filling Strategy**. This ensures that batches are distributed vertically in columns, providing better visual separation than row-wise allocation.

### Allocation Phases
1. **Initialization**: Parse broken seats, batch limits, and roll number templates.
2. **Batch Distribution**: Assign classroom columns to batches based on student counts and column modulo logic.
3. **Seat Mapping**: Iterate through columns (top-to-bottom) to place students, respecting "broken" status.
4. **Paper Set Assignment**: Dynamically assign "A" or "B" paper sets using a multi-tier priority system.

---

## 🛡️ Constraint & Priority System

The algorithm enforces **8 primary constraints** during the generation process.

### Paper Set Alternation (3-Tier Priority)
To ensure examination integrity, paper sets alternate based on the following priority list:

| Priority | Level | Logic |
| :--- | :--- | :--- |
| **P1** | **Highest** | **Vertical Batch Check**: If the student immediately above belongs to the *same batch*, they MUST receive the alternate paper set. |
| **P2** | **Medium** | **Horizontal Batch Check**: If the student to the left belongs to the *same batch*, they MUST receive the alternate paper set. |
| **P3** | **Lowest** | **Standard Alternation**: If no same-batch adjacency is detected, apply standard checkerboard alternation (A → B → A). |

---

## 📊 Batch & Student Management

### Column-Based Assignment
Batches are mapped to columns using a distribution formula:
- **Columns per Batch** = `(Total Columns // Total Batches)`
- **Remainders** are distributed to the first `N` batches.
- **Seat Order**: Column 0 (top-to-bottom) → Column 1 (top-to-bottom) → ...

### Roll Number Formatting
The engine supports three modes for student IDs:
1. **Simple Numeric**: Sequential integers.
2. **Templated**: e.g., `{prefix}{year}O{serial}` (BTCS2024O1001).
3. **Manual Roll List**: Direct mapping from uploaded student enrollment data.

---

## 🛑 Error Handling & Validation

Every generated plan undergoes a final validation pass that checks for:
- **Duplicate Enrollments**: Ensures no student is seated twice.
- **Batch Overflows**: Verifies that allocation counts do not exceed uploaded student totals.
- **Configuration Mismatches**: Validates that room dimensions (rows/cols) match the provided grid data.

---
*Algorithm Specification: v2.3*
