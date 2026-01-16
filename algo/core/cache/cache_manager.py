# Centralized cache management system.
# Handles saving, loading, and merging seating data snapshots (JSON) for active and finalized sessions.
import os
import json
import logging
import re

logger = logging.getLogger(__name__)
from enum import Enum
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Optional

# Determine cache directory
# Assuming this file is in algo/core/cache/
# and we want cache in algo/cache (to match original structure's relative path intent or explicitly set it)
# The original code used: CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache') 
# resulting in algo/cache/cache? No, original was in algo/cache_manager.py so algo/cache.
# Let's target the root 'algo/cache' to maintain existing data visibility or move it to algo/core/cache/data?
# Plan says: algo/core/cache/cache_manager.py.
# To preserve existing cache, we should point to the SAME directory: /home/blazex/Documents/git/seat-allocation-sys/algo/cache
# BASE_DIR calculation:
# file is in: algo/core/cache/cache_manager.py
# dirname: algo/core/cache
# ../../.. -> algo
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

class AlgoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum): return obj.value
        if is_dataclass(obj): return asdict(obj)
        if isinstance(obj, set): return list(obj)
        return super().default(obj)

class CacheManager:
    """
    FIXED: Supports multi-room persistence, unique room inputs, 
    and per-room raw_matrix storage for PDF generation.
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

    def save_or_update(self, plan_id, input_config, output_data, room_no="N/A"):
        """
        Special Logic: If the seating arrangement (students + positions) matches 
        an existing room exactly, we update the room name (M101 -> M102) 
        instead of creating a duplicate.
        """
        existing_data = self.load_snapshot(plan_id) or {}
        
        # 1. Process seating for the incoming room
        seating_matrix = output_data.get('seating', [])
        all_seats = [seat for row in seating_matrix for seat in row 
                     if seat and not seat.get('is_broken') and not seat.get('is_unallocated')]

        # Create the Room-specific batch structure
        room_batches = {}
        # We'll use this to compare if seating is identical (Position + Roll Number)
        current_fingerprint = [] 

        for student in all_seats:
            label = student.get('batch_label', 'Unknown')
            if label not in room_batches:
                academic_info = self._parse_enrollment(student.get('roll_number'))
                room_batches[label] = {"info": academic_info, "students": []}
            
            student['room_no'] = room_no
            room_batches[label]["students"].append(student)
            
            # Create a unique fingerprint of this seat (Pos + Roll)
            current_fingerprint.append(f"{student.get('position')}:{student.get('roll_number')}")

        current_fingerprint.sort() # Sort to ensure consistent comparison

        # 4. Prepare the entry for this room
        current_room_entry = {
            "batches": room_batches,
            "student_count": len(all_seats),
            "raw_matrix": seating_matrix,
            "inputs": {
                "rows": input_config.get('rows'),
                "cols": input_config.get('cols'),
                "block_width": input_config.get('block_width'),
                "broken_seats": input_config.get('broken_seats')
            }
        }

        # 5. Merge Logic (Always keeps multiple rooms, strictly appends or updates if name matches)
        if existing_data and "rooms" in existing_data:
            # Add/Update the specific room entry
            existing_data["rooms"][room_no] = current_room_entry
            existing_data["metadata"]["latest_room"] = room_no
            existing_data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Recalculate global totals
            total = sum(r.get('student_count', 0) for r in existing_data["rooms"].values())
            existing_data["metadata"]["total_students"] = total
            
            # Update room configurations list
            if "room_configs" not in existing_data["inputs"]:
                existing_data["inputs"]["room_configs"] = {}
            existing_data["inputs"]["room_configs"][room_no] = current_room_entry["inputs"]
            
            payload = existing_data
        else:
            # Standard first-time payload
            payload = {
                "metadata": {
                    "plan_id": plan_id,
                    "latest_room": room_no,
                    "last_updated": datetime.now().isoformat(),
                    "total_students": len(all_seats),
                    "type": "multi_room_snapshot"
                },
                "inputs": {**input_config, "room_configs": {room_no: current_room_entry["inputs"]}},
                "rooms": {room_no: current_room_entry}
            }
        
        # 6. Save
        file_path = self.get_file_path(plan_id)
        with open(file_path, 'w') as f:
            json.dump(payload, f, indent=4, cls=AlgoEncoder)
            
        logger.info(f"✅ Updated cache: {os.path.basename(file_path)}")
        return plan_id

    def load_snapshot(self, plan_id, silent=False):
        """Load saved snapshot"""
        file_path = self.get_file_path(plan_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    if not silent:
                        logger.info(f"🔍 [L1-CACHE] Checking cache for plan: {plan_id}")
                    data = json.load(f)
                    
                    # Log hit if successful
                    if not silent:
                        room_report = data.get('metadata', {}).get('latest_room') or data.get('inputs', {}).get('room_no', 'Unknown')
                        logger.info(f"⚡ [L1-CACHE HIT] Seating loaded from cache (room: {room_report})")
                    return data
            except Exception:
                return None
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
        if not os.path.exists(CACHE_DIR): return []
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CACHE_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        snapshots.append({
                            'plan_id': data['metadata']['plan_id'],
                            'room_no': data['metadata'].get('latest_room', 'N/A'),
                            'last_updated': data['metadata']['last_updated'],
                            'total_students': data['metadata']['total_students'],
                            'rooms': list(data.get('rooms', {}).keys())
                        })
                except:
                    continue
        return snapshots
    
    # ==================================================
    # TO REMOVE EXTERIMENTAL ROOMS FROM CACHE 
    # ==================================================
    def finalize_rooms(self, plan_id, finalized_room_list):
        """
        Prune cache to keep only finalized rooms with allocated students.
        Removes all experimental/unused rooms that were generated during testing.
        
        Args:
            plan_id: The plan ID to finalize
            finalized_room_list: List of room names (keys) that should be kept
        
        Returns:
            True if successful, False otherwise
        """
        if not plan_id or not finalized_room_list:
            return False
        
        data = self.load_snapshot(plan_id)
        if not data or "rooms" not in data:
            return False
        
        # Safety check: if we have no finalized rooms but snapshot has rooms, don't delete
        if not finalized_room_list and data.get("rooms"):
            return False
        
        # 1. Filter the 'rooms' object - Keep ONLY the finalized names
        # Explicitly rebuild to exclude any keys not in finalized_room_list
        original_rooms = data["rooms"]
        data["rooms"] = {}
        
        for room_name in finalized_room_list:
            if room_name in original_rooms:
                data["rooms"][room_name] = original_rooms[room_name]
        
        # 2. Filter the 'room_configs' in inputs - same explicit rebuild
        if "inputs" in data:
            original_configs = data["inputs"].get("room_configs", {})
            data["inputs"]["room_configs"] = {}
            
            for room_name in finalized_room_list:
                if room_name in original_configs:
                    data["inputs"]["room_configs"][room_name] = original_configs[room_name]
            
            # Update the primary room pointer to first finalized room
            if finalized_room_list:
                data["inputs"]["room_no"] = finalized_room_list[0]

        # 3. Update Global Metadata
        data["metadata"]["active_rooms"] = list(data["rooms"].keys())
        data["metadata"]["total_students"] = sum(
            r.get('student_count', 0) for r in data["rooms"].values()
        )
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        data["metadata"]["status"] = "FINALIZED"

        # 4. Save the cleaned file
        file_path = self.get_file_path(plan_id)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4, cls=AlgoEncoder)
        
        return True
    
    # ==================================================
    # CACHE SEARCH - Find by configuration
    # ==================================================

    
    # ==================================================
    # CACHE INFO - Get statistics
    # ==================================================
    def get_cache_stats(self) -> dict:
        """Get comprehensive cache statistics"""
        snapshots = self.list_snapshots()
        
        total_students = sum(s.get('total_students', 0) for s in snapshots)
        total_rooms = sum(len(s.get('rooms', [])) for s in snapshots)
        
        # Calculate cache disk size
        cache_size_bytes = 0
        if os.path.exists(CACHE_DIR):
            for file in os.listdir(CACHE_DIR):
                filepath = os.path.join(CACHE_DIR, file)
                if os.path.isfile(filepath):
                    cache_size_bytes += os.path.getsize(filepath)
        
        return {
            'total_plans': len(snapshots),
            'total_students_cached': total_students,
            'total_rooms': total_rooms,
            'cache_size_mb': round(cache_size_bytes / (1024 * 1024), 2),
            'avg_students_per_plan': round(total_students / len(snapshots), 1) if snapshots else 0,
            'avg_rooms_per_plan': round(total_rooms / len(snapshots), 1) if snapshots else 0
        }
