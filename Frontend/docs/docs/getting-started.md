---
sidebar_position: 2
---

# Getting Started

Quick start guide to get the Seat Allocation System up and running.

## Prerequisites

- **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.8 or higher) - [Download](https://www.python.org/)
- **Git** - [Download](https://git-scm.com/)

Verify installations:
```bash
node --version
python --version
```

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

```bash
git clone https://github.com/TANISHX1/seat-allocation-sys.git
cd seat-allocation-sys
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd algo

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Database Initialization

```bash
# Go to Backend directory
cd ../Backend

# Initialize database
python database.py

# You should see: "Database initialized successfully"

# Return to algo directory
cd ../algo
```

### Step 4: Start Backend Server

```bash
# From algo directory
python app.py
```

**Expected Output:**
```
 * Running on http://localhost:5000
 * Debug mode: on
 * Press CTRL+C to quit
```

### Step 5: Frontend Setup (New Terminal)

```bash
# From project root, navigate to Frontend
cd Frontend

# Install npm dependencies
npm install

# Start development server
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view your app in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

### Step 6: Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the Seat Allocation System home page.

## First Time Usage

### 1. Create Account

1. Click **Sign Up** on the login page
2. Enter your details:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `SecurePass123`
   - Role: Select **STUDENT** or **FACULTY**
3. Click **Sign Up**

### 2. Generate Seating

1. Log in with your credentials
2. Click **Generate Seating**
3. Fill in the form:
   - **Rows**: 8
   - **Columns**: 10
   - **Number of Batches**: 3
   - **Block Width**: 2
4. Click **Generate**
5. View the seating arrangement

### 3. Export to PDF

1. Once seating is generated
2. Click **Export PDF** button
3. PDF downloads to your device

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

```bash
# The Flask server will show logs in the terminal
# Look for:
# - POST /api/generate-seating
# - GET /api/auth/profile
```

### Check Database Status

```bash
# View database file
ls -la Backend/user_auth.db

# Check file size and modification time
```

## Troubleshooting

### Issue: "Port 3000 already in use"

**Solution:**
```bash
# Kill process on port 3000
# On macOS/Linux:
lsof -ti:3000 | xargs kill -9

# On Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Issue: "Cannot find module 'flask'"

**Solution:**
```bash
# Ensure pip packages are installed
pip install -r requirements.txt

# Or install individually
pip install Flask Flask-CORS
```

### Issue: "npm ERR! Cannot find module"

**Solution:**
```bash
# Clear npm cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: "Database locked" Error

**Solution:**
```bash
# Close all connections and recreate database
rm Backend/user_auth.db
cd Backend
python database.py
cd ../algo
```

### Issue: Backend and Frontend not connecting

**Solution:**
1. Verify backend is running on port 5000
2. Check frontend .env has correct API URL
3. Verify CORS is enabled in Flask app
4. Check browser console for specific errors

## Next Steps

1. **Learn the Algorithm**: Read [Algorithm Documentation](./algorithm-documentation)
2. **Understand Architecture**: Check [System Architecture](./system-architecture)
3. **Integrate with Your App**: See [Quick Reference](./quick-reference)
4. **Setup Authentication**: Follow [Authentication Guide](./authentication-setup)

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

## Development Workflow

### With Backend Running
```bash
cd algo
python app.py
```
Runs on `http://localhost:5000`

### With Frontend Running
```bash
cd Frontend
npm start
```
Runs on `http://localhost:3000`

### With Documentation Running
```bash
cd Frontend/docs
npm start
```
Runs on `http://localhost:3000` (different port in docs package.json)

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

## Performance Tips

1. **Clear Cache**: Delete `__pycache__` and `node_modules` periodically
2. **Close Unused Tabs**: Reduces browser memory usage
3. **Monitor Logs**: Check console for errors during development
4. **Use Virtual Environment**: Isolates Python packages

## Getting Help

- Check the specific documentation sections in the sidebar
- Review error messages carefully
- Check browser console for frontend errors
- Check terminal for backend errors
- Review [Troubleshooting](#troubleshooting) section above

## Security Reminders

**For Development Only**:
- Never use default credentials in production
- Change JWT_SECRET to a strong random value
- Use HTTPS in production
- Never commit .env files with secrets

## Next: Run Your First Seating Generation

```bash
# 1. Backend running?
# Terminal 1: cd algo && python app.py

# 2. Frontend running?
# Terminal 2: cd Frontend && npm start

# 3. Open browser
# http://localhost:3000

# 4. Sign up and generate seating!
```

---

**Version**: 2.1  
**Last Updated**: January 2026
