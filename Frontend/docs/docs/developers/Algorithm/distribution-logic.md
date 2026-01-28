---
sidebar_label: 🏗️ Distribution Strategy
---
import MagicBento from '@site/src/components/MagicBento';
import CodeHeader from '@site/src/components/filetypeheaderstyle';

<style>{`
  [data-theme='light'] .bento-card {
    border: 1px solid #f97316 !important;
  }
`}</style>

# 🏗️ Distribution Strategy

The distribution strategy determines how batches are partitioned across the physical space. The Seat Allocation System uses a **Column-Major Filling Strategy** by default.

---

## 1. Column-Batch Mapping

Unlike simple sequential filling, the engine maps batches to specific columns. This provides superior visual separation for invigilators.

### The Formula
For a room with **C** columns and **B** batches:
1.  **Base Width** (W_base) = floor(C / B)
2.  **Remainders** (R) = C mod B
3.  Each batch is assigned a list of column indices.

In the standard `batch_by_column` mode, the assignment is derived dynamically:

<CodeHeader title="PYTHON">
{`batch_id = (col % num_batches) + 1`}
</CodeHeader>

---

## 2. Block-Aware Gaps

A unique feature of the algorithm is the **Block-Aware Isolation** used when `num_batches == 1`. 

When only one batch is being seated (e.g., a single-subject exam), the algorithm must still prevent horizontal copying. It achieves this by creating "Ghost Columns" within blocks.

### Logic Flow
Inside the allocation loop:
- If `num_batches == 1`:
    - Calculate `col_in_block = col % block_width`.
    - If `col_in_block % 2 != 0`: MARK AS GAP.
- **Result**: Every alternate column within a block remains empty or is marked as unallocated.

---

## 3. Vertically Aligned Filling

The engine fills the grid vertically:
1. Select Column **i**.
2. Iterate through Rows 0 to R_max.
3. Shift to Column **i+1**.

<MagicBento glowColor="59, 130, 246" enableStars={false} className="bento-card">
  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
    <div style={{ background: '#3b82f6', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>🏛️</div>
    <div>
      <h4 style={{ margin: 0, color: '#3b82f6' }}>Why Vertical?</h4>
      <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Physical classrooms are often arranged in columns. Vertical filling ensures that a batch "stays" in its lane, making attendance management significantly easier for faculty.</p>
    </div>
  </div>
</MagicBento>

---

## 4. Column Randomization

If the `randomize_column` flag is enabled:
1. The engine fetches all students intended for a specific column.
2. It performs a **Fisher-Yates Shuffle** on the subset.
3. It assigns them to the non-broken seats in that column.

<MagicBento glowColor="239, 68, 68" enableStars={false} className="bento-card">
  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
    <div style={{ background: '#ef4444', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>⚠️</div>
    <div>
      <h4 style={{ margin: 0, color: '#ef4444' }}>Randomization Limit</h4>
      <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Randomization happens <b>within</b> the assigned column only. This preserves the batch-by-column distribution while preventing students with adjacent roll numbers from sitting vertically next to each other.</p>
    </div>
  </div>
</MagicBento>
