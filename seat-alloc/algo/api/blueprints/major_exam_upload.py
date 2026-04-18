"""
Major Exam Upload Blueprint
Handles file uploads for major exam plans
"""
from flask import Blueprint, request, jsonify
import pandas as pd
import io
from pathlib import Path
import re
from datetime import datetime

from algo.services.auth_service import token_required
from algo.core.cache.major_exam_cache import get_major_cache_manager

major_exam_upload_bp = Blueprint('major_exam_upload', __name__, url_prefix='/api/major-exam')

cache_manager = get_major_cache_manager()

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

# Column detection patterns (flexible matching)
COLUMN_PATTERNS = {
    'name': [r'name', r'student.*name', r'full.*name', r'employee.*name'],
    'enrollment': [r'enrollment', r'enroll.*id', r'student.*id', r'roll.*no', r'roll.*number', r'student.*number'],
    'code': [r'code', r'subject.*code', r'course.*code', r'paper.*code', r'exam.*code'],
    'password': [r'password', r'pwd', r'pass', r'secret', r'access.*code']
}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_column_mapping(df_columns) -> dict:
    """
    Intelligently detect and map column names based on patterns.
    Returns dict mapping standard names to actual column names.
    """
    # Normalize columns for matching
    normalized_cols = {col: col.strip().lower() for col in df_columns}
    mapping = {}
    
    for standard_name, patterns in COLUMN_PATTERNS.items():
        for col, norm_col in normalized_cols.items():
            for pattern in patterns:
                if re.search(pattern, norm_col, re.IGNORECASE):
                    mapping[standard_name] = col
                    break
            if standard_name in mapping:
                break
    
    return mapping


def parse_upload_file(file) -> tuple:
    """Parse Excel or CSV file and return student data with intelligent column detection"""
    try:
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file.read()))
        else:  # .xlsx or .xls
            df = pd.read_excel(io.BytesIO(file.read()), sheet_name=0)
        
        if df.empty:
            return None, "File is empty"
        
        # Detect column mapping
        col_mapping = detect_column_mapping(df.columns)
        
        # Check if all required columns are found
        required_fields = ['name', 'enrollment', 'code', 'password']
        missing = [field for field in required_fields if field not in col_mapping]
        
        if missing:
            detected = list(col_mapping.keys())
            available = [col for col in df.columns]
            return None, f"Could not detect required columns: {', '.join(missing)}. Found: {', '.join(detected)}. Available: {', '.join(available)}"
        
        # Check for duplicates in enrollment column
        enrollment_col = col_mapping['enrollment']
        duplicates = df[enrollment_col].duplicated().sum()
        if duplicates > 0:
            return None, f"Found {duplicates} duplicate enrollment numbers"
        
        # Parse student data
        students = []
        for idx, row in df.iterrows():
            student = {
                'name': str(row.get(col_mapping['name'], '')).strip(),
                'enrollment': str(row.get(col_mapping['enrollment'], '')).strip(),
                'code': str(row.get(col_mapping['code'], '')).strip(),
                'password': str(row.get(col_mapping['password'], '')).strip(),
                'batch': idx % 2 + 1,  # Assign batch
                'paper_set': 'A'  # Default paper set
            }
            
            # Validate required fields are not empty
            if not all([student['name'], student['enrollment'], student['code'], student['password']]):
                return None, f"Row {idx + 1}: Missing required fields"
            
            students.append(student)
        
        return students, None
    except pd.errors.EmptyDataError:
        return None, "File is empty"
    except Exception as e:
        return None, f"Error parsing file: {str(e)}"


@major_exam_upload_bp.route('/upload', methods=['POST'])
@token_required
def upload_file():
    """Upload student data file"""
    try:
        user_id = request.user_id
        
        print(f"\n🔄 MAJOR EXAM UPLOAD START")
        print(f"   User ID: {user_id}")
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only Excel (.xlsx, .xls) and CSV files are allowed'}), 400
        
        # Parse file
        students, error = parse_upload_file(file)
        if error:
            return jsonify({'error': error}), 400
        
        print(f"   Parsed students: {len(students)}")
        
        # Generate plan ID
        plan_id = cache_manager.generate_plan_id()
        print(f"   Generated plan_id: {plan_id}")
        
        # Create plan data
        plan_data = {
            'plan_id': plan_id,
            'users_id': user_id,
            'exam_name': f'Major Exam - {plan_id}',
            'students': students,
            'metadata': {
                'total_students': len(students),
                'allocated_count': len(students),
                'room_count': 1,
                'status': 'uploaded'
            }
        }
        
        # Store in cache
        success = cache_manager.store_plan(user_id, plan_id, plan_data)
        print(f"   Store result: {success}")
        
        if not success:
            return jsonify({'error': 'Failed to store plan in cache'}), 500
        
        # AUTO-ALLOCATE STUDENTS IMMEDIATELY
        print(f"   Auto-allocating students...")
        try:
            from algo.api.blueprints.major_exam_allocation import allocate_students_to_rooms
            
            rooms = allocate_students_to_rooms(students)
            if rooms:
                plan_data['rooms'] = rooms
                plan_data['metadata']['status'] = 'FINALIZED'
                plan_data['metadata']['room_count'] = len(rooms)
                plan_data['metadata']['allocated_count'] = len(students)
                plan_data['metadata']['finalized_at'] = datetime.utcnow().isoformat() + 'Z'
                
                # Save with allocations
                success = cache_manager.store_plan(user_id, plan_id, plan_data)
                print(f"   Auto-allocation result: {success}")
                if not success:
                    print(f"   Warning: Auto-allocation save failed, but plan exists")
            else:
                print(f"   Warning: Auto-allocation returned no rooms")
        except Exception as e:
            print(f"   Warning: Auto-allocation failed: {e}")
            # Don't fail the upload if allocation fails, plan was already saved
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'total_students': len(students),
            'message': f'File uploaded successfully. Plan ID: {plan_id}'
        }), 201
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_upload_bp.route('/plan/<plan_id>', methods=['GET'])
@token_required
def get_plan_details(plan_id):
    """Get plan details"""
    try:
        user_id = request.user_id
        
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        return jsonify({
            'success': True,
            'plan': {
                'plan_id': plan.get('plan_id'),
                'exam_name': plan.get('exam_name'),
                'created_at': plan.get('created_at'),
                'total_students': plan.get('metadata', {}).get('total_students', 0),
                'allocated_count': plan.get('metadata', {}).get('allocated_count', 0),
                'room_count': plan.get('metadata', {}).get('room_count', 0),
                'status': plan.get('metadata', {}).get('status', 'pending')
            }
        }), 200
    
    except Exception as e:
        print(f"❌ Error fetching plan: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_upload_bp.route('/recent', methods=['GET'])
@token_required
def get_recent_plans():
    """Get recent major exam plans"""
    try:
        user_id = request.user_id
        
        print(f"\n📋 MAJOR EXAM GET RECENT")
        print(f"   User ID: {user_id}")
        
        plans = cache_manager.get_all_user_plans(user_id, limit=5)
        
        print(f"   Found {len(plans)} plans")
        for plan in plans:
            print(f"     - {plan.get('plan_id')}: {plan.get('status')}")
        
        return jsonify({
            'success': True,
            'plans': plans
        }), 200
    
    except Exception as e:
        print(f"Error fetching recent plans: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500
