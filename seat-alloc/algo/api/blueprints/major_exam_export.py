"""
Major Exam Export Blueprint
Handles Excel and other format exports
"""
from flask import Blueprint, request, jsonify, send_file
import io
import pandas as pd
from datetime import datetime

from algo.services.auth_service import token_required
from algo.core.cache.major_exam_cache import get_major_cache_manager

major_exam_export_bp = Blueprint('major_exam_export', __name__, url_prefix='/api/major-exam')

cache_manager = get_major_cache_manager()


def generate_excel_export(plan_data: dict) -> bytes:
    """Generate Excel file with student data"""
    try:
        output = io.BytesIO()
        
        students = plan_data.get('students', [])
        df = pd.DataFrame(students)
        
        # Write to Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Students', index=False)
            
            # Add summary sheet
            metadata = plan_data.get('metadata', {})
            summary_data = {
                'Metric': [
                    'Total Students',
                    'Allocated',
                    'Room Count',
                    'Status',
                    'Created At'
                ],
                'Value': [
                    metadata.get('total_students', 0),
                    metadata.get('allocated_count', 0),
                    metadata.get('room_count', 0),
                    metadata.get('status', 'pending'),
                    plan_data.get('created_at', '')
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    except Exception as e:
        print(f"❌ Error generating Excel: {e}")
        return None


@major_exam_export_bp.route('/download/excel/<plan_id>', methods=['GET'])
@token_required
def download_excel(plan_id):
    """Download student data as Excel"""
    try:
        user_id = request.user_id
        
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        excel_data = generate_excel_export(plan)
        if not excel_data:
            return jsonify({'error': 'Failed to generate Excel file'}), 500
        
        return send_file(
            io.BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'major_exam_{plan_id}_students.xlsx'
        )
    
    except Exception as e:
        print(f"❌ Error downloading Excel: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_export_bp.route('/download/json/<plan_id>', methods=['GET'])
@token_required
def download_json(plan_id):
    """Download plan as JSON"""
    try:
        user_id = request.user_id
        
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        # Prepare response
        response_data = io.BytesIO()
        import json
        json_str = json.dumps(plan, indent=2, default=str)
        response_data.write(json_str.encode())
        response_data.seek(0)
        
        return send_file(
            response_data,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'major_exam_{plan_id}.json'
        )
    
    except Exception as e:
        print(f"❌ Error downloading JSON: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
