import sys
import os

# Add root directory to path
sys.path.append('/home/blazex/Documents/git/seat-allocation-sys')

from algo.core.algorithm.seating import SeatingAlgorithm
from algo.core.models.allocation import PaperSet

def test_paper_set_alternation():
    # CASE 1: Horizontal alternation across blocks (num_batches=1, block_width=2)
    print("--- Testing CASE 1: Horizontal Across Blocks ---")
    rows = 1
    cols = 4
    block_width = 2
    num_batches = 1
    
    algo = SeatingAlgorithm(
        rows=rows,
        cols=cols,
        num_batches=num_batches,
        block_width=block_width,
        batch_by_column=True,
        batch_student_counts={1: 10}
    )
    
    plan = algo.generate_seating()
    
    # Col 0 (Block 0) and Col 2 (Block 1) are same batch (1)
    s0 = plan[0][0]
    s2 = plan[0][2]
    
    print(f"Col 0 Seat: Batch={s0.batch}, Set={s0.paper_set}")
    print(f"Col 2 Seat: Batch={s2.batch}, Set={s2.paper_set}")
    
    if s0.batch == s2.batch and s0.paper_set == s2.paper_set:
        print("❌ Horizontal fail: Col 0 and Col 2 have same batch and SAME set across blocks.")
    else:
        print("✅ Horizontal pass: Sets alternate correctly across blocks.")

    # CASE 2: Vertical alternation with broken seat gap
    print("\n--- Testing CASE 2: Vertical with Broken Seat ---")
    rows = 4
    cols = 1
    block_width = 1
    num_batches = 1
    broken_seats = [(1, 0)] # Row 1 is broken
    
    algo = SeatingAlgorithm(
        rows=rows,
        cols=cols,
        num_batches=num_batches,
        block_width=block_width,
        batch_by_column=True,
        broken_seats=broken_seats,
        batch_student_counts={1: 10}
    )
    
    plan = algo.generate_seating()
    
    # Row 0 and Row 2 are student neighbors (skipping Row 1 broken)
    r0 = plan[0][0]
    r1 = plan[1][0]
    r2 = plan[2][0]
    
    print(f"Row 0 Seat: Batch={r0.batch}, Set={r0.paper_set}")
    print(f"Row 1 Seat: Broken={r1.is_broken}")
    print(f"Row 2 Seat: Batch={r2.batch}, Set={r2.paper_set}")
    
    if r0.batch == r2.batch and r0.paper_set == r2.paper_set:
        print("❌ Vertical fail: Row 0 and Row 2 have same batch and SAME set skipping broken seat.")
    else:
        print("✅ Vertical pass: Sets alternate correctly skipping broken seat.")

if __name__ == "__main__":
    test_paper_set_alternation()
