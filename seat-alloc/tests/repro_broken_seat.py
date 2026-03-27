import sys
import os

# Add root directory to path
sys.path.append('/home/blazex/Documents/git/seat-allocation-sys')

from algo.core.algorithm.seating import SeatingAlgorithm

def test_broken_seat_repro():
    # Input from user
    rows = 8
    cols = 10
    block_width = 2
    num_batches = 1
    broken_seats = [(2, 4), (3, 3), (5, 2), (1, 9), (4, 6)]
    
    print(f"Initializing SeatingAlgorithm with rows={rows}, cols={cols}, num_batches={num_batches}, block_width={block_width}")
    print(f"Broken seats (0-indexed): {broken_seats}")
    
    algo = SeatingAlgorithm(
        rows=rows,
        cols=cols,
        num_batches=num_batches,
        block_width=block_width,
        batch_by_column=True,
        broken_seats=broken_seats,
        batch_student_counts={1: 10}
    )
    
    print("\nGenerating seating...")
    algo.generate_seating()
    
    print("\nChecking constraints...")
    status = algo.get_constraints_status()
    
    broken_seats_handling = next(c for c in status['constraints'] if c['name'] == "Broken Seats Handling")
    print(f"Broken Seats Handling: applied={broken_seats_handling['applied']}, satisfied={broken_seats_handling['satisfied']}")
    
    if not broken_seats_handling['satisfied']:
        print("\n❌ BUG REPRODUCED: Broken seats are not respected!")
        
        # Identify which broken seats are not respected
        for r, c in broken_seats:
            seat = algo.seating_plan[r][c]
            if not seat.is_broken:
                print(f"  Broken seat at ({r}, {c}) is NOT marked as broken! Roll: {seat.roll_number}")
    else:
        print("\n✅ Bug NOT reproduced. Constraints satisfied.")

if __name__ == "__main__":
    test_broken_seat_repro()
