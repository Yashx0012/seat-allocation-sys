# Classroom management endpoints.
# Handles CRUD operations for rooms and their specific row/column/broken-seat configurations.
from flask import Blueprint, request, jsonify
import sqlite3
import json
from algo.config.settings import Config
from algo.database.db import get_db_connection
from algo.auth_service import token_required

classrooms_bp = Blueprint('classrooms', __name__, url_prefix='/api/classrooms')

@classrooms_bp.route('', methods=['GET'])
@token_required
def get_classrooms():
    """List all classrooms - returns array directly for frontend compatibility"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM classrooms ORDER BY name ASC")
        rows = cur.fetchall()
        
        classrooms = [dict(row) for row in rows]
        conn.close()
        
        # Return array directly (legacy compatible)
        return jsonify(classrooms), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@classrooms_bp.route('', methods=['POST'])
@token_required
def add_classroom():
    """Add a new classroom"""
    data = request.json
    name = data.get('name')
    rows = data.get('rows')
    cols = data.get('cols')
    
    if not all([name, rows, cols]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # broken_seats handling
        broken = data.get('broken_seats', [])
        if isinstance(broken, list):
             broken_str = json.dumps(broken)
        else:
             broken_str = str(broken)
             
        cur.execute("""
            INSERT INTO classrooms (name, rows, cols, broken_seats, block_width)
            VALUES (?, ?, ?, ?, ?)
        """, (name, rows, cols, broken_str, data.get('block_width', 2)))
        
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
    try:
        conn = get_db_connection()
        cur = conn.cursor()
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
    data = request.json
    try:
         conn = get_db_connection()
         cur = conn.cursor()
         
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
             
         values.append(room_id)
         
         query = f"UPDATE classrooms SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
         cur.execute(query, values)
         conn.commit()
         conn.close()
         
         return jsonify({"status": "success", "message": "Updated"}), 200
    except Exception as e:
         return jsonify({"status": "error", "message": str(e)}), 500
