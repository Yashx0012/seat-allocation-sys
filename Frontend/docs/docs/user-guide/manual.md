---
sidebar_position: 1
---

import MagicBento from '@site/src/components/MagicBento';
import CodeHeader from '@site/src/components/filetypeheaderstyle';

# 📖 User Manual

Welcome to the **Seat Allocation System**. Transform your examination management with our intelligent, automated seating engine. This guide provides everything you need to know to move from raw rosters to professional layouts.

---

## 🚀 Quick Workflow
*A high-level view of the standard process.*

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
  <MagicBento glowColor="59, 130, 246" enableStars={true}>
    <h4 style={{ color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <span style={{ fontSize: '1.2rem' }}>1️⃣</span> Initialize
    </h4>
    <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Define your room canvas and set the baseline constraints.</p>
  </MagicBento>

  <MagicBento glowColor="16, 185, 129" enableStars={true}>
    <h4 style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <span style={{ fontSize: '1.2rem' }}>2️⃣</span> Upload
    </h4>
    <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Sync student data via secure Excel or CSV imports.</p>
  </MagicBento>

  <MagicBento glowColor="245, 158, 11" enableStars={true}>
    <h4 style={{ color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <span style={{ fontSize: '1.2rem' }}>3️⃣</span> Generate
    </h4>
    <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Let the engine solve the allocation matrix instantly.</p>
  </MagicBento>

  <MagicBento glowColor="139, 92, 246" enableStars={true}>
    <h4 style={{ color: '#8b5cf6', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <span style={{ fontSize: '1.2rem' }}>4️⃣</span> Export
    </h4>
    <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Generate print-ready PDFs and attendance reports.</p>
  </MagicBento>
</div>

---

## 🏠 Core Management

<MagicBento enableStars={true} glowColor="139, 92, 246">
  <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', alignItems: 'center' }}>
    <div style={{ flex: 1, minWidth: '300px' }}>
      <h3 style={{ color: '#8b5cf6' }}>📊 Plan-Based Architecture</h3>
      <p>Every examination is treated as a <b>"Plan"</b>. This ensures total data isolation, version history, and specific room targeting. You can clone existing plans to save time on recurring examinations.</p>
    </div>
    <div style={{ borderLeft: '2px solid rgba(139, 92, 246, 0.3)', paddingLeft: '2rem' }}>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        <li>✅ Isolated Data Storage</li>
        <li>✅ Room-Specific Templates</li>
        <li>✅ Historical Analytics</li>
      </ul>
    </div>
  </div>
</MagicBento>

---

## 📝 Detailed Configuration
*Follow these steps to configure your seating arrangement with precision.*

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginTop: '1rem', marginBottom: '2rem' }}>
  
  <MagicBento glowColor="59, 130, 246" enableStars={false}>
    <h4 style={{ borderBottom: '1px solid rgba(59, 130, 246, 0.2)', paddingBottom: '0.5rem' }}>🏗️ Room Setup</h4>
    <ul style={{ fontSize: '0.9rem', paddingLeft: '1.2rem' }}>
      <li>Define <b>Rows & Columns</b>.</li>
      <li>Identify <b>Broken Seats</b> to exclude them.</li>
      <li>Specify <b>Block Widths</b> for logical grouping.</li>
    </ul>
  </MagicBento>

  <MagicBento glowColor="16, 185, 129" enableStars={false}>
    <h4 style={{ borderBottom: '1px solid rgba(16, 185, 129, 0.2)', paddingBottom: '0.5rem' }}>📂 Data Ingestion</h4>
    <ul style={{ fontSize: '0.9rem', paddingLeft: '1.2rem' }}>
      <li>Upload <b>CSV/Excel</b> rosters.</li>
      <li>Map headers like <b>"Roll No"</b> and <b>"Name"</b>.</li>
      <li>Validate data integrity before processing.</li>
    </ul>
  </MagicBento>

  <MagicBento glowColor="245, 158, 11" enableStars={false}>
    <h4 style={{ borderBottom: '1px solid rgba(245, 158, 11, 0.2)', paddingBottom: '0.5rem' }}>⚖️ Constraint Engine</h4>
    <ul style={{ fontSize: '0.9rem', paddingLeft: '1.2rem' }}>
      <li>Set <b>Paper Set Priorities</b> (A/B logic).</li>
      <li>Toggle <b>Sequence-Centric</b> mode.</li>
      <li>Add <b>Buffer Seats</b> between batches.</li>
    </ul>
  </MagicBento>

  <MagicBento glowColor="236, 72, 153" enableStars={false}>
    <h4 style={{ borderBottom: '1px solid rgba(236, 72, 153, 0.2)', paddingBottom: '0.5rem' }}>⚡ Generation</h4>
    <ul style={{ fontSize: '0.9rem', paddingLeft: '1.2rem' }}>
      <li>Run <b>Pragmatic Validation</b>.</li>
      <li>View real-time engine processing.</li>
      <li>Resolve detected sequence gaps.</li>
    </ul>
  </MagicBento>

</div>

<MagicBento glowColor="245, 158, 11" enableStars={true}>
  <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', padding: '0.5rem' }}>
    <div style={{ fontSize: '2.5rem', opacity: 0.9 }}>💡</div>
    <div>
      <h4 style={{ color: '#f59e0b', margin: '0 0 0.25rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        Pro-Tip
      </h4>
      <p style={{ margin: 0, fontSize: '0.95rem', opacity: 0.8, lineHeight: '1.5' }}>
        Use the <b>Broken Seats</b> feature to mirror the physical reality of your classroom, ensuring the algorithm never places a student on a damaged chair.
      </p>
    </div>
  </div>
</MagicBento>

---

## 🖱️ Interactive Management
*The dashboard isn't just for viewing—it's a fully interactive canvas.*

<div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
     <div style={{ textAlign: 'center', padding: '1rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)' }}>
        <b style={{ color: '#3b82f6' }}>Drag & Drop</b>
        <p style={{ margin: 0, fontSize: '0.8rem' }}>Move students between seats</p>
     </div>
     <div style={{ textAlign: 'center', padding: '1rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)' }}>
        <b style={{ color: '#10b981' }}>Instant Swap</b>
        <p style={{ margin: 0, fontSize: '0.8rem' }}>Switch two student positions</p>
     </div>
     <div style={{ textAlign: 'center', padding: '1rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)' }}>
        <b style={{ color: '#f59e0b' }}>Quick Unallocate</b>
        <p style={{ margin: 0, fontSize: '0.8rem' }}>Remove specific allocations</p>
     </div>
  </div>
</div>

---

## 📄 Reporting & Outputs
*Professional documentation is just one click away.*

| Report Type | Format | Content |
| :--- | :--- | :--- |
| **Seating Plan** | PDF / Image | Visual map for entrance doors. |
| **Attendance Sheet** | PDF / Excel | Roll-number sorted list for signatures. |
| **Statistics** | JSON / CSV | Breakdown of batches and room utilization. |

<MagicBento glowColor="239, 68, 68" enableStars={true} style={{ marginTop: '2rem' }}>
  <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', padding: '0.5rem' }}>
    <div style={{ fontSize: '2.5rem', opacity: 0.9 }}>🛡️</div>
    <div>
      <h4 style={{ color: '#ef4444', margin: '0 0 0.25rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        Important
      </h4>
      <p style={{ margin: 0, fontSize: '0.95rem', opacity: 0.8, lineHeight: '1.5' }}>
        Verify the <b>Total Allocation Count</b> against your original roster before finalizing the export. Discrepancies usually indicate unallocated students due to strict constraints.
      </p>
    </div>
  </div>
</MagicBento>

---

## 🧭 Developer Quick Links

<div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
  <a href="./frontend-setup" style={{ textDecoration: 'none', color: 'inherit' }}>
    <MagicBento glowColor="59, 130, 246">
      <h4>🖥️ Frontend Setup</h4>
      <p style={{ fontSize: '0.8rem', margin: 0 }}>React, Vite, Docusaurus integration guide.</p>
    </MagicBento>
  </a>
  <a href="./backend-setup" style={{ textDecoration: 'none', color: 'inherit' }}>
    <MagicBento glowColor="236, 72, 153">
      <h4>⚙️ Backend Setup</h4>
      <p style={{ fontSize: '0.8rem', margin: 0 }}>Python, Flask, SQLite configuration guide.</p>
    </MagicBento>
  </a>
</div>
