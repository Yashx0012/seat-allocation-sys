---
sidebar_position: 6
---

# Authentication Setup Guide

Complete guide for user authentication and database integration.

## Overview

Your seat allocation system includes full authentication with a SQLite database backend, JWT tokens, and bcrypt password hashing.

## What's Been Implemented

### Backend (Python/Flask)

#### 1. **Backend/database.py** - SQLite Database Handler
- Creates and manages users and sessions tables
- Handles database connections
- Manages schema initialization

#### 2. **Backend/auth_service.py** - Authentication Service
- Password hashing with bcrypt
- JWT token generation and verification
- User management (signup, login, profile)
- Session handling

#### 3. **algo/app.py** - Updated Flask Application
- REST API endpoints with authentication
- CORS configuration
- Error handling
- Session management

### Frontend (React)

#### 1. **Frontend/src/context/AuthContext.jsx** - Authentication Context
- Real API calls to backend
- Token storage in localStorage
- User data persistence
- Profile update methods
- Login/logout functionality

#### 2. **Frontend/src/pages/LoginPage.jsx** - Login Page
- Form validation
- Real backend authentication
- Error handling
- Redirect on success

#### 3. **Frontend/src/pages/ProfilePage.jsx** - Profile Page
- Display user information
- Edit profile functionality
- Real-time data updates
- Password management

#### 4. **Frontend/src/pages/SignupPage.jsx** - Signup Page
- Account creation form
- Input validation
- Role assignment (STUDENT, ADMIN, FACULTY)
- Error feedback

## Installation & Running

### Backend Setup

```bash
# Navigate to backend directory
cd algo

# Install dependencies
pip install -r requirements.txt

# Initialize database (if needed)
cd ../Backend
python database.py

# Go back to algo directory
cd ../algo

# Run Flask server
python app.py
```

**Expected Output:**
```
 * Running on http://localhost:5000
 * Press CTRL+C to quit
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd Frontend

# Install dependencies
npm install

# Start development server
npm start
```

**Expected Output:**
```
Compiled successfully!
You can now view your app in the browser.
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'STUDENT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key (auto-increment) |
| `username` | VARCHAR(80) | Unique username |
| `email` | VARCHAR(120) | Unique email address |
| `password` | VARCHAR(255) | Hashed password (bcrypt) |
| `role` | VARCHAR(20) | User role (STUDENT, ADMIN, FACULTY) |
| `created_at` | TIMESTAMP | Account creation timestamp |

### Sessions Table

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key (auto-increment) |
| `user_id` | INTEGER | Foreign key to users table |
| `token` | VARCHAR(500) | JWT authentication token |
| `created_at` | TIMESTAMP | Token creation timestamp |

## API Endpoints

### Authentication Endpoints

#### 1. **Signup** - Create New Account

```http
POST /api/auth/signup
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password_123",
  "role": "STUDENT"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Account created successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "STUDENT",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Username already exists"
}
```

#### 2. **Login** - Authenticate User

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password_123"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "STUDENT"
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

#### 3. **Get Profile** - Retrieve Current User (Protected)

```http
GET /api/auth/profile
Authorization: Bearer <token>
```

**Success Response (200):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "STUDENT",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

#### 4. **Update Profile** - Modify User Info (Protected)

```http
PUT /api/auth/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "role": "FACULTY"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "newemail@example.com",
    "role": "FACULTY"
  }
}
```

#### 5. **Logout** - End Session (Protected)

```http
POST /api/auth/logout
Authorization: Bearer <token>
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```


## Google OAuth Integration

The system supports Google Sign-In for easier access.

### 1. Setup
- Backend uses `google_auth_handler`
- Frontend uses `GoogleLoginComponent.jsx`

### 2. Flow
1. User clicks "Sign in with Google"
2. Google popup handles authentication
3. Token sent to `/api/auth/google`
4. Backend verifies token with Google
5. If valid email:
   - Registers user (if new)
   - Logs in user (if exists)
   - Returns standard JWT token

### 3. Configuration
Add to `.env`:
```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

## Frontend Implementation

### Authentication Context Usage

```javascript
// In your React component
import { useAuth } from '../context/AuthContext';

function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }
  
  return (
    <div>
      <h1>Welcome, {user.username}!</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Login Flow

```javascript
const handleLogin = async (username, password) => {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Token is stored by AuthContext
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      // Redirect to dashboard
    } else {
      console.error(data.error);
    }
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```

### Protected API Calls

```javascript
const makeAuthenticatedRequest = async (endpoint, method = 'GET', body = null) => {
  const token = localStorage.getItem('token');
  
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  };
  
  if (body) {
    options.body = JSON.stringify(body);
  }
  
  const response = await fetch(endpoint, options);
  return response.json();
};

// Usage
const profile = await makeAuthenticatedRequest('/api/auth/profile');
```

## User Roles

### Supported Roles

| Role | Permissions | Use Case |
|---|---|---|
| **STUDENT** | View seating, generate for self | Student accessing their seating |
| **FACULTY** | Generate and manage seating | Faculty managing examinations |
| **ADMIN** | Full system access | System administrator |

### Role-Based Access Control

```javascript
// Check user role in component
function AdminPanel() {
  const { user } = useAuth();
  
  if (user.role !== 'ADMIN') {
    return <div>Access Denied</div>;
  }
  
  return <div>Admin Panel Content</div>;
}
```

## Security Considerations

### Password Security
- Passwords hashed with bcrypt (10 salt rounds)
- Passwords never stored in plaintext
- Never transmitted over unencrypted connections

### Token Security
- JWT tokens have expiration time
- Tokens stored in localStorage (client-side)
- Tokens sent in Authorization header
- HTTPS recommended for production

### CORS Configuration
```python
# In Flask app
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Environment Variables

Create `.env` file in `algo` directory:
```
FLASK_ENV=development
JWT_SECRET=your_secret_key_here
DATABASE_URL=sqlite:///user_auth.db
```

## Common Tasks

### Creating User Accounts Programmatically

```python
# In Python backend
from auth_service import signup

user = signup(
    username="alice",
    email="alice@example.com",
    password="secure_pass",
    role="FACULTY"
)
```

### Verifying Tokens

```python
from auth_service import verify_token

user_id = verify_token(token)
if user_id:
    # Token is valid
else:
    # Token is invalid or expired
```

### Changing User Password

```javascript
// Frontend
const changePassword = async (oldPassword, newPassword) => {
  const response = await fetch('/api/auth/change-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({ oldPassword, newPassword })
  });
  return response.json();
};
```

## Troubleshooting

### Issue: "No module named 'flask'"

**Solution:**
```bash
pip install Flask Flask-CORS
```

### Issue: "Database locked" Error

**Solution:**
```bash
# Close all connections and reinitialize
rm user_auth.db
python Backend/database.py
```

### Issue: Token Invalid/Expired

**Solution:**
- User needs to log in again
- Frontend should redirect to login page
- Token should be refreshed automatically

### Issue: CORS Error

**Solution:**
- Ensure CORS is enabled in Flask app
- Check frontend URL matches CORS origins
- Verify headers are correct

## Testing Authentication

### Manual Testing with cURL

```bash
# Signup
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "role": "STUDENT"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# Get Profile (replace TOKEN with actual token)
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer TOKEN"
```

### Frontend Testing

```javascript
// Test signup
async function testSignup() {
  const response = await fetch('/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123',
      role: 'STUDENT'
    })
  });
  console.log(await response.json());
}

// Test login
async function testLogin() {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'testuser',
      password: 'password123'
    })
  });
  const data = await response.json();
  console.log('Token:', data.token);
}
```

## Production Deployment

### Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use strong JWT secret key
- [ ] Enable HTTPS only
- [ ] Set secure cookie flags
- [ ] Configure proper CORS origins
- [ ] Implement rate limiting
- [ ] Set up database backups
- [ ] Enable logging and monitoring
- [ ] Use environment variables for secrets
- [ ] Test all authentication flows

### Example Production Config

```python
# config.py
import os

class Config:
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    JWT_SECRET = os.environ.get('JWT_SECRET')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///user_auth.db')
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

---

**Version**: 2.1  
**Last Updated**: January 2026
