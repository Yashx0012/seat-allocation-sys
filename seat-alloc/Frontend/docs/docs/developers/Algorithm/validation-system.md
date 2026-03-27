---
sidebar_label: 🛡️ Validation System
---
import MagicBento from '@site/src/components/MagicBento';
import CodeHeader from '@site/src/components/filetypeheaderstyle';

<style>{`
  [data-theme='light'] .bento-card {
    border: 1px solid #f97316 !important;
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.1) !important;
  }
`}</style>

# 🛡️ Validation System

Post-allocation, the system runs a comprehensive validation suite to ensure that no "logical leak" occurred during the complex filling process.

---

## 1. Dual-Tier Reporting

The algorithm distinguishes between **Critical Errors** and **Integrity Warnings**.

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
  <MagicBento glowColor="239, 68, 68" enableStars={false} className="bento-card">
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1.2rem' }}>
      <div style={{ background: '#ef4444', width: '45px', height: '45px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', flexShrink: 0, boxShadow: '0 4px 12px rgba(239, 68, 68, 0.3)' }}>🛑</div>
      <div style={{ flex: 1 }}>
        <h4 style={{ margin: '0 0 0.5rem 0', color: '#ef4444' }}>Critical Errors</h4>
        <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.85rem', opacity: 0.8 }}>
          <li><b>Duplicate Enrollments</b>: Student ID assigned to two seats.</li>
          <li><b>Physical Collision</b>: Same batch & set sitting next to each other.</li>
          <li><b>Batch Overflow</b>: More students allocated than available.</li>
        </ul>
      </div>
    </div>
  </MagicBento>

  <MagicBento glowColor="245, 158, 11" enableStars={false} className="bento-card">
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1.2rem' }}>
      <div style={{ background: '#f59e0b', width: '45px', height: '45px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', flexShrink: 0, boxShadow: '0 4px 12px rgba(245, 158, 11, 0.3)' }}>⚠️</div>
      <div style={{ flex: 1 }}>
        <h4 style={{ margin: '0 0 0.5rem 0', color: '#f59e0b' }}>Integrity Warnings</h4>
        <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.85rem', opacity: 0.8 }}>
          <li><b>Sequence Gaps</b>: Same paper sets for students separated by gaps.</li>
          <li><b>Numeric Fallback</b>: Serial numbers used instead of enrollment data.</li>
        </ul>
      </div>
    </div>
  </MagicBento>
</div>

---

## 2. Automated Validation Suite

The `validate_constraints` method performs the following passes:

<MagicBento glowColor="59, 130, 246" enableStars={false} className="bento-card">
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
    <div>
      <h4 style={{ color: '#3b82f6', marginBottom: '0.5rem' }}>Vertical Adjacency</h4>
      <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Tracks state per batch label in each column to prevent same-set vertical neighbors.</p>
    </div>
    <div>
      <h4 style={{ color: '#3b82f6', marginBottom: '0.5rem' }}>Horizontal Adjacency</h4>
      <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Checks rows and verifies <b>Batch Isolation</b> within physical blocks.</p>
    </div>
    <div>
      <h4 style={{ color: '#3b82f6', marginBottom: '0.5rem' }}>Data Cross-Check</h4>
      <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Matches final count against roll pools to ensure 100% data coverage.</p>
    </div>
  </div>
</MagicBento>

---

## 3. The Validation Response

The final JSON returned to the user includes a structured validation object:

<CodeHeader title="JSON">
{`{
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  }
}`}
</CodeHeader>

A plan with only warnings will return `is_valid: true`, allowing the user to proceed to PDF export while being informed of minor sequence gaps.

---

<MagicBento glowColor="239, 68, 68" enableStars={false} className="bento-card">
  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
    <div style={{ background: '#ef4444', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>💥</div>
    <div>
      <h4 style={{ margin: 0, color: '#ef4444' }}>Important Caution</h4>
      <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Always review <b>Integrity Warnings</b> when seating large combined batches, as they might indicate that the room geometry is making perfect alternation mathematically difficult.</p>
    </div>
  </div>
</MagicBento>
