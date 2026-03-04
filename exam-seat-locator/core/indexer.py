"""
core/indexer.py - Index construction layer.
Converts a list of room sessions into O(1)-lookup dictionaries.
"""

import logging

logger = logging.getLogger(__name__)


def build_indexes(
    sessions: list[tuple[str, dict]],
) -> tuple[dict, dict]:
    """
    Build two in-memory indexes from a list of (room_name, session) tuples.

    Returns
    -------
    session_index : dict
        (exam_date, start_time, end_time, room_name) → session

    student_index : dict
        (enrollment, exam_date, start_time, end_time) → {
            room, session, row, col
        }
    """
    session_index: dict = {}
    student_index: dict = {}

    for room_name, session in sessions:
        exam_date  = session["exam_date"]
        start_time = session["start_time"]
        end_time   = session["end_time"]

        # Index 1 — keyed by (date, start, end, room)
        session_key = (exam_date, start_time, end_time, room_name)
        session_index[session_key] = session

        # Index 2 — keyed by (enrollment, date, start, end) for O(1) lookup
        for row_idx, row in enumerate(session.get("seats", [])):
            for col_idx, cell in enumerate(row):
                if (
                    cell
                    and isinstance(cell, dict)
                    and cell.get("status") == "allocated"
                ):
                    enrollment = cell.get("roll_number")
                    if enrollment:
                        student_key = (enrollment, exam_date, start_time, end_time)
                        student_index[student_key] = {
                            "room":    room_name,
                            "session": session,
                            "row":     row_idx,
                            "col":     col_idx,
                        }

    logger.info(f"INDEX  sessions={len(session_index)} students={len(student_index)}")
    return session_index, student_index
