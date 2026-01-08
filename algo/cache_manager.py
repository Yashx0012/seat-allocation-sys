import os
import json
import re
from enum import Enum
from dataclasses import asdict, is_dataclass
from datetime import datetime

CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

class AlgoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum): return obj.value
        if is_dataclass(obj): return asdict(obj)
        if isinstance(obj, set): return list(obj)
        return super().default(obj)

class CacheManager:
    """
    SIMPLIFIED: Focus on snapshot storage for PDF/Attendance generation
    No aggressive session caching - that's handled by DB directly
    """
    
    def get_file_path(self, plan_id):
        safe_id = "".join([c for c in str(plan_id) if c.isalnum() or c in ('-', '_')])
        return os.path.join(CACHE_DIR, f"{safe_id}.json")

    def _parse_enrollment(self, roll_no):
        """Extract academic info from enrollment number"""
        match = re.match(r"([A-Z]{2})([A-Z]{2})(\d{2})", str(roll_no))
        if match:
            deg_code, branch_code, year_short = match.groups()
            degree_map = {"BT": "B.Tech", "MT": "M.Tech", "BC": "B.C.A"}
            return {
                "degree": degree_map.get(deg_code, deg_code),
                "branch": branch_code,
                "joining_year": f"20{year_short}"
            }
        return {"degree": "B.Tech", "branch": "N/A", "joining_year": "2024"}

    def save_or_update(self, plan_id, input_config, output_data):
        """
        Save allocation snapshot for PDF/attendance generation
        This is the ONLY file-based cache we need
        """
        # Flatten seating
        all_seats = [seat for row in output_data.get('seating', []) for seat in row 
                     if seat and not seat.get('is_broken') and not seat.get('is_unallocated')]

        # Extract structured batches
        batches = {}
        for student in all_seats:
            label = student.get('batch_label', 'Unknown')
            if label not in batches:
                academic_info = self._parse_enrollment(student.get('roll_number'))
                batches[label] = {
                    "info": academic_info,
                    "students": []
                }
            batches[label]["students"].append(student)

        # Sort students within batches
        for label in batches:
            batches[label]["students"].sort(key=lambda x: x.get('roll_number', ''))

        payload = {
            "metadata": {
                "plan_id": plan_id,
                "last_updated": datetime.now().isoformat(),
                "total_students": len(all_seats),
                "type": "structured_seating_snapshot"
            },
            "inputs": input_config,
            "batches": batches,
            "raw_matrix": output_data.get('seating')
        }
        
        file_path = self.get_file_path(plan_id)
        with open(file_path, 'w') as f:
            json.dump(payload, f, indent=4, cls=AlgoEncoder)
        return plan_id

    def load_snapshot(self, plan_id):
        """Load saved snapshot"""
        file_path = self.get_file_path(plan_id)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None

    def delete_snapshot(self, plan_id):
        """Delete a snapshot"""
        file_path = self.get_file_path(plan_id)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def list_snapshots(self):
        """List all cached snapshots"""
        snapshots = []
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CACHE_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        snapshots.append({
                            'plan_id': data['metadata']['plan_id'],
                            'last_updated': data['metadata']['last_updated'],
                            'total_students': data['metadata']['total_students']
                        })
                except:
                    continue
        return snapshots

    def cleanup_old_snapshots(self, days=30):
        """Remove snapshots older than X days"""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted = 0
        
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CACHE_DIR, filename)
                if os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    deleted += 1
        
        return deleted