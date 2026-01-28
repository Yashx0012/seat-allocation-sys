---
sidebar_position: 2
---

import MagicBento from '@site/src/components/MagicBento';

# 🛠️ User Troubleshooting

Resolve common hurdles and system messages with this interactive guide. If you encounter an issue not listed here, please use the system feedback tool.

---

## 📂 Data & Intake
*Issues related to student rosters and file processing.*

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
  <MagicBento glowColor="59, 130, 246" enableStars={true}>
    <h4 style={{ color: '#3b82f6', marginBottom: '1rem' }}>❌ Unsupported Format</h4>
    <div style={{ fontSize: '0.9rem' }}>
      <p><b>Cause:</b> Attempting to upload non-standard extensions (.pdf, .txt).</p>
      <div style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '0.8rem', borderRadius: '8px', borderLeft: '3px solid #3b82f6' }}>
        <b>Solution:</b> Use <code>.csv</code> or <code>.xlsx</code>. We highly recommend <b>CSV (Comma Delimited)</b> for the fastest processing.
      </div>
    </div>
  </MagicBento>

  <MagicBento glowColor="236, 72, 153" enableStars={true}>
    <h4 style={{ color: '#ec4899', marginBottom: '1rem' }}>⚠️ Missing Columns</h4>
    <div style={{ fontSize: '0.9rem' }}>
      <p><b>Cause:</b> Missing "Roll No" or "Name" headers.</p>
      <div style={{ background: 'rgba(236, 72, 153, 0.1)', padding: '0.8rem', borderRadius: '8px', borderLeft: '3px solid #ec4899' }}>
        <b>Solution:</b> Ensure your file's first row contains clear headers. The engine is case-insensitive but requires these exact identifiers.
      </div>
    </div>
  </MagicBento>
</div>

---

## ⚙️ Engine & Logic
*Troubleshooting the allocation algorithm and constraints.*

<MagicBento glowColor="16, 185, 129" enableStars={true}>
  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', flexWrap: 'wrap' }}>
    <div>
      <h4 style={{ color: '#10b981' }}>🚨 Critical: Overfilled Room</h4>
      <p style={{ fontSize: '0.9rem' }}>This occurs when the student count exceeds the net capacity of your room layout (accounting for broken seats).</p>
      <ul style={{ fontSize: '0.85rem', opacity: 0.9 }}>
        <li>Reduce batch size per plan.</li>
        <li>Expand grid dimensions in <b>Room Setup</b>.</li>
        <li>Check for accidentally marked "Broken Seats".</li>
      </ul>
    </div>
    <div style={{ borderLeft: '1px solid rgba(16, 185, 129, 0.2)', paddingLeft: '2rem' }}>
      <h4 style={{ color: '#f59e0b' }}>⚖️ Sequence Gaps</h4>
      <p style={{ fontSize: '0.9rem' }}>Algorithms sometimes skip seats to preserve A/B paper set isolation or buffer zones.</p>
      <blockquote style={{ fontSize: '0.85rem', border: 'none', background: 'rgba(245, 158, 11, 0.05)', margin: 0, padding: '1rem', borderRadius: '8px' }}>
        <b>Note:</b> These are "Warnings", not errors. You can proceed with generation, but the sequence may not be perfectly contiguous.
      </blockquote>
    </div>
  </div>
</MagicBento>

---

## 🖥️ Interface & Access
*Display issues and session management.*

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
  <MagicBento glowColor="139, 92, 246">
    <h5 style={{ color: '#8b5cf6' }}>Distorted Grid</h5>
    <p style={{ fontSize: '0.85rem' }}>Reset zoom with <b>Ctrl + 0</b> or use <b>Fullscreen Mode</b>.</p>
  </MagicBento>
  
  <MagicBento glowColor="245, 158, 11">
    <h5 style={{ color: '#f59e0b' }}>Session Timeout</h5>
    <p style={{ fontSize: '0.85rem' }}>Security tokens expire every 24h. Simply <b>Relogin</b>; your plan is auto-saved.</p>
  </MagicBento>

  <MagicBento glowColor="239, 68, 68">
    <h5 style={{ color: '#ef4444' }}>Stale Data</h5>
    <p style={{ fontSize: '0.85rem' }}>Perform a <b>Hard Refresh (Ctrl + F5)</b> to clear local frontend cache.</p>
  </MagicBento>
</div>

---

:::tip Still Stuck?
Our technical support team is available for departmental escalations.
**Email:** support@allocation-sys.edu | **Extension:** 404
:::
