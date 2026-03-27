import sys
import os

# Add root directory to path
sys.path.append('/home/blazex/Documents/git/seat-allocation-sys')

from algo.core.algorithm.seating import SeatingAlgorithm

def test_multi_batch_complex():
    # Attempting to reproduce the large error list provided by user
    # Rows=8, Cols=10, Block Width=2
    # Two batches: CSD (1) and CSE (2)
    rows = 8
    cols = 10
    block_width = 2
    num_batches = 2
    broken_seats = [(2, 4), (3, 3), (5, 2), (1, 9), (4, 6)]
    batch_labels = {1: "csd", 2: "cse"}
    batch_student_counts = {1: 40, 2: 40}
    
    print(f"--- Running Complex Multi-Batch Test ---")
    
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
    
    algo.generate_seating()
    ok, errors = algo.validate_constraints()
    
    if not ok:
        print(f"❌ VALIDATION FAILED with {len(errors)} errors")
        for err in errors[:15]:
            print(f"  {err}")
        if len(errors) > 15: print(f"  ... and {len(errors)-15} more")
    else:
        print("✅ VALIDATION PASSED! All multi-batch paper set constraints met.")

if __name__ == "__main__":
    test_multi_batch_complex()
