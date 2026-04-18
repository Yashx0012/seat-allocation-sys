"""
Major Exam Template Management Endpoints
Provides RESTful API for managing major exam PDF templates
"""
from flask import Blueprint, request, jsonify
from algo.services.auth_service import verify_token
from algo.core.cache.major_exam_template_manager import MajorExamTemplateManager
from functools import wraps, lru_cache

major_exam_template_bp = Blueprint('major_exam_template', __name__, url_prefix='/api/major-exam/template')
template_manager = MajorExamTemplateManager()


def login_required(f):
    """Decorator to check authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            user = verify_token(token)
            if not user:
                return jsonify({'error': 'Invalid token'}), 401
            
            request.user_id = user.get('user_id') or user.get('id')
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
    
    return decorated_function


@major_exam_template_bp.route('/config', methods=['GET'])
@login_required
def get_template_config():
    """
    GET /api/major-exam/template/config
    Retrieve user's major exam template configuration
    """
    try:
        user_id = request.user_id
        template = template_manager.get_user_template(user_id)
        
        return jsonify({
            'success': True,
            'template': template,
            'message': 'Template retrieved successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve template: {str(e)}'
        }), 500


@major_exam_template_bp.route('/config', methods=['POST'])
@login_required
def save_template_config():
    """
    POST /api/major-exam/template/config
    Save or update user's major exam template configuration
    
    Expected JSON:
    {
        "major_exam_dept_name": "...",
        "major_exam_heading": "...",
        "major_exam_title": "...",
        "major_banner_path": "...",
        "major_coordinator_name": "...",
        "major_coordinator_title": "...",
        "major_hod_name": "...",
        "major_hod_title": "..."
    }
    """
    try:
        user_id = request.user_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = [
            'major_exam_dept_name',
            'major_exam_heading',
            'major_coordinator_name',
            'major_coordinator_title'
        ]
        
        missing = [f for f in required_fields if f not in data or not data[f]]
        if missing:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        # Save template
        success = template_manager.save_user_template(user_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Template saved successfully',
                'template': template_manager.get_user_template(user_id)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save template'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to save template: {str(e)}'
        }), 500


@major_exam_template_bp.route('/config/reset', methods=['POST'])
@login_required
def reset_template():
    """
    POST /api/major-exam/template/config/reset
    Reset template to defaults
    """
    try:
        user_id = request.user_id
        success = template_manager.reset_to_default(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Template reset to defaults',
                'template': template_manager.get_user_template(user_id)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reset template'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to reset template: {str(e)}'
        }), 500


@major_exam_template_bp.route('/config', methods=['DELETE'])
@login_required
def delete_template():
    """
    DELETE /api/major-exam/template/config
    Delete user's template (will revert to defaults on next fetch)
    """
    try:
        user_id = request.user_id
        success = template_manager.delete_user_template(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Template deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete template'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete template: {str(e)}'
        }), 500
