"""
Major Exam Upload Blueprint
Handles file uploads with multi-sheet branch-aware parsing.
Each sheet in the uploaded Excel = one branch. Sheet name = branch name.
"""
from flask import Blueprint, request, jsonify
import pandas as pd
import io
import re
from datetime import datetime

from algo.services.auth_service import token_required
from algo.core.cache.major_exam_cache import get_major_cache_manager

major_exam_upload_bp = Blueprint('major_exam_upload', __name__, url_prefix='/api/major-exam')

cache_manager = get_major_cache_manager()

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Flexible column detection patterns
COLUMN_PATTERNS = {
    'name': [r'name', r'student.*name', r'full.*name'],
    'enrollment': [r'enrollment', r'enroll', r'student.*id', r'roll.*no', r'roll.*number'],
    'code': [r'code', r'subject.*code', r'course.*code', r'paper.*code'],
    'password': [r'password', r'pwd', r'pass', r'passowrd']  # note: handles typo 'Passowrd'
}

# Branch alias groups aligned with minor PDF generation branch expansion logic
# (CS -> CSE, CD -> CSD, EC -> ECE, EE -> EEE) with full-name keyword aliases.
BRANCH_ALIAS_GROUPS = {
    'CSE': {
        'CSE', 'CS', 'COMPUTERSCIENCE', 'COMPUTERSCIENCEENGINEERING',
        'COMPUTERSCIENCEANDENGINEERING'
    },
    'CSD': {
        'CSD', 'CD', 'COMPUTERSCIENCEDESIGN', 'COMPUTERSCIENCEANDDESIGN'
    },
    'ECE': {
        'ECE', 'EC', 'ELECTRONICSCOMMUNICATION',
        'ELECTRONICSCOMMUNICATIONENGINEERING',
        'ELECTRONICSANDCOMMUNICATIONENGINEERING'
    },
    'EEE': {
        'EEE', 'EE', 'ELECTRICALENGINEERING',
        'ELECTRICALANDELECTRONICSENGINEERING'
    },
    'IT': {
        'IT', 'INFORMATIONTECHNOLOGY'
    },
    'ME': {
        'ME', 'MECHANICALENGINEERING'
    },
    'CE': {
        'CE', 'CIVILENGINEERING'
    },
    'ET': {
        'ET', 'ELECTRONICSTELECOMMUNICATIONENGINEERING',
        'ELECTRONICSANDTELECOMMUNICATIONENGINEERING'
    },
}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _normalize_branch_key(value: str) -> str:
    """Normalize branch name for alias matching."""
    return re.sub(r'[^A-Z0-9]', '', str(value or '').upper())


def _resolve_branch_group(normalized_branch: str) -> str:
    """Resolve a normalized branch token into a known alias group."""
    for group_name, aliases in BRANCH_ALIAS_GROUPS.items():
        if normalized_branch in aliases:
            return group_name
    return ''


def _build_branch_lookup(available_branches) -> dict:
    """Build normalized lookup map from user-provided branch labels to stored branch names."""
    lookup = {}

    for branch in available_branches:
        normalized = _normalize_branch_key(branch)
        if not normalized:
            continue

        # Exact normalized match
        lookup[normalized] = branch

        # Alias expansion (e.g. CS -> CSE, EC -> ECE)
        group = _resolve_branch_group(normalized)
        if group:
            for alias in BRANCH_ALIAS_GROUPS[group]:
                lookup.setdefault(alias, branch)

    return lookup


def detect_columns(df_columns) -> dict:
    """
    Detect and map column names using fuzzy pattern matching.
    Returns dict: standard_name -> actual_column_name
    """
    normalized = {col: col.strip().lower() for col in df_columns}
    mapping = {}

    for standard_name, patterns in COLUMN_PATTERNS.items():
        for col, norm in normalized.items():
            for pattern in patterns:
                if re.search(pattern, norm, re.IGNORECASE):
                    mapping[standard_name] = col
                    break
            if standard_name in mapping:
                break

    return mapping


def clean_value(val):
    """Clean a cell value: handle NaN, floats, whitespace"""
    s = str(val).strip()
    if s.lower() in ('nan', 'none', ''):
        return ''
    # Fix float-encoded integers (e.g. 734292.0 -> 734292)
    if s.endswith('.0'):
        try:
            return str(int(float(s)))
        except (ValueError, OverflowError):
            pass
    return s


def parse_excel_branched(file_bytes: bytes) -> tuple:
    """
    Parse multi-sheet Excel file where each sheet = one branch.
    Sheet name = branch name.

    Returns:
        (result_dict, error_string)
        result_dict has: branches, total_students, preview
    """
    try:
        xl = pd.ExcelFile(io.BytesIO(file_bytes))

        if not xl.sheet_names:
            return None, "Excel file has no sheets"

        branches = {}
        preview = {}
        total_students = 0

        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)

            if df.empty or len(df) < 1:
                continue

            # Clean column names
            df.columns = df.columns.str.strip()

            # Detect column mapping
            col_map = detect_columns(df.columns)

            # Need at least enrollment and name columns
            if 'enrollment' not in col_map or 'name' not in col_map:
                # Skip sheets that don't have student data
                continue

            # Extract student records
            students = []
            for idx, row in df.iterrows():
                enrollment = clean_value(row.get(col_map['enrollment'], ''))
                name = clean_value(row.get(col_map['name'], ''))

                # Skip rows with empty enrollment or name (header rows, blank rows)
                if not enrollment or not name:
                    continue

                student = {
                    'sno': len(students) + 1,
                    'enrollment': enrollment,
                    'name': name,
                    'code': clean_value(row.get(col_map.get('code', ''), '')),
                    'password': clean_value(row.get(col_map.get('password', ''), '')),
                    'branch': sheet_name.strip()
                }
                students.append(student)

            if not students:
                continue

            # Sort by enrollment within branch
            students.sort(key=lambda s: s['enrollment'])

            # Re-number after sorting
            for i, s in enumerate(students):
                s['sno'] = i + 1

            branch_name = sheet_name.strip()
            branches[branch_name] = {
                'students': students,
                'count': len(students)
            }

            # Preview: first 10 students (safe subset for frontend display)
            preview[branch_name] = [
                {k: v for k, v in s.items() if k != 'branch'}
                for s in students[:10]
            ]

            total_students += len(students)

        if not branches:
            return None, "No valid student data found in any sheet. Ensure columns include Enrollment and Name."

        return {
            'branches': branches,
            'total_students': total_students,
            'preview': preview,
            'branch_names': list(branches.keys()),
            'branch_counts': {name: data['count'] for name, data in branches.items()}
        }, None

    except Exception as e:
        return None, f"Error parsing file: {str(e)}"


@major_exam_upload_bp.route('/upload', methods=['POST'])
@token_required
def upload_file():
    """
    Upload student data Excel file.
    Each sheet = one branch. Sheet name = branch name.
    Returns branch-wise preview for confirmation step.
    """
    try:
        user_id = request.user_id

        print(f"\n🔄 MAJOR EXAM UPLOAD START")
        print(f"   User ID: {user_id}")

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Only Excel (.xlsx, .xls) files are allowed'}), 400

        # Read file bytes (keep in memory)
        file_bytes = file.read()

        # Parse with branch detection
        result, error = parse_excel_branched(file_bytes)
        if error:
            return jsonify({'error': error}), 400

        print(f"   Branches found: {list(result['branches'].keys())}")
        print(f"   Total students: {result['total_students']}")
        for branch, data in result['branches'].items():
            print(f"     {branch}: {data['count']} students")

        # Generate plan ID
        plan_id = cache_manager.generate_plan_id()
        print(f"   Generated plan_id: {plan_id}")

        # Create plan data (no allocation yet — that happens after room config)
        plan_data = {
            'plan_id': plan_id,
            'user_id': user_id,
            'exam_name': f'Major Exam - {plan_id}',
            'branches': {
                name: data['students']
                for name, data in result['branches'].items()
            },
            'metadata': {
                'total_students': result['total_students'],
                'branch_names': result['branch_names'],
                'branch_counts': result['branch_counts'],
                'status': 'uploaded',
                'uploaded_at': datetime.utcnow().isoformat() + 'Z'
            }
        }

        # Store in cache
        success = cache_manager.store_plan(user_id, plan_id, plan_data)
        print(f"   Store result: {success}")

        if not success:
            return jsonify({'error': 'Failed to store plan in cache'}), 500

        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'total_students': result['total_students'],
            'branch_names': result['branch_names'],
            'branch_counts': result['branch_counts'],
            'preview': result['preview'],
            'message': f'File parsed successfully. {len(result["branches"])} branch(es) detected.'
        }), 201

    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_upload_bp.route('/configure-rooms/<plan_id>', methods=['POST'])
@token_required
def configure_rooms(plan_id):
    """
    Configure room allocation for a plan.
    Accepts rooms with name, capacity, and assigned branches.
    Runs sequential allocation and saves result.

    Body: {
      "rooms": [
        { "name": "Lab 104", "capacity": 50, "branches": ["CSE", "CSD"] },
        { "name": "Lab 105", "capacity": 35, "branches": ["CSE"] }
      ],
      "metadata": { "exam_name": "...", "date": "..." }  // optional
    }
    """
    try:
        user_id = request.user_id
        data = request.json or {}

        print(f"\n🏫 CONFIGURE ROOMS")
        print(f"   User ID: {user_id}, Plan ID: {plan_id}")

        # Retrieve plan
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        available_branches = plan.get('metadata', {}).get('branch_names') or list((plan.get('branches') or {}).keys())
        if not available_branches:
            return jsonify({'error': 'No branch data found in plan. Re-upload the Excel file.'}), 400

        branch_lookup = _build_branch_lookup(available_branches)

        if plan.get('metadata', {}).get('status') != 'uploaded':
            # Allow re-configuration
            pass

        rooms_config = data.get('rooms', [])
        if not rooms_config:
            return jsonify({'error': 'No rooms provided'}), 400

        # Validate rooms
        for room in rooms_config:
            if not room.get('name'):
                return jsonify({'error': 'Each room must have a name'}), 400
            if not room.get('capacity') or int(room['capacity']) < 1:
                return jsonify({'error': f'Room "{room["name"]}" must have a valid capacity'}), 400
            if not room.get('branches') or len(room['branches']) < 1:
                return jsonify({'error': f'Room "{room["name"]}" must have at least one branch assigned'}), 400

            normalized_room_branches = []
            unknown_branches = []
            seen = set()

            for raw_branch in room.get('branches', []):
                normalized_key = _normalize_branch_key(raw_branch)
                resolved_branch = branch_lookup.get(normalized_key)

                if not resolved_branch:
                    unknown_branches.append(str(raw_branch))
                    continue

                if resolved_branch not in seen:
                    normalized_room_branches.append(resolved_branch)
                    seen.add(resolved_branch)

            if unknown_branches:
                return jsonify({
                    'error': f'Room "{room["name"]}" has unknown branch(es): {", ".join(unknown_branches)}',
                    'unknown_branches': unknown_branches,
                    'available_branches': available_branches,
                }), 400

            if not normalized_room_branches:
                return jsonify({'error': f'Room "{room["name"]}" must map to at least one valid branch'}), 400

            # Persist normalized branches so allocation always receives canonical keys.
            room['branches'] = normalized_room_branches

        # Run allocation
        from algo.api.blueprints.major_exam_allocation import allocate_branches_to_rooms

        branches_data = plan.get('branches', {})
        allocation_result = allocate_branches_to_rooms(branches_data, rooms_config)

        if not allocation_result:
            return jsonify({'error': 'Allocation failed — check room capacities and branch data'}), 500

        # Update plan with allocation
        plan['rooms'] = allocation_result['rooms']
        plan['rooms_config'] = rooms_config
        plan['metadata']['status'] = 'FINALIZED'
        plan['metadata']['room_count'] = len(allocation_result['rooms'])
        plan['metadata']['allocated_count'] = allocation_result['total_allocated']
        plan['metadata']['finalized_at'] = datetime.utcnow().isoformat() + 'Z'

        # Merge optional metadata
        extra_meta = data.get('metadata', {})
        if extra_meta:
            plan['metadata'].update(extra_meta)

        success = cache_manager.store_plan(user_id, plan_id, plan)
        print(f"   Allocation stored: {success}")

        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'status': 'FINALIZED',
            'total_allocated': allocation_result['total_allocated'],
            'rooms': [
                {
                    'name': r['room_name'],
                    'total': r['total_students'],
                    'branches': {
                        b: info['count']
                        for b, info in r['branch_allocations'].items()
                    }
                }
                for r in allocation_result['rooms']
            ],
            'message': f'Plan finalized. {allocation_result["total_allocated"]} students across {len(allocation_result["rooms"])} rooms.'
        }), 200

    except Exception as e:
        print(f"❌ Configure rooms error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_upload_bp.route('/plan/<plan_id>', methods=['GET'])
@token_required
def get_plan_details(plan_id):
    """Get plan details including branch and room info"""
    try:
        user_id = request.user_id

        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        metadata = plan.get('metadata', {})

        # Build room summaries
        rooms_summary = []
        for room in plan.get('rooms', []):
            rooms_summary.append({
                'name': room.get('room_name', ''),
                'capacity': room.get('capacity', 0),
                'total_students': room.get('total_students', 0),
                'branches': {
                    b: info['count']
                    for b, info in room.get('branch_allocations', {}).items()
                }
            })

        return jsonify({
            'success': True,
            'plan': {
                'plan_id': plan.get('plan_id'),
                'exam_name': plan.get('exam_name'),
                'created_at': plan.get('created_at'),
                'total_students': metadata.get('total_students', 0),
                'allocated_count': metadata.get('allocated_count', 0),
                'room_count': metadata.get('room_count', 0),
                'status': metadata.get('status', 'pending'),
                'branch_names': metadata.get('branch_names', []),
                'branch_counts': metadata.get('branch_counts', {}),
                'rooms': rooms_summary
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

        return jsonify({
            'success': True,
            'plans': plans
        }), 200

    except Exception as e:
        print(f"Error fetching recent plans: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500
