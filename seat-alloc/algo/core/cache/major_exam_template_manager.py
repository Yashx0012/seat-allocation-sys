"""
Major Exam Template Manager
Handles template storage and retrieval for major exam PDFs
Uses JSON-based cache, not database
"""
import json
import os
from datetime import datetime
from pathlib import Path


class MajorExamTemplateManager:
    """Manages user-specific templates for major exam PDFs"""
    
    def __init__(self, cache_dir='cache'):
        self.cache_dir = Path(cache_dir)
        self.templates_dir = self.cache_dir / 'major_templates'
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_user_template_path(self, user_id: str) -> Path:
        """Get path to user's template file"""
        user_file = self.templates_dir / f"{user_id}_template.json"
        return user_file
    
    def _get_default_template(self) -> dict:
        """Return default template structure"""
        return {
            # Major Exam Seating Plan Fields
            'major_exam_dept_name': 'Department of Computer Science & Engineering',
            'major_exam_heading': 'MAJOR EXAMINATION',
            'major_exam_title': 'Seating Plan - Major Examination',
            
            # Banner & Appearance
            'major_banner_path': '',  # User uploads custom banner
            'major_banner_filename': 'banner.png',
            
            # Coordinator Information
            'major_coordinator_name': 'Dr. Exam Coordinator',
            'major_coordinator_title': 'Dept. Exam Coordinator',
            'major_hod_name': 'Dr. Head of Department',
            'major_hod_title': 'Head of Department',
            
            # Metadata
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'updated_at': datetime.utcnow().isoformat() + 'Z',
            'template_name': 'default',
            'version': '1.0'
        }
    
    def get_user_template(self, user_id: str) -> dict:
        """Get user's template, fallback to default if not found"""
        try:
            template_path = self._get_user_template_path(user_id)
            
            if template_path.exists():
                with open(template_path, 'r') as f:
                    template = json.load(f)
                    # Ensure all required fields exist
                    default = self._get_default_template()
                    for key in default:
                        if key not in template:
                            template[key] = default[key]
                    return template
            else:
                return self._get_default_template()
        except Exception as e:
            print(f"❌ Error retrieving template for {user_id}: {e}")
            return self._get_default_template()
    
    def save_user_template(self, user_id: str, template_data: dict) -> bool:
        """Save user template"""
        try:
            template_path = self._get_user_template_path(user_id)
            
            # Ensure required fields
            required_fields = [
                'major_exam_dept_name',
                'major_exam_heading',
                'major_coordinator_name',
                'major_coordinator_title'
            ]
            
            for field in required_fields:
                if field not in template_data:
                    template_data[field] = self._get_default_template()[field]
            
            # Update metadata
            template_data['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            if 'created_at' not in template_data:
                template_data['created_at'] = datetime.utcnow().isoformat() + 'Z'
            
            with open(template_path, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Error saving template for {user_id}: {e}")
            return False
    
    def reset_to_default(self, user_id: str) -> bool:
        """Reset user template to default"""
        try:
            default = self._get_default_template()
            return self.save_user_template(user_id, default)
        except Exception as e:
            print(f"❌ Error resetting template: {e}")
            return False
    
    def delete_user_template(self, user_id: str) -> bool:
        """Delete user template"""
        try:
            template_path = self._get_user_template_path(user_id)
            if template_path.exists():
                template_path.unlink()
            return True
        except Exception as e:
            print(f"❌ Error deleting template: {e}")
            return False
