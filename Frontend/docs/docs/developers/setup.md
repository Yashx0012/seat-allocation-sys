---
sidebar_position: 2
---

import CodeHeader from '@site/src/components/filetypeheaderstyle';


import ComplexityCards from '@site/src/components/complexitycards';

# 🛠️ Developer Setup

<ComplexityCards />

Comprehensive technical guide to setting up the Seat Allocation System development environment.

## Prerequisites

<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
  <div style={{ padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #334155', display: 'flex', flexDirection: 'column', gap: '1rem', transition: 'border-color 0.2s', backgroundColor: '#1e293b' }} className="hover:border-orange-500">
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
      <div style={{ width: '3rem', height: '3rem', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#334155', borderRadius: '0.5rem' }}>
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" class="text-white"><path d="M12 2L2 7l10 5 10-5-10-5zm0 9l2.5-1.25L12 8.5l-2.5 1.25L12 11zm0 2.5l-5-2.5-5 2.5L12 22l10-8.5-5-2.5-5 2.5z" fill="#84cc16"/></svg>
      </div>
      <div>
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: '#f8fafc' }}>Node.js</h3>
        <p style={{ margin: 0, fontSize: '0.875rem', color: '#94a3b8' }}>v16 or higher</p>
      </div>
    </div>
    <a href="https://nodejs.org/" style={{ fontSize: '0.875rem', color: '#f97316', fontWeight: 500, textDecoration: 'none' }}>Download Node.js →</a>
  </div>

  <div style={{ padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #334155', display: 'flex', flexDirection: 'column', gap: '1rem', transition: 'border-color 0.2s', backgroundColor: '#1e293b' }} className="hover:border-orange-500">
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
      <div style={{ width: '3rem', height: '3rem', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#334155', borderRadius: '0.5rem' }}>
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none"><path d="M14.25 15.75h-.75a.75.75 0 0 1-.75-.75v-3.75a1.5 1.5 0 0 0-1.5-1.5h-.75a.75.75 0 0 0-.75.75v.75a2.25 2.25 0 0 1-2.25 2.25h-1.5A2.25 2.25 0 0 1 3.75 11.25v-1.5a9 9 0 0 1 18 0v1.5a2.25 2.25 0 0 1-2.25 2.25h-1.5a2.25 2.25 0 0 1-2.25-2.25v-.75a.75.75 0 0 0-.75-.75h-.75a.75.75 0 0 0-.75.75v3.75c0 .414-.336.75-.75.75z" fill="#3b82f6"/></svg>
      </div>
      <div>
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: '#f8fafc' }}>Python</h3>
        <p style={{ margin: 0, fontSize: '0.875rem', color: '#94a3b8' }}>v3.8 or higher</p>
      </div>
    </div>
    <a href="https://www.python.org/" style={{ fontSize: '0.875rem', color: '#f97316', fontWeight: 500, textDecoration: 'none' }}>Download Python →</a>
  </div>

  <div style={{ padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #334155', display: 'flex', flexDirection: 'column', gap: '1rem', transition: 'border-color 0.2s', backgroundColor: '#1e293b' }} className="hover:border-orange-500">
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
      <div style={{ width: '3rem', height: '3rem', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#334155', borderRadius: '0.5rem' }}>
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none"><path d="M12 2L2 7l10 5 10-5-10-5zm0 9l2.5-1.25L12 8.5l-2.5 1.25L12 11zm0 2.5l-5-2.5-5 2.5L12 22l10-8.5-5-2.5-5 2.5z" fill="#f97316"/></svg>
      </div>
      <div>
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: '#f8fafc' }}>Git</h3>
        <p style={{ margin: 0, fontSize: '0.875rem', color: '#94a3b8' }}>Version Control</p>
      </div>
    </div>
    <a href="https://git-scm.com/" style={{ fontSize: '0.875rem', color: '#f97316', fontWeight: 500, textDecoration: 'none' }}>Download Git →</a>
  </div>
</div>

## Installation Guide

<div style={{ position: 'relative' }}>
  <div style={{ position: 'absolute', left: '15px', top: '24px', bottom: '0', width: '1px', backgroundColor: '#334155' }}></div>

  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>1</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Clone Repository</h3>
    <CodeHeader title="BASH">
{`$ git clone https://github.com/TANISHX1/seat-allocation-sys.git
$ cd seat-allocation-sys`}
    </CodeHeader>
  </div>

  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>2</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Backend Setup</h3>
    <CodeHeader title="BASH">
{`# Navigate to backend directory
$ cd algo

# Create virtual environment
$ python -m venv venv

# Activate virtual environment (Windows)
$ venv\\Scripts\\activate

# Install Python dependencies
$ pip install -r requirements.txt`}
    </CodeHeader>
  </div>

  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>3</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Start Backend Server</h3>
    <p>The system initializes the database (demo.db) automatically on the first run.</p>
    <CodeHeader title="BASH">
{`$ cd algo
$ python app.py

# Expected Output:
🚀 Starting Seat Allocation System - Modular Backend
🔧 Environment: development
🐛 Debug Mode: True
* Running on http://localhost:5000`}
    </CodeHeader>
  </div>

  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>4</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Run Documentation Server</h3>
    <CodeHeader title="BASH">
{`$ cd Frontend/docs
$ npm start

# Runs on: http://localhost:3001`}
    </CodeHeader>
  </div>

  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>5</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Frontend Setup</h3>
    <CodeHeader title="BASH">
{`# From project root, navigate to Frontend
$ cd Frontend

$ npm install

$ npm start

Compiled successfully!
Local: http://localhost:3000`}
    </CodeHeader>
  </div>

<div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '0' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>6</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Access the Application</h3>
    <p>Open your browser and navigate to:</p>
    <div style={{ backgroundColor: '#1e293b', padding: '1rem', borderRadius: '0.5rem', fontFamily: 'monospace', color: '#f8fafc', borderLeft: '4px solid #f97316' }}>
      http://localhost:3000
    </div>
    <p style={{ marginTop: '1rem' }}>You should see the Seat Allocation System home page.</p>
  </div>
</div>

## Project Structure

<CodeHeader title="FILE STRUCTURE">
{`seat-allocation-sys/
├── algo/                    # Backend (Flask Modular Architecture)
│   ├── app.py              # Main entry point (Port 5000)
│   ├── main.py             # App factory & Route registration
│   ├── auth_service.py     # Auth logic & JWT management
│   ├── api/                # API Blueprints
│   │   └── blueprints/    # Individual feature routes
│   ├── core/               # Core business logic
│   │   ├── algorithm/     # Seating engine (seating.py)
│   │   ├── database/      # DB Schema & Queries (demo.db)
│   │   └── services/      # Logic isolation layer
│   └── ...
├── Frontend/               # React Application
│   ├── src/
│   │   ├── components/    # Reusable UI (Navbar, Bento, etc.)
│   │   ├── pages/         # Dashboard & Layouts
│   │   └── App.jsx        # Main context & routing
│   ├── docs/              # Documentation (Docusaurus - Port 3001)
│   └── package.json       # Frontend dependencies
├── tests/                  # Verification & Repro scripts
├── app.log                 # Backend system logs
└── demo.db                 # Primary SQLite database`}
</CodeHeader>

## First Time Usage

### 1. Create Account

1. Click **Sign Up** on the login page
2. Enter your details:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `SecurePass123`
   - Role: Select **STUDENT** or **FACULTY**
3. Click **Sign Up** (or use **Google Sign In**)

### 2. Upload Data (Optional)
To use real student names instead of counts:
1. Navigate to **Upload Data**
2. Download the CSV template
3. Fill with: *Name, Enrollment, Internal/External, BatchID*
4. Upload the file
5. Proceed to Generation options

### 3. Generate Seating

1. Log in with your credentials
2. Click **Generate Seating**
3. Fill in the form:
   - **Rows**: 8
   - **Columns**: 10
   - **Number of Batches**: 3
   - **Block Width**: 2
4. Click **Generate**
5. View the seating arrangement

6. (Optional) Use **Manual Allocation** to drag-and-drop students

### 4. Export Results

1. Once seating is generated
2. Click **Export PDF** button
3. PDF downloads to your device
4. Click **Attendance Sheet** to download signature lists per-batch

## Configuration

### Backend Configuration (algo/.env)

Create a `.env` file in the `algo` directory:

<CodeHeader title="ENV">
{`FLASK_ENV=development
JWT_SECRET=your_secret_key_here
DATABASE_URL=sqlite:///user_auth.db
CORS_ORIGINS=http://localhost:3000`}
</CodeHeader>

### Frontend Configuration (Frontend/.env)

Create a `.env` file in the `Frontend` directory:

<CodeHeader title="ENV">
{`REACT_APP_API_URL=http://localhost:5000`}
</CodeHeader>

## Environment Variables Reference

### Backend (.env in algo/)
<CodeHeader title="ENV">
{`FLASK_ENV              # development, production, testing
JWT_SECRET             # Secret key for JWT tokens
DATABASE_URL           # Database connection string
CORS_ORIGINS           # Allowed frontend origins
DEBUG                  # Enable debug mode (True/False)`}
</CodeHeader>

### Frontend (.env in Frontend/)
<CodeHeader title="ENV">
{`REACT_APP_API_URL      # Backend API base URL
REACT_APP_VERSION      # Application version`}
</CodeHeader>

## Development Workflow

### With Backend Running
<CodeHeader title="BASH">
{`$ cd algo
$ python app.py`}
</CodeHeader>
Runs on `http://localhost:5000`

### With Frontend Running
<CodeHeader title="BASH">
{`$ cd Frontend
$ npm start`}
</CodeHeader>
Runs on `http://localhost:3000`

### With Documentation Running
<CodeHeader title="BASH">
{`$ cd Frontend/docs
$ npm start`}
</CodeHeader>
Runs on `http://localhost:3000` (different port in docs package.json)

## Common Tasks

### Change Port Numbers

**Backend (algo/app.py):**
<CodeHeader title="PYTHON">
{`if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)`}
</CodeHeader>

**Frontend (Frontend/package.json):**
<CodeHeader title="JSON">
{`"scripts": {
  "start": "PORT=3001 react-scripts start"
}`}
</CodeHeader>

### Access Backend Logs

<CodeHeader title="BASH">
{`# The Flask server will show logs in the terminal
# Look for:
# - POST /api/generate-seating
# - GET /api/auth/profile`}
</CodeHeader>


### Database Registry

| Location | Purpose |
|---|---|
| `algo/demo.db` | Primary SQLite database |
| `algo/app.log` | Backend activity logs |
| `algo/user_auth.db` | Legacy authentication store (Auth v1) |

## File Descriptions

### Key Backend Files

| File | Purpose |
|---|---|
| `algo/app.py` | Flask REST API server |
| `algo/core/algorithm/seating.py` | Seating algorithm implementation |
| `algo/auth_service.py` | User authentication logic |
| `algo/student_parser.py` | Student data parsing |
| `algo/database/db.py` | SQLite database handler |

### Key Frontend Files

| File | Purpose |
|---|---|
| `Frontend/src/App.jsx` | Main application component |
| `Frontend/src/pages/` | Page components |
| `Frontend/src/components/` | Reusable UI components |
| `Frontend/src/context/AuthContext.jsx` | Authentication state management |

### Key Documentation Files

| File | Purpose |
|---|---|
| `docs/docs/intro.md` | Overview and introduction |
| `docs/docs/algorithm-documentation.md` | Complete technical reference |
| `docs/docs/system-architecture.md` | Architecture and data flow |
| `docs/docs/quick-reference.md` | Developer quick start |
| `docs/docs/authentication-setup.md` | Auth configuration guide |

## Troubleshooting

### Issue: "Port 3000 already in use"

**Solution:**
<CodeHeader title="BASH">
{`# Kill process on port 3000
# On macOS/Linux:
$ lsof -ti:3000 | xargs kill -9

# On Windows:
$ netstat -ano | findstr :3000
$ taskkill /PID <PID> /F`}
</CodeHeader>

### Issue: "Cannot find module 'flask'"

**Solution:**
<CodeHeader title="BASH">
{`$ pip install -r requirements.txt

# Or install individually
$ pip install Flask Flask-CORS`}
</CodeHeader>

### Issue: "npm ERR! Cannot find module"

**Solution:**
<CodeHeader title="BASH">
{`# Clear npm cache and reinstall
$ rm -rf node_modules package-lock.json
$ npm install`}
</CodeHeader>

### Issue: "Database locked" Error

**Solution:**
<CodeHeader title="BASH">
{`$ rm algo/user_auth.db
$ cd algo
$ python app.py`}
</CodeHeader>

### Issue: Backend and Frontend not connecting

**Solution:**
1. Verify backend is running on port 5000
2. Check frontend .env has correct API URL
3. Verify CORS is enabled in Flask app
4. Check browser console for specific errors

## Performance Tips

1. **Clear Cache**: Delete `__pycache__` and `node_modules` periodically
2. **Close Unused Tabs**: Reduces browser memory usage
3. **Monitor Logs**: Check console for errors during development
4. **Use Virtual Environment**: Isolates Python packages

## Security Reminders

:::warning Security Notice
**For Development Only**:
- Never use default credentials in production
- Change JWT_SECRET to a strong random value
- Use HTTPS in production
- Never commit .env files with secrets
:::

## Getting Help

- Check the specific documentation sections in the sidebar
- Review error messages carefully
- Check browser console for frontend errors
- Check terminal for backend errors
- Review [Troubleshooting](#troubleshooting) section above

## Next Steps

1. **Learn the Algorithm**: Read [Algorithm Documentation](./algorithm-documentation)
2. **Understand Architecture**: Check [System Architecture](./system-architecture)
3. **Integrate with Your App**: See [Quick Reference](./quick-reference)
4. **Setup Authentication**: Follow [Authentication Guide](./authentication-setup)

## Next: Run Your First Seating Generation

<CodeHeader title="BASH">
{`# 1. Backend running?
$ cd algo && python app.py

# 2. Frontend running?
$ cd Frontend && npm start

# 3. Open browser
# http://localhost:3000

# 4. Sign up and generate seating!`}
</CodeHeader>

---

**Version**: 2.3 <span style={{ backgroundColor: '#f97316', color: 'white', padding: '2px 6px', borderRadius: '4px', fontSize: '0.6rem' }}>NEW UPDATE</span>  
**Last Updated**: January 24, 2026
