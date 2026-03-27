import sys
import os

# Add root directory to path
sys.path.append('/home/blazex/Documents/git/seat-allocation-sys')

from algo.core.algorithm.seating import SeatingAlgorithm

def debug_multi_batch():
    rows = 8
    cols = 10
    block_width = 2
    num_batches = 2
    batch_labels = {1: "csd", 2: "cse"}
    batch_student_counts = {1: 40, 2: 40}
    
    algo = SeatingAlgorithm(
        rows=rows,
        cols=cols,
        num_batches=num_batches,
        block_width=block_width,
        batch_by_column=True,
        batch_student_counts=batch_student_counts,
        batch_labels=batch_labels
    )
    
    algo.generate_seating()
    
    print("Row 0 Snapshot:")
    for c in range(cols):
        s = algo.seating_plan[0][c]
        print(f"Col {c}: Batch {s.batch} Set {s.paper_set}")

if __name__ == "__main__":
    debug_multi_batch()
