# Logic for managing student allocations and persisting them to the database.
# Orchestrates the seating algorithm and handles the conversion between models and database records.
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from algo.config.settings import Config
from algo.database.queries.session_queries import SessionQueries
from algo.database.queries.student_queries import StudentQueries
from algo.database.queries.allocation_queries import AllocationQueries
from algo.core.algorithm.seating import SeatingAlgorithm
from algo.core.models.allocation import Seat, PaperSet
from algo.core.cache.cache_manager import CacheManager
from algo.utils.helpers import parse_str_dict, parse_int_dict

logger = logging.getLogger(__name__)


class AllocationService:
    """
    Seating allocation orchestration service.
    
    Handles all allocation-related business logic including:
    - Algorithm execution and configuration
    - Constraint validation
    - Allocation storage and retrieval
    - Cache management for generated plans
    
    Usage:
        from algo.services import AllocationService
        
        # Generate allocation for a classroom
        result = AllocationService.allocate_classroom(
            session_id=5,
            classroom={'id': 3, 'name': 'Room 101', 'rows': 6, 'cols': 8},
            student_distribution={1: 20, 2: 15},
            student_roll_numbers={1: ['BTCS24O1001', ...], 2: [...]}
        )
    """

    @staticmethod
    def allocate_classroom(
        session_id: int, 
        classroom: Dict[str, Any], 
        student_distribution: Dict,
        student_roll_numbers: Dict[str, List[str]] = None,
        allow_adjacent_same_batch: bool = False
    ) -> Dict[str, Any]:
        """
        Run the seating algorithm for a specific classroom.
        
        Args:
            session_id: ID of the current session
            classroom: Classroom config (id, name, rows, cols, broken_seats, etc.)
            student_distribution: Dict mapping batch_id -> count_to_allocate
            student_roll_numbers: Optional dict of batch_id -> list of roll numbers (if assigning specific students)
            
        Returns:
            Dict containing the allocation result
        """
        # 0. Fetch Session
        session = SessionQueries.get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # 1. Prepare Algorithm Inputs
        rows = int(classroom.get('rows', 1))
        cols = int(classroom.get('cols', 1))
        
        # Convert broken seats from JSON string if needed, or list of tuples
        broken_seats_raw = classroom.get('broken_seats', [])
        broken_seats = []
        if isinstance(broken_seats_raw, str):
            try:
                # Expecting JSON list of [row, col]
                bs_list = json.loads(broken_seats_raw)
                broken_seats = [tuple(x) for x in bs_list]
            except Exception:
                logger.warning(f"Failed to parse broken_seats: {broken_seats_raw}")
        elif isinstance(broken_seats_raw, list):
             broken_seats = [tuple(x) for x in broken_seats_raw]
        
        batch_ids = list(student_distribution.keys())
        num_batches = len(batch_ids)
        
        # We need to map batch indices (1..N) to internal batch IDs or Names
        # The algorithm expects 1..N indices.
        # We will create a mapping: Algo Index -> Batch Info
        batch_map = {} # index -> batch_id
        batch_counts = {} # index -> count
        batch_colors = {} # index -> color
        batch_labels = {} # index -> name
        
        # Fetch batch details to get colors/names
        # Optimziation: fetch all batch info for this session once, but here we query as needed or pass in
        # We can query batch info from DB based on batch_ids found in distribution
        # For now, let's assume we fetch all info
        
        all_batches = StudentQueries.get_batch_counts(session_id) # Returns [{batch_name, count, color}, ...]
        # This returns grouped by Name, but we deal with Upload generated Batch IDs ideally?
        # The current DB schema uses batch_id in uploads/students.
        # Let's map batch_id -> details
        
        # Wait, student_distribution keys are likely batch *names* or *ids*?
        # In the original app, it seems to pass batch names or IDs.
        # Let's assume input keys are what we need to identify the batch.
        
        # Mapping by Name as per original app logic usually
        # Let's reconstruct consistent mapping
        
        # 2. Get Student Data for allocation
        # We need actual student records if we are assigning by name/roll
        # If specific students are provided in student_roll_numbers, usage is clear.
        # Otherwise, we might just be doing a count-based simulation or fetching next available.
        
        # For this refactor, let's stick to the logic:
        # We need to feed the algo with:
        # - batch_student_counts: {1: 30, 2: 25}
        # - batch_roll_numbers: {1: ["A1", "A2"], 2: ...} (Optional)
        
        idx = 1
        algo_input_rolls = {}
        
        for batch_key, count in student_distribution.items():
             # batch_key could be batch name
             # Find batch details
             # We need color and name
             matching_batch = next((b for b in all_batches if b['batch_name'] == batch_key), None)
             color = matching_batch['color'] if matching_batch else "#CCCCCC"
             
             batch_map[idx] = batch_key
             batch_counts[idx] = count
             batch_colors[idx] = color
             batch_labels[idx] = batch_key
             
             if student_roll_numbers and batch_key in student_roll_numbers:
                 algo_input_rolls[idx] = student_roll_numbers[batch_key]
                 
             idx += 1
        
        # Get block_structure from classroom (auto-converted on read)
        block_structure = classroom.get('block_structure')
        block_width = int(classroom.get('block_width', 2))
             
        # 3. Instantiate Algorithm
        algo = SeatingAlgorithm(
            rows=rows,
            cols=cols,
            num_batches=num_batches,
            block_width=block_width,
            block_structure=block_structure,  # NEW: Variable block widths
            broken_seats=broken_seats,
            batch_student_counts=batch_counts,
            batch_colors=batch_colors,
            batch_labels=batch_labels,
            batch_roll_numbers=algo_input_rolls,
            allow_adjacent_same_batch=allow_adjacent_same_batch
        )
        
        # 4. Run Generation
        try:
            seating_plan = algo.generate_seating()
            stats = algo.get_statistics()
        except Exception as e:
            logger.error(f"Algorithm failed: {e}")
            raise
            
        # 5. Format Output
        # Convert Seat objects to dicts
        json_plan = []
        students_to_allocate = []
        
        for r in range(rows):
            row_data = []
            for c in range(cols):
                seat: Seat = seating_plan[r][c]
                seat_dict = None
                if seat:
                    seat_dict = {
                        "row": seat.row,
                        "col": seat.col,
                        "status": "allocated" if seat.batch else "available",
                        "batch": seat.batch,
                        "batch_label": batch_labels.get(seat.batch) if seat.batch else None,
                        "roll_number": seat.roll_number,
                        "student_name": seat.student_name,
                        "paper_set": seat.paper_set if isinstance(seat.paper_set, str) else (seat.paper_set.value if seat.paper_set else None),
                        "color": seat.color,
                        "is_broken": seat.is_broken,
                        "block": seat.block
                    }
                    
                    # Prepare for DB persistence
                    if seat.batch and seat.roll_number:
                        # Find student ID by enrollment/roll to link correctly?
                        # Or just store text if we don't have strict foreign keys yet?
                        # DB schema requires student_id.
                        # We need to lookup student_id by enrollment + batch?
                        # This implies we fetched students earlier.
                        # For now, let's create the record tuple for bulk insert later
                        # (session_id, classroom_id, student_id, enrollment, seat_pos, batch_name, paper_set)
                        
                        # Optimization: We need to know WHICH student ID maps to this roll.
                        # Logic:
                        # 1. Get all allocatable students for this session & batch
                        # 2. Match roll numbers
                        pass
                        
                row_data.append(seat_dict)
            json_plan.append(row_data)

        # 6. Save to Cache (for PDF Gen and Session Persistence)
        # Using CacheManager
        cache_mgr = CacheManager()
        
        # room_config for cache
        input_config = {
            "rows": rows,
            "cols": cols,
            "block_width": classroom.get('block_width', 2),
            "broken_seats": broken_seats
        }
        
        output_data = {
            "seating": json_plan,
            "stats": stats
        }
        
        room_name = classroom.get('name', 'Unknown')
        
        # Check if plan_id exists on session, if not create logic usually handled by session creation
        plan_id = session.get('plan_id')
        
        cache_mgr.save_or_update(plan_id, input_config, output_data, room_no=room_name)
        
        return {
            "seating": json_plan,
            "stats": stats,
            "plan_id": plan_id
        }

    @staticmethod
    def save_allocations_to_db(session_id: int, classroom_id: int, seating_plan: List[List[Dict]]):
        """
        Persist the allocation results to the relational DB.
        This requires resolving student IDs from enrollments.
        """
        # Fetch all students for this session once to create a lookup map
        # enrollment -> student_id
        # Note: Enrollments should be unique within a session ideally, or at least (batch, enrollment)
        
        all_students = StudentQueries.get_students_by_session(session_id)
        enrollment_map = {s['enrollment']: s['id'] for s in all_students}
        
        allocations_to_insert = []
        
        for row in seating_plan:
            for seat in row:
                if seat and seat.get('status') == 'allocated' and seat.get('roll_number'):
                    enrollment = seat['roll_number']
                    student_id = enrollment_map.get(enrollment)
                    
                    if student_id:
                        allocations_to_insert.append((
                            session_id,
                            classroom_id,
                            student_id,
                            enrollment,
                            f"{seat['row']},{seat['col']}",
                            seat['batch_label'],
                            seat['paper_set']
                        ))
                    else:
                        logger.warning(f"Student ID not found for allocated enrollment: {enrollment}")

        if allocations_to_insert:
            AllocationQueries.save_allocation_batch(allocations_to_insert)
            
            # Update session stats
            SessionService.update_stats(session_id)

    @staticmethod
    def reset_allocations(session_id: int):
        """Clear all allocations for a session"""
        AllocationQueries.clear_session_allocations(session_id)
        SessionService.update_stats(session_id)
        # Also clear cache?
        # The cache manager logic for deletion might be needed.
        session = SessionQueries.get_session_by_id(session_id)
        if session:
             CacheManager().delete_snapshot(session['plan_id'])

    @staticmethod
    def undo_last_allocation(session_id: int) -> Dict[str, Any]:
        """
        Undo the last room allocation for a session.
        
        Finds the most recent classroom allocation (via history or fallback to last modified),
        removes all allocations for that classroom, and updates session counts.
        
        Returns:
            Dict with success, message, classroom_name, students_restored
        """
        from algo.database.db import get_db
        db = get_db()
        
        try:
            # Try to find last allocation from history
            history_id = None
            target_classroom = None
            affected = 0
            
            try:
                cursor = db.execute("""
                    SELECT id, classroom_id, students_affected
                    FROM allocation_history
                    WHERE session_id = ? AND action_type = 'allocate'
                    ORDER BY step_number DESC LIMIT 1
                """, (session_id,))
                last_step = cursor.fetchone()
                
                if last_step:
                    history_id = last_step['id']
                    target_classroom = last_step['classroom_id']
                    affected = last_step['students_affected']
            except Exception:
                pass  # Table might not exist
            
            # Fallback: find last classroom with allocations
            if not target_classroom:
                cursor = db.execute("""
                    SELECT classroom_id, COUNT(*) as cnt
                    FROM allocations WHERE session_id = ?
                    GROUP BY classroom_id ORDER BY MAX(id) DESC LIMIT 1
                """, (session_id,))
                fallback = cursor.fetchone()
                
                if not fallback:
                    return {"success": False, "message": "Nothing to undo"}
                
                target_classroom = fallback['classroom_id']
                affected = fallback['cnt']
            
            # Get classroom name for message
            cursor = db.execute("SELECT name FROM classrooms WHERE id = ?", (target_classroom,))
            classroom_row = cursor.fetchone()
            classroom_name = classroom_row['name'] if classroom_row else f"Room {target_classroom}"
            
            # Delete allocations for that classroom
            cursor = db.execute("""
                DELETE FROM allocations WHERE session_id = ? AND classroom_id = ?
            """, (session_id, target_classroom))
            deleted = cursor.rowcount
            
            # Also delete any external students manually added to this room
            try:
                db.execute("""
                    DELETE FROM external_students 
                    WHERE session_id = ? AND room_no = ?
                """, (session_id, classroom_name))
                logger.info(f"Cleared external students for room {classroom_name}")
            except Exception as e:
                logger.warning(f"Could not clear external students: {e}")
            
            # Update session count
            db.execute("""
                UPDATE allocation_sessions
                SET allocated_count = MAX(0, allocated_count - ?), last_activity = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (deleted, session_id))
            
            # Remove history record if exists
            if history_id:
                try:
                    db.execute("DELETE FROM allocation_history WHERE id = ?", (history_id,))
                except:
                    pass
            
            db.commit()
            
            logger.info(f"Undid allocation for {classroom_name} ({deleted} students)")
            
            return {
                "success": True,
                "message": f"Undid allocation for {classroom_name} ({deleted} students)",
                "classroom_name": classroom_name,
                "students_restored": deleted
            }
            
        except Exception as e:
            logger.error(f"Error undoing allocation for session {session_id}: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def save_room_allocation(
        session_id: int,
        classroom_id: int,
        seating_data: Dict,
        selected_batch_names: List[str] = None
    ) -> Dict[str, Any]:
        """
        Save allocation for one room from seating matrix data.
        
        Args:
            session_id: Session ID
            classroom_id: Classroom ID  
            seating_data: Dict with 'seating' key containing 2D matrix
            selected_batch_names: Optional list of batch names to filter
            
        Returns:
            Dict with allocation result including updated session stats
        """
        from algo.database.db import get_db
        db = get_db()
        
        try:
            # Validate session
            cursor = db.execute("""
                SELECT session_id, plan_id, status, total_students, allocated_count
                FROM allocation_sessions WHERE session_id = ?
            """, (session_id,))
            session_row = cursor.fetchone()
            
            if not session_row:
                return {"success": False, "error": "Session not found"}
            
            if session_row['status'] != 'active':
                return {"success": False, "error": f"Session is {session_row['status']}, not active"}
            
            # Get classroom info
            cursor = db.execute("SELECT id, name, rows, cols FROM classrooms WHERE id = ?", (classroom_id,))
            classroom = cursor.fetchone()
            if not classroom:
                return {"success": False, "error": "Classroom not found"}
            
            # Process seating matrix
            seating_matrix = seating_data.get('seating', [])
            allocated_students = []
            
            # Bulk-fetch all pending students once → O(1) instead of O(seats) queries
            all_students = StudentQueries.get_students_by_session(session_id)
            already_allocated = set(AllocationQueries.get_allocated_student_ids(session_id))
            
            # Build enrollment → {id, batch_name} lookup for unallocated students only
            enrollment_map = {}
            for s in all_students:
                if s['id'] not in already_allocated:
                    enrollment_map[s['enrollment']] = {'id': s['id'], 'batch_name': s.get('batch_name')}
            
            for row_idx, row in enumerate(seating_matrix):
                if not isinstance(row, list):
                    continue
                for col_idx, seat in enumerate(row):
                    if not seat or seat.get('is_broken') or seat.get('is_unallocated'):
                        continue
                    
                    enrollment = seat.get('roll_number')
                    if not enrollment:
                        continue
                    
                    # Look up student from pre-fetched map
                    student_info = enrollment_map.get(enrollment)
                    
                    if student_info:
                        # Filter by batch if specified
                        if selected_batch_names and student_info['batch_name'] not in selected_batch_names:
                            continue
                        
                        # Insert allocation
                        db.execute("""
                            INSERT INTO allocations
                            (session_id, classroom_id, student_id, enrollment, seat_position, batch_name, paper_set)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            session_id, 
                            classroom_id, 
                            student_info['id'], 
                            enrollment,
                            f"{row_idx + 1}-{col_idx + 1}", 
                            student_info['batch_name'], 
                            seat.get('paper_set', 'A')
                        ))
                        
                        allocated_students.append(enrollment)
                        # Remove from map to prevent double-allocation within same save
                        del enrollment_map[enrollment]
            
            # Update session totals
            db.execute("""
                UPDATE allocation_sessions
                SET allocated_count = allocated_count + ?, last_activity = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (len(allocated_students), session_id))
            
            # Add to history (if table exists)
            try:
                cursor = db.execute("SELECT COALESCE(MAX(step_number), 0) + 1 FROM allocation_history WHERE session_id = ?", (session_id,))
                step_num = cursor.fetchone()[0]
                
                db.execute("""
                    INSERT INTO allocation_history (session_id, step_number, classroom_id, action_type, students_affected, created_at)
                    VALUES (?, ?, ?, 'allocate', ?, CURRENT_TIMESTAMP)
                """, (session_id, step_num, classroom_id, len(allocated_students)))
            except Exception:
                pass  # allocation_history table might not exist
            
            db.commit()
            
            # Get fresh totals
            cursor = db.execute("""
                SELECT total_students, allocated_count, plan_id 
                FROM allocation_sessions WHERE session_id = ?
            """, (session_id,))
            fresh = cursor.fetchone()
            
            # Get all allocated rooms
            allocated_rooms = AllocationQueries.get_allocated_rooms(session_id)
            
            fresh_total = fresh['total_students'] or 0
            fresh_allocated = fresh['allocated_count'] or 0
            fresh_pending = max(0, fresh_total - fresh_allocated)
            
            logger.info(f"Allocated {len(allocated_students)} students to {classroom['name']}")
            
            return {
                "success": True,
                "message": f"Allocated {len(allocated_students)} students to {classroom['name']}",
                "allocated_count": len(allocated_students),
                "remaining_count": fresh_pending,
                "session": {
                    "session_id": session_id,
                    "plan_id": fresh['plan_id'],
                    "total_students": fresh_total,
                    "allocated_count": fresh_allocated,
                    "pending_count": fresh_pending,
                    "allocated_rooms": allocated_rooms
                },
                "can_finalize": fresh_pending == 0
            }
            
        except Exception as e:
            logger.error(f"Error saving room allocation: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
