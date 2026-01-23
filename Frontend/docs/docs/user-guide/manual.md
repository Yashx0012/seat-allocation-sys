---
sidebar_position: 1
---

import MagicBento from '@site/src/components/MagicBento';
import CodeHeader from '@site/src/components/filetypeheaderstyle';

# 📖 User Manual

Welcome to the **Seat Allocation System**. This guide will help you navigate the platform and generate professional seating arrangements for your examinations.

---

## 🚀 Quick Workflow

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
  <div style={{ padding: '1.5rem', borderRadius: '12px', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
    <h4 style={{ color: '#3b82f6', marginBottom: '0.5rem' }}>1. Initialize</h4>
    <p style={{ margin: 0, fontSize: '0.9rem' }}>Set room dimensions and basic constraints.</p>
  </div>
  <div style={{ padding: '1.5rem', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
    <h4 style={{ color: '#10b981', marginBottom: '0.5rem' }}>2. Upload</h4>
    <p style={{ margin: 0, fontSize: '0.9rem' }}>Import your student Excel/CSV rosters.</p>
  </div>
  <div style={{ padding: '1.5rem', borderRadius: '12px', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
    <h4 style={{ color: '#f59e0b', marginBottom: '0.5rem' }}>3. Generate</h4>
    <p style={{ margin: 0, fontSize: '0.9rem' }}>Run the algorithm and verify the layout.</p>
  </div>
  <div style={{ padding: '1.5rem', borderRadius: '12px', background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.2)' }}>
    <h4 style={{ color: '#8b5cf6', marginBottom: '0.5rem' }}>4. Export</h4>
    <p style={{ margin: 0, fontSize: '0.9rem' }}>Download official PDF seating charts.</p>
  </div>
</div>

---

## 🏠 Dashboard Overview

The **Admin Dashboard** is your command center. From here, you can manage multiple seating plans and track overall system status.

<MagicBento enableStars={true} glowColor="59, 130, 246">
  <h3>📊 Plan Management</h3>
  <p>Every examination session is saved as a <b>"Plan"</b>. You can create multiple plans for different rooms or exam dates, each preserving its own history and data isolation.</p>
</MagicBento>

---

## 📝 Step-by-Step Instructions

### 1. Creating a New Plan
1. Navigate to the **"New Plan"** section.
2. Enter a descriptive name (e.g., *Midterm Nov 2025*).
3. Specify the **Room Number** and select the predefined classroom template if available.

### 2. Uploading Rosters
The system matches students to seats using their **Roll Number** or **Enrollment ID**.
- Go to the **Upload** tab.
- Select your CSV or Excel file.
- **Tip**: Ensure your header names are clear (e.g., "Roll No", "Name", "Batch").

### 3. Configuring Constraints
Fine-tune how the algorithm behaves:
- **Block Width**: Controls how many seats are grouped together before a gap.
- **Paper Sets**: Enable **Sequence-Centric** mode to ensure A/B sets alternate strictly by roll number order.
- **Broken Seats**: Mark specific chairs as unusable to avoid allocations there.

### 4. Generation & Verification
Click the **Generate Seating** button. The system will:
1. Validate your constraints.
2. Run the allocation engine.
3. Show **Pragmatic Notifications** (Errors vs Warnings).

> [!TIP]
> **Warnings** indicate sequence gaps (e.g., 1 seat skipped), but still allow you to proceed with a valid (though not mathematically perfect) plan.

---

## 🖱️ Manual Adjustments

If the algorithm's result needs minor tweaks:
- **Drag & Drop**: Simply pick a student and move them to an empty seat.
- **Swap**: Drag one student onto another to swap their positions instantly.
- **Unallocate**: Remove a student from a seat if they are no longer attending.

---

## 📄 Official Documentation Export

Once satisfied, generate your final reports:
- **Seating Plan PDF**: A visual map for room entrances.
- **Attendance Sheet**: A structured list for signatures, sorted by roll number.

---

> [!IMPORTANT]
> Always verify the **Total Allocation Count** matches your provided roster before printing.
