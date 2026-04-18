# Attendance Tool Setup Guide

## Status
✅ **Method Created** - Compatibility workaround for Python 3.14 + Flask 3.1.0

## Problem
Flask 3.1.0 has a compatibility issue with Python 3.14. The `pkgutil.get_loader()` method was removed in Python 3.13+, causing:
```
AttributeError: module 'pkgutil' has no attribute 'get_loader'
```

## Solution
Created `/attendance_tool/run.py` - A wrapper script that monkey-patches `pkgutil` before Flask initializes.

```python
# Monkey-patch pkgutil.get_loader for compatibility with Python 3.14
if not hasattr(pkgutil, 'get_loader'):
    from importlib.util import find_spec
    def get_loader(module_name):
        spec = find_spec(module_name)
        return spec.loader if spec else None
    pkgutil.get_loader = get_loader
```

## To Run Attendance Tool

### Option 1: Use the wrapper script
```bash
cd /home/harshitdv/Documents/seat-allocation-sys/seat-alloc/attendance_tool
python run.py
```

### Option 2: Direct Flask command
```bash
cd /home/harshitdv/Documents/seat-allocation-sys/seat-alloc/attendance_tool
PYTHONPATH="." python -m flask run --port=5001
```

### Option 3: From virtual environment
```bash
cd /home/harshitdv/Documents/seat-allocation-sys
source .venv/bin/activate
cd seat-alloc/attendance_tool
python run.py
```

## Features
- **Port**: 5001
- **Functionality**: 
  - Upload Excel student lists (.xlsx)
  - Extract and preview data by branch
  - Configure room allocations dynamically
  - Generate seating PDFs and attendance sheets
  - Generate Excel master plans
  - All in-memory processing (no temp files)

## API Endpoints
- `GET /` - Upload interface  
- `POST /` - Upload and preview data
- `POST /generate` - Generate PDFs and Excel
- `GET /download/<filename>` - Download generated files

## Dependencies
All in `requirements.txt`:
- Flask 3.1.0
- pandas
- openpyxl  
- reportlab
- werkzeug

## Next Steps
1. Run: `python run.py`
2. Visit: `http://localhost:5001`
3. Upload a students Excel file
4. Configure rooms and room capacities
5. Generate and download seating plans
