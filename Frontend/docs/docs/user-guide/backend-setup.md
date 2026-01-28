---
sidebar_position: 2
---

import MagicBento from '@site/src/components/MagicBento';
import CodeHeader from '@site/src/components/filetypeheaderstyle';

# ⚙️ Backend Setup Guide

Initialize the **Seat Allocation System** backend—a high-performance **Flask** API designed for complex algorithm execution, secure data persistence, and professional reporting.

---

## 🏗️ Tech Stack
*The core technologies driving the allocation engine and API.*

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
  <MagicBento glowColor="16, 185, 129" enableStars={true}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
      <div style={{ background: '#10b981', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🐍</div>
      <h4 style={{ margin: 0, color: '#10b981' }}>Flask API</h4>
    </div>
    <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Modular micro-framework handling RESTful requests, session management, and core business logic.</p>
  </MagicBento>

  <MagicBento glowColor="245, 158, 11" enableStars={true}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
      <div style={{ background: '#f59e0b', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🔑</div>
      <h4 style={{ margin: 0, color: '#f59e0b' }}>JWT & OAuth</h4>
    </div>
    <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Secure authentication pipeline using JSON Web Tokens and Google OAuth for departmental access.</p>
  </MagicBento>

  <MagicBento glowColor="59, 130, 246" enableStars={true}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
      <div style={{ background: '#3b82f6', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🗄️</div>
      <h4 style={{ margin: 0, color: '#3b82f6' }}>SQLite Engine</h4>
    </div>
    <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Zero-config relational database for isolated plan storage and historical seating analytics.</p>
  </MagicBento>

  <MagicBento glowColor="236, 72, 153" enableStars={true}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
      <div style={{ background: '#ec4899', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>📊</div>
      <h4 style={{ margin: 0, color: '#ec4899' }}>Excel Logic</h4>
    </div>
    <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>High-speed processing of CSV and Excel rosters via optimized streaming and validation layers.</p>
  </MagicBento>
</div>

---

## 🛡️ Requirements
*System baseline for algorithm stability.*

<MagicBento glowColor="16, 185, 129" enableStars={false}>
  <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: '1rem' }}>
    <div style={{ textAlign: 'center' }}>
      <b style={{ color: '#10b981' }}>Python</b>
      <p style={{ margin: 0, fontSize: '0.9rem' }}>v3.8 or higher</p>
    </div>
    <div style={{ textAlign: 'center' }}>
      <b style={{ color: '#3b82f6' }}>Pip</b>
      <p style={{ margin: 0, fontSize: '0.9rem' }}>Latest version</p>
    </div>
    <div style={{ textAlign: 'center' }}>
      <b style={{ color: '#f59e0b' }}>Venv</b>
      <p style={{ margin: 0, fontSize: '0.9rem' }}>Highly Recommended</p>
    </div>
  </div>
</MagicBento>

---

## 📥 Installation Pipeline
*Initialize the Python environment and sync dependencies.*

### 1. Environment Isolation
Navigate to the algorithm core and create a sandboxed environment.

<CodeHeader title="POWERSHELL">
```powershell
cd algo
python -m venv venv
.\venv\Scripts\activate
```
</CodeHeader>

### 2. Dependency Sync
Retrieve all required modules including Flask, JWT, and Openpyxl.

<CodeHeader title="BASH">
```bash
pip install -r requirements.txt
```
</CodeHeader>

---

## 🚀 Server Operations

<div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
  <div style={{ flex: 1, minWidth: '300px' }}>
    <MagicBento glowColor="59, 130, 246">
      <h4 style={{ color: '#3b82f6' }}>⚡ Running Local Server</h4>
      <CodeHeader title="BASH">
      ```bash
      python app.py
      ```
      </CodeHeader>
      <p style={{ fontSize: '0.85rem', marginTop: '1rem' }}>The server will bind to <code>http://localhost:5000</code> and initialize <code>demo.db</code> automatically.</p>
    </MagicBento>
  </div>
  
  <div style={{ flex: 1, minWidth: '300px' }}>
    <MagicBento glowColor="139, 92, 246">
    <h4 style={{ color: '#8b5cf6' }}>⚙️ Configuration</h4>
    <ul style={{ fontSize: '0.85rem', paddingLeft: '1.2rem' }}>
      <li><b>FLASK_ENV</b>: <code>development</code> / <code>production</code></li>
      <li><b>FLASK_APP</b>: <code>app.py</code></li>
      <li><b>FLASK_SECRET_KEY</b>: Secure entropy for JWT.</li>
    </ul>
    </MagicBento>
  </div>
</div>

---

## 🏗️ Architectural Overview
*A modular breakdown of the backend filesystem.*

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
  <div style={{ padding: '1rem', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '12px' }}>
    <b style={{ color: '#10b981' }}>/api</b>
    <p style={{ margin: 0, fontSize: '0.8rem' }}>Flask Blueprints & Route handlers.</p>
  </div>
  <div style={{ padding: '1rem', border: '1px solid rgba(59, 130, 246, 0.2)', borderRadius: '12px' }}>
    <b style={{ color: '#3b82f6' }}>/core</b>
    <p style={{ margin: 0, fontSize: '0.8rem' }}>Seating Logic & Model definitions.</p>
  </div>
  <div style={{ padding: '1rem', border: '1px solid rgba(245, 158, 11, 0.2)', borderRadius: '12px' }}>
    <b style={{ color: '#f59e0b' }}>/database</b>
    <p style={{ margin: 0, fontSize: '0.8rem' }}>Query builders & schema management.</p>
  </div>
  <div style={{ padding: '1rem', border: '1px solid rgba(236, 72, 153, 0.2)', borderRadius: '12px' }}>
    <b style={{ color: '#ec4899' }}>/services</b>
    <p style={{ margin: 0, fontSize: '0.8rem' }}>Isolated Business Logic layers.</p>
  </div>
</div>

---

> [!TIP]
> **Deep Dive**: For a technical breakdown of the allocation engine, visit the **[Algorithm Core](../developers/Algorithm/index)** documentation.
