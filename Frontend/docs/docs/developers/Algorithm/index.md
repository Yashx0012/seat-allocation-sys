---
sidebar_position: 1
sidebar_label: 🧠 Overview
---

import MagicBento from '@site/src/components/MagicBento';

<style>{`
  [data-theme='light'] .bento-card {
    border: 1px solid #f97316 !important;
  }
`}</style>

# 🧠 Algorithm Deep Dive

Welcome to the technical specification of the Seat Allocation System. This portal serves as the primary gateway to the system's "brain"—a modular, constraint-based engine optimized for examination integrity and administrative efficiency.

---

## 🏗️ Architecture Overview

<h3 style={{ color: '#8b5cf6', marginTop: '1.5rem' }}>Constraint-Based Allocation Engine</h3>

<p style={{ fontSize: '1.1rem', lineHeight: '1.6', opacity: 0.9 }}>
  The system transforms raw administrative inputs—batch sizes, enrollment sequences, and room geometries—into an optimized seating matrix. By treating seating as a series of <b>spatial and relational constraints</b>, the algorithm ensures that isolation rules (A/B sets) are respected without sacrificing classroom utilization.
</p>

---

## 🧩 Technical Modules
*Explore the core components of the systemic seating logic.*

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
  
  <a href="./data-structures" style={{ textDecoration: 'none', color: 'inherit' }}>
    <MagicBento glowColor="236, 72, 153" className="bento-card">
      <h4 style={{ color: '#ec4899' }}>💾 Data Structures</h4>
      <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Definition of the <code>Seat</code>, <code>PaperSet</code>, and <code>Plan</code> models powering the engine state.</p>
    </MagicBento>
  </a>

  <a href="./distribution-logic" style={{ textDecoration: 'none', color: 'inherit' }}>
    <MagicBento glowColor="59, 130, 246" className="bento-card">
      <h4 style={{ color: '#3b82f6' }}>🏗️ Distribution Logic</h4>
      <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Deep dive into the <b>Column-Major</b> strategies and block-aware gap mechanisms.</p>
    </MagicBento>
  </a>

  <a href="./allocation-engine" style={{ textDecoration: 'none', color: 'inherit' }}>
    <MagicBento glowColor="16, 185, 129" className="bento-card">
      <h4 style={{ color: '#10b981' }}>⚙️ Allocation Engine</h4>
      <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>The 5-phase execution flow: From initialization and filtering to final state verification.</p>
    </MagicBento>
  </a>

  <a href="./paper-set-priority" style={{ textDecoration: 'none', color: 'inherit' }}>
    <MagicBento glowColor="245, 158, 11" className="bento-card">
      <h4 style={{ color: '#f59e0b' }}>⚖️ Paper Set Priority</h4>
      <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Analysis of the 3-tier priority system preserving the integrity of alternating sequences.</p>
    </MagicBento>
  </a>

  <a href="./validation-system" style={{ textDecoration: 'none', color: 'inherit' }}>
    <MagicBento glowColor="239, 68, 68" className="bento-card">
      <h4 style={{ color: '#ef4444' }}>🛡️ Validation System</h4>
      <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Automated sanity checking and the programmatic "Error vs Warning" reporting model.</p>
    </MagicBento>
  </a>

  <a href="../../user-guide/manual" style={{ textDecoration: 'none', color: 'inherit' }}>
    <MagicBento glowColor="139, 92, 246" className="bento-card">
      <h4 style={{ color: '#8b5cf6' }}>🧭 User Framework</h4>
      <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Need a high-level overview? Switch to the administrative <b>User Manual</b>.</p>
    </MagicBento>
  </a>

</div>

---

## 📊 Performance & Spec Identity

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', textAlign: 'center' }}>
  <div style={{ padding: '1rem', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '12px', background: 'rgba(245, 158, 11, 0.05)' }}>
    <small style={{ opacity: 0.6 }}>Logic Layer</small>
    <div style={{ color: '#f59e0b', fontWeight: 'bold' }}>Python v3.10</div>
  </div>
  <div style={{ padding: '1rem', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '12px', background: 'rgba(245, 158, 11, 0.05)' }}>
    <small style={{ opacity: 0.6 }}>Complexity</small>
    <div style={{ color: '#f59e0b', fontWeight: 'bold' }}>O(N) Linear</div>
  </div>
  <div style={{ padding: '1rem', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '12px', background: 'rgba(245, 158, 11, 0.05)' }}>
    <small style={{ opacity: 0.6 }}>Strategy</small>
    <div style={{ color: '#f59e0b', fontWeight: 'bold' }}>Col-Major</div>
  </div>
  <div style={{ padding: '1rem', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '12px', background: 'rgba(245, 158, 11, 0.05)' }}>
    <small style={{ opacity: 0.6 }}>Version</small>
    <div style={{ color: '#f59e0b', fontWeight: 'bold' }}>2.3 Stable</div>
  </div>
</div>

---

> [!NOTE]
> This documentation is a live technical specification. For pull requests or logic extensions, please follow the contributing guidelines in the core repository.
