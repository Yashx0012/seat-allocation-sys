"""
Major Exam Allocation Blueprint
Analyzes cached JSON student data and creates room-wise allocation
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from algo.services.auth_service import token_required
from algo.core.cache.major_exam_cache import get_major_cache_manager

major_exam_allocation_bp = Blueprint('major_exam_allocation', __name__, url_prefix='/api/major-exam')
cache_manager = get_major_cache_manager()
logger = logging.getLogger(__name__)


# Default classroom rooms for allocation
DEFAULT_ROOMS = [
    {'name': 'Lab M005', 'capacity': 30},
    {'name': 'Lab 104', 'capacity': 50},
    {'name': 'Lab 105', 'capacity': 35},
    {'name': 'Project Lab', 'capacity': 28},
    {'name': 'CC Lab', 'capacity': 22},
]


def allocate_students_to_rooms(students: list, room_config: list = None) -> dict:
    """
    Analyze cached student JSON and allocate to rooms
    Creates roll number ranges for each room/batch allocation
    
    Args:
        students: List of student dicts from cached JSON
        room_config: Optional list of room configs, defaults to DEFAULT_ROOMS
        
    Returns:
        Dict with rooms structure: {room_name: {batches: {batch_label: {...}}}}
    """
    if not students:
        return {}
    
    rooms_config = room_config or DEFAULT_ROOMS
    rooms = {}
    
    # Sort students by enrollment number for consistent ordering
    sorted_students = sorted(students, key=lambda s: s.get('enrollment', ''))
    
    # Distribute students across rooms based on capacity
    total_capacity = sum(r['capacity'] for r in rooms_config)
    student_idx = 0
    
    for room_config_item in rooms_config:
        room_name = room_config_item['name']
        room_capacity = room_config_item['capacity']
        
        # Calculate how many students for this room
        # Distribute proportionally based on capacity
        proportion = room_capacity / total_capacity
        students_for_room = int(len(sorted_students) * proportion)
        
        # Adjust last room to get all remaining students
        if room_name == rooms_config[-1]['name']:
            students_for_room = len(sorted_students) - student_idx
        
        room_students = sorted_students[student_idx:student_idx + students_for_room]
        student_idx += students_for_room
        
        if not room_students:
            continue
        
        # Create batches within room (Batch A, Batch B)
        batches = {}
        
        # Split into 2 batches per room
        mid = len(room_students) // 2
        batch_configs = [
            ('Batch A', room_students[:mid]),
            ('Batch B', room_students[mid:])
        ]
        
        for batch_label, batch_students in batch_configs:
            if not batch_students:
                continue
            
            # Get enrollment numbers for From/To range
            enrollments = [s.get('enrollment', '') for s in batch_students]
            enrollments = [e for e in enrollments if e.strip()]  # Filter empty
            enrollments.sort()
            
            if enrollments:
                from_roll = enrollments[0]
                to_roll = enrollments[-1]
                
                batches[batch_label] = {
                    'info': {
                        'branch': 'CSE',
                        'semester': 'IV',
                        'joining_year': '2024',
                        'degree': 'B.Tech'
                    },
                    'students': batch_students,
                    'from_roll': from_roll,
                    'to_roll': to_roll,
                    'total': len(batch_students)
                }
        
        if batches:
            rooms[room_name] = {
                'name': room_name,
                'capacity': room_capacity,
                'allocated_count': len(room_students),
                'batches': batches
            }
    
    return rooms


@major_exam_allocation_bp.route('/allocate/<plan_id>', methods=['POST'])
@token_required
def allocate_plan(plan_id):
    """
    Analyze cached JSON student data and allocate to rooms
    Creates From/To roll number ranges for each room batch
    Endpoint: POST /api/major-exam/allocate/<plan_id>
    """
    try:
        user_id = request.user_id
        
        print(f"\n🏫 MAJOR EXAM ALLOCATE START")
        print(f"   User ID: {user_id}")
        print(f"   Plan ID: {plan_id}")
        
        # Retrieve plan from cache
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            print(f"   ERROR: Plan not found")
            return jsonify({'error': 'Plan not found', 'plan_id': plan_id}), 404
        
        students = plan.get('students', [])
        print(f"   Students in plan: {len(students)}")
        
        if not students:
            return jsonify({'error': 'No students in plan'}), 400
        
        # Allocate students to rooms (analyze JSON data)
        rooms = allocate_students_to_rooms(students)
        print(f"   Allocated to rooms: {len(rooms)}")
        
        if not rooms:
            return jsonify({'error': 'Allocation failed'}), 500
        
        # Update plan with room allocations
        plan['rooms'] = rooms
        plan['metadata']['status'] = 'FINALIZED'
        plan['metadata']['room_count'] = len(rooms)
        plan['metadata']['allocated_count'] = len(students)
        plan['metadata']['finalized_at'] = datetime.utcnow().isoformat() + 'Z'
        
        # Store updated plan back to cache
        stored = cache_manager.store_plan(user_id, plan_id, plan)
        print(f"   Store result: {stored}")
        
        # Return summary
        total_allocated = sum(r['allocated_count'] for r in rooms.values())
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'status': 'FINALIZED',
            'rooms_count': len(rooms),
            'total_allocated': total_allocated,
            'rooms': {
                room_name: {
                    'allocated_count': room_data['allocated_count'],
                    'batch_count': len(room_data.get('batches', {}))
                }
                for room_name, room_data in rooms.items()
            },
            'message': f'Plan finalized. {total_allocated} students allocated across {len(rooms)} rooms'
        }), 200
    
    except Exception as e:
        logger.error(f"Allocation error: {e}", exc_info=True)
        print(f"❌ Allocation error: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_allocation_bp.route('/status/<plan_id>', methods=['GET'])
@token_required
def get_allocation_status(plan_id):
    """Get allocation status of a plan"""
    try:
        user_id = request.user_id
        
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        metadata = plan.get('metadata', {})
        rooms = plan.get('rooms', {})
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'status': metadata.get('status', 'unknown'),
            'total_students': metadata.get('total_students', 0),
            'allocated_count': metadata.get('allocated_count', 0),
            'room_count': len(rooms),
            'finalized_at': metadata.get('finalized_at'),
            'rooms_summary': {
                'count': len(rooms),
                'names': list(rooms.keys()) if rooms else []
            }
        }), 200
    
    except Exception as e:
        print(f"❌ Error fetching status: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
