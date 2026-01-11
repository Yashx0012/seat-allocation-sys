---
sidebar_position: 2
---

# Getting Started

Quick start guide to get the Seat Allocation System up and running.

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
    <div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
      <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
        <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
        <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
        <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
        <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>git clone https://github.com/TANISHX1/seat-allocation-sys.git</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>cd seat-allocation-sys</span>
        </div>
      </div>
    </div>
  </div>

  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>2</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Backend Setup</h3>
    <div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
      <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
        <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
        <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
        <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
        <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
        <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Navigate to backend directory</div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>cd algo</span>
        </div>
        <br/>
        <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Create virtual environment</div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>python -m venv venv</span>
        </div>
        <br/>
        <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Activate virtual environment (Windows)</div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>venv\Scripts\activate</span>
        </div>
        <br/>
        <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Install Python dependencies</div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>pip install -r requirements.txt</span>
        </div>
      </div>
    </div>
  </div>

  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>3</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Database Initialization</h3>
    <div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
      <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
        <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
        <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
        <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
        <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
        <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Go to Backend directory</div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>cd ../Backend</span>
        </div>
        <br/>
        <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Initialize database</div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>python database.py</span>
        </div>
         <div style={{ display: 'flex', alignItems: 'center', color: '#4ade80' }}>
          <span style={{ color: 'transparent', marginRight: '5px' }}>$</span>
          <span style={{ fontStyle: 'italic' }}>Database initialized successfully</span>
        </div>
        <br/>
        <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Return to algo directory</div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>cd ../algo</span>
        </div>
      </div>
    </div>
  </div>

  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>4</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Start Backend Server</h3>
    <div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
      <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
        <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
        <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
        <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
        <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>python app.py</span>
        </div>
         <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}>
          <span style={{ color: 'transparent', marginRight: '5px' }}>$</span>
          <span>* Running on http://localhost:5000</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}>
          <span style={{ color: 'transparent', marginRight: '5px' }}>$</span>
          <span>* Debug mode: on</span>
        </div>
      </div>
    </div>
  </div>

  <div style={{ position: 'relative', paddingLeft: '3.5rem', paddingBottom: '3rem' }}>
    <div style={{ position: 'absolute', left: '0', top: '0', width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#f97316', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px', border: '4px solid var(--ifm-background-color)' }}>5</div>
    <h3 style={{ marginTop: '0', marginBottom: '1rem', fontSize: '1.25rem' }}>Frontend Setup</h3>
    <div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
      <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
        <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
        <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
        <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
        <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
        <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># From project root, navigate to Frontend</div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>cd Frontend</span>
        </div>
        <br/>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>npm install</span>
        </div>
        <br/>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
          <span style={{ color: '#f8fafc' }}>npm start</span>
        </div>
        <br/>
         <div style={{ display: 'flex', alignItems: 'center', color: '#4ade80' }}>
          <span style={{ color: 'transparent', marginRight: '5px' }}>$</span>
          <span>Compiled successfully!</span>
        </div>
         <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}>
          <span style={{ color: 'transparent', marginRight: '5px' }}>$</span>
          <span>Local: http://localhost:3000</span>
        </div>
      </div>
    </div>
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

```
seat-allocation-sys/
├── algo/                    # Backend (Flask)
│   ├── app.py              # Main Flask application
│   ├── algo.py             # Seating algorithm
│   ├── auth_service.py     # Authentication logic
│   ├── requirements.txt    # Python dependencies
│   └── ...
├── Backend/                # Database & Auth
│   ├── database.py         # Database setup
│   └── auth_service.py     # Authentication service
├── Frontend/               # React application
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── context/       # Context providers
│   │   └── App.jsx        # Main app component
│   ├── package.json       # npm dependencies
│   └── ...
└── docs/                   # Documentation (Docusaurus)
    ├── docs/              # Documentation files
    └── docusaurus.config.js
```

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

```env
FLASK_ENV=development
JWT_SECRET=your_secret_key_here
DATABASE_URL=sqlite:///user_auth.db
CORS_ORIGINS=http://localhost:3000
```

### Frontend Configuration (Frontend/.env)

Create a `.env` file in the `Frontend` directory:

```env
REACT_APP_API_URL=http://localhost:5000
```

## Environment Variables Reference

### Backend (.env in algo/)
```env
FLASK_ENV              # development, production, testing
JWT_SECRET             # Secret key for JWT tokens
DATABASE_URL           # Database connection string
CORS_ORIGINS           # Allowed frontend origins
DEBUG                  # Enable debug mode (True/False)
```

### Frontend (.env in Frontend/)
```env
REACT_APP_API_URL      # Backend API base URL
REACT_APP_VERSION      # Application version
```

## Development Workflow

### With Backend Running
<div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
  <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
    <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
    <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
    <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
    <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>cd algo</span>
    </div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>python app.py</span>
    </div>
  </div>
</div>
Runs on `http://localhost:5000`

### With Frontend Running
<div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
  <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
    <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
    <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
    <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
    <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>cd Frontend</span>
    </div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>npm start</span>
    </div>
  </div>
</div>
Runs on `http://localhost:3000`

### With Documentation Running
<div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
  <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
    <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
    <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
    <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
    <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>cd Frontend/docs</span>
    </div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>npm start</span>
    </div>
  </div>
</div>
Runs on `http://localhost:3000` (different port in docs package.json)

## Common Tasks

### Change Port Numbers

**Backend (algo/app.py):**
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
```

**Frontend (Frontend/package.json):**
```json
"scripts": {
  "start": "PORT=3001 react-scripts start"
}
```

### Access Backend Logs

<div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
  <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
    <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
    <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
    <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
    <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># The Flask server will show logs in the terminal</div>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Look for:</div>
     <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># - POST /api/generate-seating</div>
     <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># - GET /api/auth/profile</div>
  </div>
</div>


### Check Database Status

<div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
  <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
    <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
    <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
    <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
    <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>ls -la Backend/user_auth.db</span>
    </div>
  </div>
</div>

## File Descriptions

### Key Backend Files

| File | Purpose |
|---|---|
| `algo/app.py` | Flask REST API server |
| `algo/algo.py` | Seating algorithm implementation |
| `algo/auth_service.py` | User authentication logic |
| `algo/student_parser.py` | Student data parsing |
| `Backend/database.py` | SQLite database handler |

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
<div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
  <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
    <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
    <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
    <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
    <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Kill process on port 3000</div>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># On macOS/Linux:</div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>lsof -ti:3000 | xargs kill -9</span>
    </div>
    <br/>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># On Windows:</div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>netstat -ano | findstr :3000</span>
    </div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>taskkill /PID &lt;PID&gt; /F</span>
    </div>
  </div>
</div>

### Issue: "Cannot find module 'flask'"

**Solution:**
<div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
  <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
    <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
    <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
    <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
    <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>pip install -r requirements.txt</span>
    </div>
    <br/>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Or install individually</div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>pip install Flask Flask-CORS</span>
    </div>
  </div>
</div>

### Issue: "npm ERR! Cannot find module"

**Solution:**
<div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
  <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
    <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
    <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
    <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
    <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># Clear npm cache and reinstall</div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>rm -rf node_modules package-lock.json</span>
    </div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>npm install</span>
    </div>
  </div>
</div>

### Issue: "Database locked" Error

**Solution:**
<div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
  <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
    <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
    <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
    <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
    <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>rm Backend/user_auth.db</span>
    </div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>cd Backend</span>
    </div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>python database.py</span>
    </div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>cd ../algo</span>
    </div>
  </div>
</div>

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

<div style={{ width: '100%', height: 'auto', backgroundColor: '#1e293b', borderRadius: '10px', display: 'grid', gridTemplateRows: '40px 1fr', marginBottom: '20px', position: 'relative', overflow: 'hidden', fontFamily: 'monospace' }}>
  <div style={{ display: 'flex', alignItems: 'center', position: 'relative', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: '100%' }}>
    <span style={{ color: '#7dd3fc', fontSize: '13px', padding: '2px 12px' }}>Terminal</span>
    <button style={{ position: 'absolute', background: 'transparent', border: 'none', top: '50%', right: '15px', transform: 'translateY(-50%)', color: 'rgb(100, 116, 139)', cursor: 'pointer', fontSize: '12px' }}>Copy</button>
    <div style={{ content: '""', position: 'absolute', borderTopLeftRadius: '5px', borderTopRightRadius: '5px', border: '1px solid rgba(100, 116, 139, 0.3)', right: '1px', bottom: '0', backgroundColor: 'rgba(51, 65, 85, 0.5)', width: 'calc(100% - 2px)', height: '33px', zIndex: '100', pointerEvents: 'none' }}></div>
    <div style={{ content: '""', position: 'absolute', width: '100%', height: '1px', backgroundColor: '#f97316', bottom: '0', opacity: '0.5' }}></div>
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '15px 10px', backgroundColor: '#1e293b' }}>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># 1. Backend running?</div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>cd algo && python app.py</span>
    </div>
    <br/>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># 2. Frontend running?</div>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <span style={{ color: 'rgb(244, 114, 182)', paddingTop: '3px', marginRight: '5px' }}>$</span>
      <span style={{ color: '#f8fafc' }}>cd Frontend && npm start</span>
    </div>
    <br/>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># 3. Open browser</div>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># http://localhost:3000</div>
    <br/>
    <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8' }}># 4. Sign up and generate seating!</div>
  </div>
</div>

---

**Version**: 2.2  
**Last Updated**: January 2026
