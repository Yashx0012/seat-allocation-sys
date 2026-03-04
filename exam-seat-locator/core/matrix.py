"""
core/matrix.py - Seat matrix construction.
Converts a flat student list + room config into a typed 2-D grid.
"""

import logging

logger = logging.getLogger(__name__)


def position_to_coordinates(position: str) -> tuple[int, int] | None:
    """
    Decode an alphanumeric position string into (row, col).
    Format: <ColLetter><RowNumber>  e.g. "A1" → (0, 0), "B3" → (2, 1)
      - Letter  (A, B, C …) = column index (A=0)
      - Number  (1, 2, 3 …) = row index    (1=0)
    """
    if not position or len(position) < 2:
        return None
    try:
        col = ord(position[0].upper()) - ord('A')
        row = int(position[1:]) - 1
        return (row, col)
    except (ValueError, IndexError):
        return None


def build_seat_matrix(room_config: dict, students: list) -> list[list]:
    """
    Build the 2-D seat matrix for a single room.

    Cell values:
      None                          → empty seat
      {"status": "broken"}          → broken / unavailable seat
      {"status": "allocated", …}    → occupied seat with full student metadata
    """
    rows = room_config.get("rows", 10)
    cols = room_config.get("cols", 10)

    # Initialise all cells as empty
    matrix: list[list] = [[None] * cols for _ in range(rows)]

    # Mark broken seats first so students can't overwrite them
    broken_set: set[tuple[int, int]] = set()
    for seat in room_config.get("broken_seats", []):
        r, c = seat[0], seat[1]
        if 0 <= r < rows and 0 <= c < cols:
            matrix[r][c] = {"status": "broken"}
            broken_set.add((r, c))

    # Place each student into the grid
    for student in students:
        position    = student.get("position", "")
        roll_number = student.get("roll_number", "")
        if not position or not roll_number:
            continue

        coords = position_to_coordinates(position)
        if coords is None:
            continue

        r, c = coords
        if 0 <= r < rows and 0 <= c < cols and (r, c) not in broken_set:
            matrix[r][c] = {
                "status":        "allocated",
                "roll_number":   roll_number,
                "paper_set":     student.get("paper_set", ""),
                "student_name":  student.get("student_name", ""),
                "batch_label":   student.get("batch_label", ""),
                "color":         student.get("color", ""),
                "is_broken":     student.get("is_broken", False),
                "is_unallocated":student.get("is_unallocated", False),
            }

    return matrix
