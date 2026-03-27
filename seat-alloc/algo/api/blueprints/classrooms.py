# Classroom management endpoints.
# Handles CRUD operations for rooms and their specific row/column/broken-seat configurations.
from flask import Blueprint, request, jsonify
import sqlite3
import json
from algo.config.settings import Config
from algo.database.db import get_db_connection
from algo.services.auth_service import token_required

classrooms_bp = Blueprint('classrooms', __name__, url_prefix='/api/classrooms')


def auto_convert_block_structure(classroom: dict) -> dict:
    """
    Auto-convert block_width to block_structure on read if block_structure is null.
    This ensures backwards compatibility with existing classrooms.
    
    Example: block_width=3, cols=9 → block_structure=[3,3,3]
             block_width=2, cols=5 → block_structure=[2,2,1]
    """
    result = dict(classroom)
    cols = result.get('cols', 1)
    block_structure_raw = result.get('block_structure')
    
    # Parse existing block_structure if it's a JSON string
    if block_structure_raw:
        if isinstance(block_structure_raw, str):
            try:
                result['block_structure'] = json.loads(block_structure_raw)
            except json.JSONDecodeError:
                result['block_structure'] = None
        elif isinstance(block_structure_raw, list):
            result['block_structure'] = block_structure_raw
    
    # Auto-generate from block_width if not set
    if not result.get('block_structure'):
        block_width = result.get('block_width', 2)
        structure = []
        remaining = cols
        while remaining > 0:
            width = min(block_width, remaining)
            structure.append(width)
            remaining -= width
        result['block_structure'] = structure
    
    return result


def validate_block_structure(block_structure: list, cols: int) -> tuple:
    """
    Validate that block_structure is valid and sums to cols.
    Returns (is_valid, error_message)
    """
    if not isinstance(block_structure, list):
        return False, "block_structure must be an array"
    
    if len(block_structure) == 0:
        return False, "block_structure cannot be empty"
    
    for i, width in enumerate(block_structure):
        if not isinstance(width, int) or width < 1:
            return False, f"Block {i+1} width must be a positive integer"
    
    total = sum(block_structure)
    if total != cols:
        return False, f"Block widths sum to {total}, but classroom has {cols} columns"
    
    return True, None


@classrooms_bp.route('', methods=['GET'])
@token_required
def get_classrooms():
    """List classrooms for current user + unassigned classrooms"""
    try:
        user_id = getattr(request, 'user_id', None)
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get user's classrooms AND unassigned classrooms (user_id IS NULL)
        # This ensures existing classrooms created before user isolation are still visible
        cur.execute("""
            SELECT * FROM classrooms 
            WHERE user_id = ? OR user_id IS NULL
            ORDER BY name ASC
        """, (user_id,))
        rows = cur.fetchall()
        
        # Apply auto-conversion for each classroom
        classrooms = [auto_convert_block_structure(dict(row)) for row in rows]
        conn.close()
        
        # Return array directly (legacy compatible)
        return jsonify(classrooms), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@classrooms_bp.route('', methods=['POST'])
@token_required
def add_classroom():
    """Add a new classroom for current user"""
    user_id = getattr(request, 'user_id', None)
    
    data = request.json
    name = data.get('name')
    rows = data.get('rows')
    cols = data.get('cols')
    
    if not all([name, rows, cols]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if user already has a classroom with this name
        cur.execute("SELECT id FROM classrooms WHERE user_id = ? AND name = ?", (user_id, name))
        if cur.fetchone():
            conn.close()
            return jsonify({"status": "error", "message": "You already have a classroom with this name"}), 400
        
        # broken_seats handling
        broken = data.get('broken_seats', [])
        if isinstance(broken, list):
             broken_str = json.dumps(broken)
        else:
             broken_str = str(broken)
        
        # Handle block_structure
        block_structure = data.get('block_structure')
        block_structure_str = None
        block_width = data.get('block_width', 2)
        
        if block_structure:
            # Validate block_structure
            is_valid, error_msg = validate_block_structure(block_structure, cols)
            if not is_valid:
                return jsonify({"status": "error", "message": error_msg}), 400
            block_structure_str = json.dumps(block_structure)
            # Use first block's width as the legacy block_width
            block_width = block_structure[0] if block_structure else 2
             
        cur.execute("""
            INSERT INTO classrooms (user_id, name, rows, cols, broken_seats, block_width, block_structure)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, rows, cols, broken_str, block_width, block_structure_str))
        
        cid = cur.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "id": cid, "message": "Classroom added"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Classroom name exists"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@classrooms_bp.route('/<int:room_id>', methods=['DELETE'])
@token_required
def delete_classroom(room_id):
    """Delete a classroom (only if user owns it or it's unassigned)"""
    user_id = getattr(request, 'user_id', None)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check ownership before deleting - allow if user owns it OR it's unassigned
        cur.execute("SELECT user_id, name FROM classrooms WHERE id = ?", (room_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"status": "error", "message": "Classroom not found"}), 404
        
        owner_id = row[0]
        if owner_id is not None and owner_id != user_id:
            conn.close()
            return jsonify({"status": "error", "message": "Access denied - you do not own this classroom"}), 403
        
        cur.execute("DELETE FROM classrooms WHERE id = ?", (room_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Update Blueprint
@classrooms_bp.route('/<int:room_id>', methods=['PUT'])
@token_required
def update_classroom(room_id):
    """Update a classroom (only if user owns it or it's unassigned)"""
    user_id = getattr(request, 'user_id', None)
    data = request.json
    
    try:
         conn = get_db_connection()
         conn.row_factory = sqlite3.Row
         cur = conn.cursor()
         
         # Get current classroom to check ownership and know cols for validation
         cur.execute("SELECT user_id, cols FROM classrooms WHERE id = ?", (room_id,))
         existing = cur.fetchone()
         if not existing:
             conn.close()
             return jsonify({"status": "error", "message": "Classroom not found"}), 404
         
         # Check ownership - allow if user owns it OR it's unassigned (NULL)
         owner_id = existing['user_id']
         if owner_id is not None and owner_id != user_id:
             conn.close()
             return jsonify({"status": "error", "message": "Access denied - you do not own this classroom"}), 403
         
         # If unassigned, claim it for this user
         if owner_id is None:
             cur.execute("UPDATE classrooms SET user_id = ? WHERE id = ?", (user_id, room_id))
             print(f"📝 Classroom {room_id} claimed by user {user_id}")
         
         # Use new cols value if provided, otherwise use existing
         target_cols = data.get('cols', existing['cols'])
         
         # Fields to update
         fields = []
         values = []
         
         if 'name' in data:
             fields.append("name = ?")
             values.append(data['name'])
         if 'rows' in data:
             fields.append("rows = ?")
             values.append(data['rows'])
         if 'cols' in data:
             fields.append("cols = ?")
             values.append(data['cols'])
         if 'broken_seats' in data:
             broken = data['broken_seats']
             bs_str = json.dumps(broken) if isinstance(broken, list) else str(broken)
             fields.append("broken_seats = ?")
             values.append(bs_str)
         if 'block_width' in data:
             fields.append("block_width = ?")
             values.append(data['block_width'])
         
         # Handle block_structure
         if 'block_structure' in data:
             block_structure = data['block_structure']
             if block_structure:
                 is_valid, error_msg = validate_block_structure(block_structure, target_cols)
                 if not is_valid:
                     conn.close()
                     return jsonify({"status": "error", "message": error_msg}), 400
                 fields.append("block_structure = ?")
                 values.append(json.dumps(block_structure))
                 # Also update legacy block_width to first block's width
                 if 'block_width' not in data:
                     fields.append("block_width = ?")
                     values.append(block_structure[0])
             else:
                 # Setting to null clears the custom structure
                 fields.append("block_structure = ?")
                 values.append(None)
             
         values.append(room_id)
         
         query = f"UPDATE classrooms SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
         cur.execute(query, values)
         conn.commit()
         conn.close()
         
         return jsonify({"status": "success", "message": "Updated"}), 200
    except Exception as e:
         return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# ROUTE: POST /api/classrooms/claim-unassigned
# ============================================================================
@classrooms_bp.route('/claim-unassigned', methods=['POST'])
@token_required
def claim_unassigned_classrooms():
    """Claim all unassigned classrooms for current user"""
    user_id = getattr(request, 'user_id', None)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Update all unassigned classrooms to current user
        cur.execute("""
            UPDATE classrooms 
            SET user_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id IS NULL
        """, (user_id,))
        
        claimed_count = cur.rowcount
        conn.commit()
        conn.close()
        
        print(f"📝 User {user_id} claimed {claimed_count} unassigned classroom(s)")
        
        return jsonify({
            "status": "success",
            "message": f"Claimed {claimed_count} classroom(s)",
            "claimed_count": claimed_count
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
