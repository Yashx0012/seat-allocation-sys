"""
Major Exam Allocation Blueprint
Sequential branch-aware room allocation.
Each room gets assigned branches; students are allocated in enrollment order
with no student reuse across rooms.
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from algo.services.auth_service import token_required
from algo.core.cache.major_exam_cache import get_major_cache_manager

major_exam_allocation_bp = Blueprint('major_exam_allocation', __name__, url_prefix='/api/major-exam')
cache_manager = get_major_cache_manager()
logger = logging.getLogger(__name__)


def allocate_branches_to_rooms(branches_data: dict, rooms_config: list) -> dict:
    """
    Sequential branch-aware room allocation.
    
    Args:
        branches_data: { "CSE": [student_dicts...], "CSD": [student_dicts...] }
        rooms_config: [ { "name": "Lab 104", "capacity": 50, "branches": ["CSE", "CSD"] } ]
    
    Returns:
        { "rooms": [...], "total_allocated": int }
    
    Logic:
        - For each room, divide capacity among assigned branches (equal split)
        - Allocate students sequentially from each branch (enrollment order)
        - Global pointer per branch — once allocated, a student is never reused
        - If a branch has fewer remaining students than its share, 
          the extra capacity goes unused (no overflow from other branches)
    """
    if not branches_data or not rooms_config:
        return None
    
    # Global pointers: track how many students from each branch have been allocated
    branch_pointers = {branch: 0 for branch in branches_data}
    
    rooms_result = []
    total_allocated = 0
    
    for room_cfg in rooms_config:
        room_name = room_cfg['name']
        capacity = int(room_cfg['capacity'])
        assigned_branches = room_cfg.get('branches', [])
        
        if not assigned_branches:
            continue
        
        # Calculate capacity share per branch
        num_branches = len(assigned_branches)
        base_share = capacity // num_branches
        remainder = capacity % num_branches
        
        room_students = []
        branch_allocations = {}
        
        for idx, branch_name in enumerate(assigned_branches):
            if branch_name not in branches_data:
                continue
            
            all_branch_students = branches_data[branch_name]
            pointer = branch_pointers[branch_name]
            
            # This branch's share of the room capacity
            share = base_share + (1 if idx < remainder else 0)
            
            # How many students remain in this branch
            remaining = len(all_branch_students) - pointer
            actual_count = min(share, remaining)
            
            if actual_count <= 0:
                continue
            
            # Slice the students for this room
            allocated = all_branch_students[pointer:pointer + actual_count]
            
            # Advance the global pointer
            branch_pointers[branch_name] = pointer + actual_count
            
            # Get enrollment range
            enrollments = [s['enrollment'] for s in allocated if s.get('enrollment')]
            from_roll = enrollments[0] if enrollments else ''
            to_roll = enrollments[-1] if enrollments else ''
            
            branch_allocations[branch_name] = {
                'students': allocated,
                'count': len(allocated),
                'from_roll': from_roll,
                'to_roll': to_roll
            }
            
            room_students.extend(allocated)
        
        if room_students:
            rooms_result.append({
                'room_name': room_name,
                'capacity': capacity,
                'total_students': len(room_students),
                'students': room_students,
                'branch_allocations': branch_allocations
            })
            total_allocated += len(room_students)
    
    if not rooms_result:
        return None
    
    return {
        'rooms': rooms_result,
        'total_allocated': total_allocated
    }


@major_exam_allocation_bp.route('/allocate/<plan_id>', methods=['POST'])
@token_required
def allocate_plan(plan_id):
    """
    Re-run allocation on an existing plan (if rooms_config exists).
    Mostly used internally; the primary flow uses /configure-rooms.
    """
    try:
        user_id = request.user_id
        
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        branches_data = plan.get('branches', {})
        rooms_config = plan.get('rooms_config', [])
        
        if not branches_data:
            return jsonify({'error': 'No branch data in plan'}), 400
        
        if not rooms_config:
            return jsonify({'error': 'No room configuration. Use /configure-rooms first.'}), 400
        
        result = allocate_branches_to_rooms(branches_data, rooms_config)
        if not result:
            return jsonify({'error': 'Allocation failed'}), 500
        
        # Update plan
        plan['rooms'] = result['rooms']
        plan['metadata']['status'] = 'FINALIZED'
        plan['metadata']['room_count'] = len(result['rooms'])
        plan['metadata']['allocated_count'] = result['total_allocated']
        plan['metadata']['finalized_at'] = datetime.utcnow().isoformat() + 'Z'
        
        cache_manager.store_plan(user_id, plan_id, plan)
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'status': 'FINALIZED',
            'total_allocated': result['total_allocated'],
            'rooms_count': len(result['rooms']),
            'message': f'Allocated {result["total_allocated"]} students across {len(result["rooms"])} rooms'
        }), 200
    
    except Exception as e:
        logger.error(f"Allocation error: {e}", exc_info=True)
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
        rooms = plan.get('rooms', [])
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'status': metadata.get('status', 'unknown'),
            'total_students': metadata.get('total_students', 0),
            'allocated_count': metadata.get('allocated_count', 0),
            'room_count': len(rooms),
            'branch_names': metadata.get('branch_names', []),
            'branch_counts': metadata.get('branch_counts', {}),
            'finalized_at': metadata.get('finalized_at'),
            'rooms_summary': [
                {
                    'name': r.get('room_name', ''),
                    'total': r.get('total_students', 0),
                    'branches': list(r.get('branch_allocations', {}).keys())
                }
                for r in rooms
            ]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
