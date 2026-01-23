---
sidebar_position: 6
---

import CodeHeader from '@site/src/components/filetypeheaderstyle';

import ComplexityCards from '@site/src/components/complexitycards';

# 🔐 Authentication & Security

<ComplexityCards />

Comprehensive technical documentation for user authentication, Google OAuth integration, and security protocols.

---

## 📋 System Overview

The authentication system is built on a secure, modular architecture combining SQLite persistence with JWT-based session management. <span style={{ backgroundColor: '#f97316', color: 'white', padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem', verticalAlign: 'middle', marginLeft: '8px' }}>v2.3 UPDATE</span>

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
  <div style={{ padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #334155', backgroundColor: '#1e293b' }}>
    <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#f8fafc', marginBottom: '0.5rem' }}>Backend (Python/Flask)</h3>
    <ul style={{ margin: 0, paddingLeft: '1.2rem', color: '#94a3b8', fontSize: '0.9rem' }}>
      <li>SQLite Database Handler</li>
      <li>JWT Authentication Service</li>
      <li>Secure REST API Endpoints</li>
      <li>Bcrypt Password Hashing</li>
    </ul>
  </div>
  <div style={{ padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #334155', backgroundColor: '#1e293b' }}>
    <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#f8fafc', marginBottom: '0.5rem' }}>Frontend (React)</h3>
    <ul style={{ margin: 0, paddingLeft: '1.2rem', color: '#94a3b8', fontSize: '0.9rem' }}>
      <li>Authentication Context API</li>
      <li>Token & User Persistence</li>
      <li>Secure Login/Signup Flows</li>
      <li>Profile Management UI</li>
    </ul>
  </div>
</div>

## 🚀 Installation & Setup Guide

Follow this timeline to initialize the authentication infrastructure and launch the system.

<div style={{ position: 'relative' }}>
  <div style={{ position: 'absolute', left: '15px', top: '24px', bottom: '0', width: '1px', backgroundColor: '#334155' }}></div>

  {/* Step 1: Backend Setup */}
  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>1</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Backend Initialization</h3>
    <p style={{ color: '#94a3b8', marginBottom: '1rem' }}>Configure the Python environment and install core authentication dependencies.</p>
    <CodeHeader title="BASH">
{`# Navigate to backend directory
cd algo

# Install dependencies
pip install -r requirements.txt`}
    </CodeHeader>
  </div>

  {/* Step 2: Database Initialization */}
  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>2</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Server Ignition</h3>
    <p style={{ color: '#94a3b8', marginBottom: '1rem' }}>Launch the Flask server. Database initialization is handled automatically by the app factor functions.</p>
    <CodeHeader title="BASH">
{`# Run Flask server
cd algo
python app.py`}
    </CodeHeader>
    :::tip Expected Output
    The server should report: `* Running on http://localhost:5000`
    :::
  </div>

  {/* Step 3: Frontend Setup */}
  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '0' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>3</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Frontend Activation</h3>
    <p style={{ color: '#94a3b8', marginBottom: '1rem' }}>Launch the React development server to interact with the authentication UI.</p>
    <CodeHeader title="BASH">
{`# Navigate to frontend directory
cd Frontend

# Install node dependencies
npm install

# Start development server
npm start`}
    </CodeHeader>
  </div>
</div>

---

## 💾 Database Architecture

The system uses SQLite for lightweight, reliable persistence.

### User Repository (`users`)

<CodeHeader title="SQL">
{`CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT,
    role TEXT DEFAULT 'STUDENT' CHECK(role IN ('STUDENT', 'ADMIN', 'TEACHER')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
)`}
</CodeHeader>

| Attribute | Data Type | Description |
|:---|:---|:---|
| `id` | INTEGER | Primary key (auto-increment) |
| `username` | VARCHAR(80) | Unique username handler |
| `email` | VARCHAR(120) | Unique contact email address |
| `password` | VARCHAR(255) | Securely hashed password (Bcrypt) |
| `role` | VARCHAR(20) | Access level (STUDENT, ADMIN, FACULTY) |
| `created_at` | TIMESTAMP | Account registration timestamp |

### Session Management (`sessions`)

<CodeHeader title="SQL">
{`CREATE TABLE allocation_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT UNIQUE NOT NULL,
    user_id INTEGER DEFAULT 1,
    name TEXT,
    status TEXT CHECK(status IN ('active', 'completed', 'archived', 'draft', 'expired')) DEFAULT 'active',
    total_students INTEGER DEFAULT 0,
    allocated_count INTEGER DEFAULT 0,
    total_capacity INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
)`}
</CodeHeader>

| Attribute | Data Type | Description |
|:---|:---|:---|
| `id` | INTEGER | Session primary key |
| `user_id` | INTEGER | Foreign key reference to `users(id)` |
| `token` | VARCHAR(500) | Active JWT authentication token |
| `created_at` | TIMESTAMP | Session initiation timestamp |

### Session Architecture (v2.3 Refined)
The system now adheres to a **Strict Session Isolation** model where each seating plan preserves its own state history and cache snapshots, identified by a unique `plan_id`.

---

## 🔌 API Reference (Authentication)

### 1. User Registration

:::info Purpose
Registers a new system account. Default access level is `STUDENT`.
:::

<CodeHeader title="HTTP">
{`POST /api/auth/signup
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password_123",
  "role": "STUDENT"
}`}
</CodeHeader>

**Expected Response (201 Created):**
<CodeHeader title="JSON">
{`{
  "success": true,
  "message": "Account created successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "STUDENT",
    "created_at": "2024-01-15T10:30:00"
  }
}`}
</CodeHeader>

### 2. User Authentication

:::info Purpose
Validates credentials and issues a JWT session token.
:::

<CodeHeader title="HTTP">
{`POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password_123"
}`}
</CodeHeader>

**Expected Response (200 OK):**
<CodeHeader title="JSON">
{`{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "STUDENT"
  }
}`}
</CodeHeader>

### 3. Profile Management

:::warning Authorization Required
A valid `Bearer` token must be provided in the `Authorization` header.
:::

<CodeHeader title="HTTP">
{`GET /api/auth/profile
Authorization: Bearer <token>`}
</CodeHeader>

**Update Profile (PUT):**
<CodeHeader title="HTTP">
{`PUT /api/auth/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "role": "FACULTY"
}`}
</CodeHeader>

### 4. Session Termination

<CodeHeader title="HTTP">
{`POST /api/auth/logout
Authorization: Bearer <token>`}
</CodeHeader>

---

## 🔐 Google OAuth Integration

The system supports Google Sign-In for streamlined user onboarding.

### Workflow Orchestration
1.  **Identity Request**: User triggers "Sign in with Google".
2.  **Verification**: Google verifies user identity and issues an ID token.
3.  **Exchange**: Token is transmitted to the backend for final verification.
4.  **Provisioning**: Backend registers or authenticates the user and issues a system JWT.

:::tip Environmental Configuration
Add the following keys to your `.env` file to enable OAuth functionality:
:::

<CodeHeader title="ENV">
{`GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here`}
</CodeHeader>

---

## 💻 Frontend Implementation

### Authentication Guard

Protect your routes and components using the `useAuth` hook.

<CodeHeader title="JAVASCRIPT">
{`import { useAuth } from '../context/AuthContext';

function ProtectedDashboard() {
  const { user, isAuthenticated, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <Redirect to="/login" />;
  }
  
  return (
    <div>
      <h1>Welcome back, {user.username}!</h1>
      <button onClick={logout}>Sign Out</button>
    </div>
  );
}`}
</CodeHeader>

### Role-Based Access Control (RBAC)

| Role | Permissions | Primary Domain |
|:---|:---|:---|
| `STUDENT` | View current seating | Student Self-Service |
| `FACULTY` | Manage seating & generation | Academic Staff |
| `ADMIN` | Global configuration & audits | System Administrators |

---

## 🛡️ Security Protocols

:::caution Critical Security Notice
Ensure the following security standards are maintained at all times.
:::

### Data Integrity
- **Password Hashing**: All passwords are processed with a 10-round Bcrypt salt.
- **Transport Security**: HTTPS is mandatory for production environments.

### Session Security
- **JWT Expiration**: Tokens are issued with a restricted lifespan.
- **Client Storage**: Tokens are securely managed within the persistent browser state.

### Cross-Origin Security
The backend restricts API access to authorized frontend origins only.

<CodeHeader title="PYTHON">
{`# Centralized CORS Configuration in app.py
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})`}
</CodeHeader>

---

## 🔍 Troubleshooting & Support

| Incident | Probable Cause | Recommended Action |
|:---|:---|:---|
| `Flask module not found` | Environment mismatch | Execute `pip install Flask Flask-CORS` in your active venv. |
| `Database Locked` | Concurrent access | Close all active database connections and restart the server. |
| `401 Unauthorized` | Expired Session | Clear browser cache and perform a new login. |
| `CORS Error` | Origin mismatch | Verify that your frontend URL is correctly listed in the `origins` array. |

---

## 🚀 Production Deployment Checklist

- [ ] **Environment**: Switch `FLASK_ENV` to `production`.
- [ ] **Secrets**: Rotate the `JWT_SECRET` key to a high-entropy string.
- [ ] **Protocol**: Enable `HTTPS` for all infrastructure components.
- [ ] **Snapshots**: Configure automated daily database backups.
- [ ] **Observability**: Set up centralized logging for authentication events.

---

**Version**: 2.3  
**Last Updated**: January 24, 2026
