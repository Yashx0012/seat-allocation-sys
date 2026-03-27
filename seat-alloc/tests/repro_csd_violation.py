import sys
import os

# Add root directory to path
sys.path.append('/home/blazex/Documents/git/seat-allocation-sys')

from algo.core.algorithm.seating import SeatingAlgorithm
from algo.core.models.allocation import PaperSet

def test_csd_violation():
    # Input from user
    rows = 8
    cols = 10
    block_width = 2
    num_batches = 1
    broken_seats = [(2, 4), (3, 3), (5, 2), (1, 9), (4, 6)]
    batch_labels = {1: "csd"}
    batch_student_counts = {1: 93}
    
    print(f"Initializing SeatingAlgorithm for batch 'csd'...")
    
    algo = SeatingAlgorithm(
        rows=rows,
        cols=cols,
        num_batches=num_batches,
        block_width=block_width,
        batch_by_column=True,
        broken_seats=broken_seats,
        batch_student_counts=batch_student_counts,
        batch_labels=batch_labels
    )
    
    print("Generating seating...")
    algo.generate_seating()
    
    print("Validating constraints...")
    ok, errors = algo.validate_constraints()
    
    if not ok:
        print("❌ VALIDATION FAILED!")
        for err in errors:
            print(f"  {err}")
    else:
        print("✅ VALIDATION PASSED!")

    # Debug Row 2, Col 6 (which was reported as a violation)
    print("\n--- Row 2 Analytics ---")
    r = 2
    row_data = []
    for c in range(cols):
        seat = algo.seating_plan[r][c]
        status = "Student" if seat.roll_number else ("Broken" if seat.is_broken else "Empty/Gap")
        row_data.append(f"Col {c}: {status} (Set: {seat.paper_set})")
    
    for line in row_data:
        print(line)

if __name__ == "__main__":
    test_csd_violation()
