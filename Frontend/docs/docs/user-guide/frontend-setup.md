---
sidebar_position: 1
---

import MagicBento from '@site/src/components/MagicBento';
import CodeHeader from '@site/src/components/filetypeheaderstyle';

# 🖥️ Frontend Setup Guide

Deploy the visual engine of the **Seat Allocation System**. This guide ensures a smooth initialization of the React-based dashboard, optimized for high-performance animations and responsive interactions.

---

## 🏗️ Tech Stack
*The technological pillars powering the seat allocation ecosystem.*

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '3rem' }}>
  <MagicBento glowColor="59, 130, 246" enableStars={true}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
      <div style={{ background: '#3b82f6', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>⚛️</div>
      <h4 style={{ margin: 0, color: '#3b82f6' }}>React 19 & Router 7</h4>
    </div>
    <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Latest concurrent rendering features with robust, typesafe routing for complex dashboard navigation.</p>
  </MagicBento>

  <MagicBento glowColor="6, 182, 212" enableStars={true}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
      <div style={{ background: '#06b6d4', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🎨</div>
      <h4 style={{ margin: 0, color: '#06b6d4' }}>Tailwind & Styled</h4>
    </div>
    <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Hybrid styling approach using Tailwind's utility-first speed and Styled Components' scoped flexibility.</p>
  </MagicBento>

  <MagicBento glowColor="236, 72, 153" enableStars={true}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
      <div style={{ background: '#ec4899', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🖱️</div>
      <h4 style={{ margin: 0, color: '#ec4899' }}>GSAP & Framer</h4>
    </div>
    <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>High-performance timeline animations (GSAP) paired with fluid micro-interactions (Framer Motion).</p>
  </MagicBento>

  <MagicBento glowColor="139, 92, 246" enableStars={true}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
      <div style={{ background: '#8b5cf6', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🛰️</div>
      <h4 style={{ margin: 0, color: '#8b5cf6' }}>Axios & Lucide</h4>
    </div>
    <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.8 }}>Optimized API communications and professional, lightweight SVG iconography across the stack.</p>
  </MagicBento>
</div>

---

## 🛡️ Prerequisites
*System requirements for a stable development environment.*

<MagicBento glowColor="139, 92, 246" enableStars={false}>
  <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: '1rem' }}>
    <div style={{ textAlign: 'center' }}>
      <b style={{ color: '#8b5cf6' }}>Node.js</b>
      <p style={{ margin: 0, fontSize: '0.9rem' }}>v18.0 or higher</p>
    </div>
    <div style={{ textAlign: 'center' }}>
      <b style={{ color: '#10b981' }}>NPM</b>
      <p style={{ margin: 0, fontSize: '0.9rem' }}>v9.0 or higher</p>
    </div>
    <div style={{ textAlign: 'center' }}>
      <b style={{ color: '#3b82f6' }}>OS</b>
      <p style={{ margin: 0, fontSize: '0.9rem' }}>Win / Mac / Linux</p>
    </div>
  </div>
</MagicBento>

---

## 📥 Installation Workflow
*Follow these systematic steps to initialize the project.*

### 1. Dependency Acquisition
Navigate to the root and install the package ecosystem.

<CodeHeader title="POWERSHELL">
{`cd Frontend
npm install`}
</CodeHeader>

> [!TIP]
> This stage automatically configures **Framer Motion**, **GSAP**, and **Styled Components** for high-end UI layout and animations.

### 2. Environment Configuration
Establish the connection between the frontend and the allocation engine.

<CodeHeader title="POWERSHELL">
{`copy .env.example .env`}
</CodeHeader>

<div style={{ marginTop: '1.5rem' }}>
  <MagicBento glowColor="245, 158, 11" enableStars={false}>
    <p style={{ margin: 0, fontSize: '0.9rem' }}><b>API Linkage:</b> By default, the frontend proxies all <code>/api</code> requests to <code>http://127.0.0.1:5000</code>. Only update <code>REACT_APP_API_BASE_URL</code> for non-local production deployments.</p>
  </MagicBento>
</div>

---

## 🚀 Deployment & Operations

<div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
  <MagicBento glowColor="16, 185, 129">
    <h4 style={{ color: '#10b981' }}>⚡ Development Mode</h4>
    <p style={{ fontSize: '0.85rem' }}>Start the local server with hot-reloading.</p>
    <CodeHeader title="BASH">
    {`npm start`}
    </CodeHeader>
  </MagicBento>

  <MagicBento glowColor="59, 130, 246">
    <h4 style={{ color: '#3b82f6' }}>🏗️ Production Build</h4>
    <p style={{ fontSize: '0.85rem' }}>Create an optimized static bundle.</p>
    <CodeHeader title="BASH">
    {`npm run build`}
    </CodeHeader>
  </MagicBento>
</div>

---

:::info Need help with the Backend?
Continue to the **[⚙️ Backend Setup](./backend-setup)** to initialize the Flask API and SQLite database.
:::
