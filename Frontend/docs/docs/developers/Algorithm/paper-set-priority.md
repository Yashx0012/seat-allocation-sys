---
sidebar_label: ⚖️ Paper Set Priority
---
import MagicBento from '@site/src/components/MagicBento';
import CodeHeader from '@site/src/components/filetypeheaderstyle';

<style>{`
  [data-theme='light'] .bento-card {
    border: 1px solid #f97316 !important;
  }
`}</style>

# ⚖️ Paper Set Priority

The paper set assignment logic is the most critical part of examination integrity. The algorithm uses a **3-Tier Priority System** to determine if a student receives Set A or Set B.

<MagicBento glowColor="16, 185, 129" enableStars={false} className="bento-card">
  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
    <div style={{ background: '#10b981', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>🛡️</div>
    <div>
      <h4 style={{ margin: 0, color: '#10b981' }}>The Integrity Goal</h4>
      <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Students of the <b>same batch</b> sitting physically close must have <b>different paper sets</b>. Adjacency between different batches is less critical but still avoided when possible.</p>
    </div>
  </div>
</MagicBento>

---

## 3-Tier Priority Matrix

| Priority | Strategy | Logic |
| :--- | :--- | :--- |
| **P1** | **Vertical Batch Check** | If the nearest student above in the same column belongs to the **same batch label**, apply the alternate set. |
| **P2** | **Horizontal Batch Check** | If the nearest student to the left in the same row belongs to the **same batch label**, apply the alternate set. |
| **P3** | **Checkerboard Fallback** | If no same-batch adjacency is detected, default to a standard pattern: `Set A` if `row % 2 == 0`, else `Set B`. |

---

## Conflict Resolution

What happens if P1 suggests "Set A" but P2 suggests "Set B"?

<MagicBento glowColor="245, 158, 11" enableStars={false} className="bento-card">
  <p style={{ margin: 0, fontSize: '0.95rem' }}>The engine favors the <b>Horizontal (Row) integrity</b> if the neighbor is physically close (distance <code>&lt;= 2</code>). This prevents the "Clean Row" issue where students in the same row might end up with similar patterns.</p>
</MagicBento>

<CodeHeader title="PYTHON">
{`if v_pref and h_pref:
    if v_pref == h_pref:
        return v_pref
    # Favor horizontal to prevent "same sets in row" issue
    return h_pref if h_dist <= 2 else v_pref`}
</CodeHeader>

---

## Why Labels Matter?

<MagicBento glowColor="139, 92, 246" enableStars={false} className="bento-card">
  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
    <div style={{ background: '#8b5cf6', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>🏷️</div>
    <div>
      <h4 style={{ margin: 0, color: '#8b5cf6' }}>Group-based Integrity</h4>
      <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>The algorithm uses <code>batch_labels</code> instead of <code>batch_ids</code>. If an admin labels Batch 1 (CSE) and Batch 2 (CS-Design) both as "Computer Science", the engine treats them as the <b>same group</b> for set alternation.</p>
    </div>
  </div>
</MagicBento>

---

### Logic Illustration

In a 2D Block:
- **Student 1 (A1)**: Batch CSE &rarr; **Set A** (Checkerboard)
- **Student 2 (A2)**: Batch CSE &rarr; **Set B** (P1: Vertical Same-Batch)
- **Student 3 (B1)**: Batch CSE &rarr; **Set B** (P2: Horizontal Same-Batch)
- **Student 4 (B2)**: Batch CSE &rarr; **Set A** (Conflicts resolved by P1/P2)
