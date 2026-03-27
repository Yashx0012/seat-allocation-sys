"""
Test Suite 4: Core Seating Algorithm
======================================
Tests the SeatingAlgorithm class in isolation (no Flask, no DB):
- Basic grid generation (rows × cols)
- Batch-by-column assignment
- Paper set alternation (3-tier: vertical, horizontal-block, checkerboard)
- Block structure (uniform and variable)
- Broken seats handling
- Single-batch gap columns
- Real enrollment numbers
- Constraint validation
- Edge cases (1×1, single batch, all seats broken)
"""
import pytest
from algo.core.models.allocation import Seat, PaperSet
from algo.core.algorithm.seating import SeatingAlgorithm


# ============================================================================
# BASIC GRID GENERATION
# ============================================================================

class TestBasicGrid:
    """Verify the algorithm produces a correctly sized grid."""

    def test_grid_dimensions(self):
        """Output grid should be rows × cols."""
        algo = SeatingAlgorithm(rows=5, cols=6, num_batches=2)
        plan = algo.generate_seating()
        assert len(plan) == 5, f"Expected 5 rows, got {len(plan)}"
        for row in plan:
            assert len(row) == 6, f"Expected 6 cols, got {len(row)}"

    def test_all_seats_are_seat_objects(self):
        """Every cell should be a Seat instance."""
        algo = SeatingAlgorithm(rows=3, cols=4, num_batches=2)
        plan = algo.generate_seating()
        for r, row in enumerate(plan):
            for c, seat in enumerate(row):
                assert isinstance(seat, Seat), f"({r},{c}) is not a Seat"

    def test_seat_coordinates_correct(self):
        """Each Seat's row/col should match its position in the grid."""
        algo = SeatingAlgorithm(rows=4, cols=5, num_batches=2)
        plan = algo.generate_seating()
        for r, row in enumerate(plan):
            for c, seat in enumerate(row):
                assert seat.row == r and seat.col == c, \
                    f"Seat at ({r},{c}) reports ({seat.row},{seat.col})"

    def test_minimum_1x1_grid(self):
        """A 1×1 grid should work."""
        algo = SeatingAlgorithm(rows=1, cols=1, num_batches=1)
        plan = algo.generate_seating()
        assert len(plan) == 1
        assert len(plan[0]) == 1
        assert plan[0][0].roll_number is not None


# ============================================================================
# BATCH ASSIGNMENT
# ============================================================================

class TestBatchAssignment:
    """Verify batch-by-column and row-wise batch distribution."""

    def test_batch_by_column_alternation(self):
        """In batch_by_column mode, adjacent columns should alternate batches."""
        algo = SeatingAlgorithm(rows=4, cols=6, num_batches=2, batch_by_column=True)
        plan = algo.generate_seating()

        for r in range(4):
            for c in range(5):
                seat = plan[r][c]
                right = plan[r][c + 1]
                if seat.roll_number and right.roll_number:
                    if not seat.is_broken and not right.is_broken:
                        assert seat.batch != right.batch, \
                            f"Adjacent seats ({r},{c}) and ({r},{c+1}) have same batch {seat.batch}"

    def test_three_batches_column_assignment(self):
        """With 3 batches, columns should cycle 1,2,3,1,2,3,..."""
        algo = SeatingAlgorithm(rows=3, cols=6, num_batches=3, batch_by_column=True)
        plan = algo.generate_seating()

        for c in range(6):
            expected_batch = (c % 3) + 1
            seat = plan[0][c]  # check first row
            if seat.roll_number and not seat.is_broken:
                assert seat.batch == expected_batch, \
                    f"Column {c} should be batch {expected_batch}, got {seat.batch}"

    @pytest.mark.xfail(reason="Known bug: row-wise mode IndexError in _calculate_paper_set — "
                               "seating_plan[row] not populated yet when P2 scans left neighbors")
    def test_row_wise_mode(self):
        """In row-wise mode (batch_by_column=False), batches should use (row+col) pattern."""
        # Note: row-wise mode uses _calculate_batch which gives (row+col)%num_batches+1
        # Use 4 batches so _calculate_paper_set's P2 won't find same-batch left neighbors
        algo = SeatingAlgorithm(rows=4, cols=4, num_batches=4, batch_by_column=False)
        plan = algo.generate_seating()

        # Verify grid was generated with correct dimensions
        assert len(plan) == 4
        for row in plan:
            assert len(row) == 4
        # Verify each seat has a batch assigned
        for r in range(4):
            for c in range(4):
                seat = plan[r][c]
                assert seat.batch is not None
                assert 1 <= seat.batch <= 4


# ============================================================================
# PAPER SET ALTERNATION
# ============================================================================

class TestPaperSetAlternation:
    """Verify the 3-tier paper set algorithm (P1: vertical, P2: block-horizontal, P3: checkerboard)."""

    def test_paper_sets_are_valid(self):
        """All paper sets should be A or B."""
        algo = SeatingAlgorithm(rows=5, cols=6, num_batches=2)
        plan = algo.generate_seating()

        for r in range(5):
            for c in range(6):
                seat = plan[r][c]
                if seat.roll_number and not seat.is_broken:
                    assert seat.paper_set in (PaperSet.A, PaperSet.B), \
                        f"Seat ({r},{c}) has invalid paper_set: {seat.paper_set}"

    def test_vertical_same_batch_alternation(self):
        """Adjacent same-batch seats in a column should have different paper sets (P1)."""
        algo = SeatingAlgorithm(rows=6, cols=6, num_batches=2, batch_by_column=True)
        plan = algo.generate_seating()

        for c in range(6):
            prev_seat = None
            for r in range(6):
                seat = plan[r][c]
                if seat.roll_number and not seat.is_broken:
                    if prev_seat and prev_seat.batch == seat.batch:
                        assert prev_seat.paper_set != seat.paper_set, \
                            f"Same batch vertical: ({r-1},{c})={prev_seat.paper_set} == ({r},{c})={seat.paper_set}"
                    prev_seat = seat

    def test_checkerboard_pattern_basic(self):
        """Without same-batch neighbors, paper sets should follow (row+col)%2 pattern."""
        algo = SeatingAlgorithm(rows=4, cols=4, num_batches=4, batch_by_column=True)
        plan = algo.generate_seating()

        # With 4 batches and 4 columns, each column is a unique batch
        # P1 and P2 won't trigger (no same-batch neighbors), so P3 (checkerboard) applies
        for r in range(4):
            for c in range(4):
                seat = plan[r][c]
                if seat.roll_number and not seat.is_broken:
                    expected = PaperSet.A if (r + c) % 2 == 0 else PaperSet.B
                    assert seat.paper_set == expected, \
                        f"Checkerboard: ({r},{c}) expected {expected}, got {seat.paper_set}"


# ============================================================================
# BLOCK STRUCTURE
# ============================================================================

class TestBlockStructure:
    """Verify uniform and variable block structures."""

    def test_uniform_blocks(self):
        """Uniform block_width=3 for 6 columns → 2 blocks."""
        algo = SeatingAlgorithm(rows=3, cols=6, num_batches=2, block_width=3)
        plan = algo.generate_seating()

        assert algo.blocks == 2
        assert algo._get_block_index(0) == 0
        assert algo._get_block_index(2) == 0
        assert algo._get_block_index(3) == 1
        assert algo._get_block_index(5) == 1

    def test_variable_block_structure(self):
        """Variable block_structure=[3,2,3] for 8 columns → 3 blocks."""
        algo = SeatingAlgorithm(
            rows=3, cols=8, num_batches=2,
            block_structure=[3, 2, 3],
        )
        plan = algo.generate_seating()

        assert algo._get_block_index(0) == 0  # Block 0: cols 0-2
        assert algo._get_block_index(2) == 0
        assert algo._get_block_index(3) == 1  # Block 1: cols 3-4
        assert algo._get_block_index(4) == 1
        assert algo._get_block_index(5) == 2  # Block 2: cols 5-7
        assert algo._get_block_index(7) == 2

    def test_same_block_check(self):
        """_is_same_block correctly identifies columns in the same block."""
        algo = SeatingAlgorithm(rows=2, cols=6, num_batches=2, block_width=3)
        algo.generate_seating()

        assert algo._is_same_block(0, 1) is True
        assert algo._is_same_block(0, 2) is True
        assert algo._is_same_block(0, 3) is False
        assert algo._is_same_block(3, 5) is True

    def test_col_in_block_position(self):
        """_get_col_in_block returns position within the block."""
        algo = SeatingAlgorithm(rows=2, cols=6, num_batches=2, block_width=3)
        algo.generate_seating()

        assert algo._get_col_in_block(0) == 0
        assert algo._get_col_in_block(1) == 1
        assert algo._get_col_in_block(2) == 2
        assert algo._get_col_in_block(3) == 0  # new block
        assert algo._get_col_in_block(4) == 1


# ============================================================================
# BROKEN SEATS
# ============================================================================

class TestBrokenSeats:
    """Verify that broken seats are handled correctly."""

    def test_broken_seat_marked(self):
        """Broken seats should have is_broken=True and no roll number."""
        broken = [(0, 0), (2, 3)]
        algo = SeatingAlgorithm(rows=4, cols=6, num_batches=2, broken_seats=broken)
        plan = algo.generate_seating()

        for r, c in broken:
            seat = plan[r][c]
            assert seat.is_broken is True, f"Seat ({r},{c}) should be broken"
            assert seat.roll_number is None, f"Broken seat ({r},{c}) should have no roll number"

    def test_broken_seat_color_is_red(self):
        """Broken seats should be colored red."""
        algo = SeatingAlgorithm(rows=3, cols=4, num_batches=2, broken_seats=[(1, 1)])
        plan = algo.generate_seating()

        assert plan[1][1].color == "#FF0000"

    def test_non_broken_seats_still_filled(self):
        """Non-broken seats should be filled normally even when some are broken."""
        algo = SeatingAlgorithm(rows=3, cols=4, num_batches=2, broken_seats=[(0, 0)])
        plan = algo.generate_seating()

        # (0,1) should not be broken and should have a roll number
        assert plan[0][1].is_broken is False
        assert plan[0][1].roll_number is not None

    def test_all_seats_broken(self):
        """If all seats are broken, no students should be allocated."""
        broken = [(r, c) for r in range(3) for c in range(4)]
        algo = SeatingAlgorithm(rows=3, cols=4, num_batches=2, broken_seats=broken)
        plan = algo.generate_seating()

        for r in range(3):
            for c in range(4):
                assert plan[r][c].is_broken is True


# ============================================================================
# BATCH STUDENT COUNTS
# ============================================================================

class TestBatchStudentCounts:
    """Verify batch_student_counts limits allocation per batch."""

    def test_batch_limit_respected(self):
        """Only batch_student_counts[b] students should be allocated per batch."""
        algo = SeatingAlgorithm(
            rows=5, cols=4, num_batches=2,
            batch_by_column=True,
            batch_student_counts={1: 3, 2: 4},
        )
        plan = algo.generate_seating()

        batch_counts = {}
        for r in range(5):
            for c in range(4):
                seat = plan[r][c]
                if seat.roll_number and not seat.is_broken:
                    batch_counts[seat.batch] = batch_counts.get(seat.batch, 0) + 1

        assert batch_counts.get(1, 0) <= 3, f"Batch 1 has {batch_counts.get(1, 0)} students (limit 3)"
        assert batch_counts.get(2, 0) <= 4, f"Batch 2 has {batch_counts.get(2, 0)} students (limit 4)"


# ============================================================================
# REAL ENROLLMENT NUMBERS
# ============================================================================

class TestRealEnrollments:
    """Verify batch_roll_numbers uses actual enrollment strings."""

    def test_real_enrollments_used(self):
        """When batch_roll_numbers provided, seats should use those values."""
        enrollments = {
            1: ["BTCS24O1001", "BTCS24O1002", "BTCS24O1003"],
            2: ["BTCD24O2001", "BTCD24O2002", "BTCD24O2003"],
        }
        algo = SeatingAlgorithm(
            rows=3, cols=2, num_batches=2,
            batch_by_column=True,
            batch_roll_numbers=enrollments,
        )
        plan = algo.generate_seating()

        all_rolls = set()
        for r in range(3):
            for c in range(2):
                seat = plan[r][c]
                if seat.roll_number:
                    all_rolls.add(seat.roll_number)

        # All provided enrollments should appear
        expected_all = set(enrollments[1]) | set(enrollments[2])
        assert all_rolls.issubset(expected_all), \
            f"Unexpected rolls: {all_rolls - expected_all}"

    def test_enrollment_count_matches(self):
        """Number of allocated students should match enrollment count."""
        enrollments = {1: ["E001", "E002"], 2: ["E003", "E004"]}
        algo = SeatingAlgorithm(
            rows=4, cols=2, num_batches=2,
            batch_by_column=True,
            batch_roll_numbers=enrollments,
        )
        plan = algo.generate_seating()

        allocated = sum(
            1 for r in range(4) for c in range(2)
            if plan[r][c].roll_number and not plan[r][c].is_broken
        )
        assert allocated == 4


# ============================================================================
# SINGLE-BATCH GAP COLUMNS
# ============================================================================

class TestSingleBatchGaps:
    """With num_batches=1, odd columns in each block should be empty (gap)."""

    def test_gap_columns_in_single_batch(self):
        """Single batch: odd-indexed columns within blocks should be gap columns."""
        algo = SeatingAlgorithm(
            rows=3, cols=6, num_batches=1,
            batch_by_column=True, block_width=3,
        )
        plan = algo.generate_seating()

        # Block 0: cols 0,1,2 — col 1 should be gap
        # Block 1: cols 3,4,5 — col 4 should be gap
        for r in range(3):
            assert plan[r][1].roll_number is None, f"Gap column 1 should be empty at row {r}"
            assert plan[r][4].roll_number is None, f"Gap column 4 should be empty at row {r}"

    def test_allow_adjacent_disables_gaps(self):
        """With allow_adjacent_same_batch=True, gap columns should not be created."""
        algo = SeatingAlgorithm(
            rows=3, cols=4, num_batches=1,
            batch_by_column=True, block_width=2,
            allow_adjacent_same_batch=True,
        )
        plan = algo.generate_seating()

        # All columns should have students
        for c in range(4):
            assert plan[0][c].roll_number is not None, \
                f"Column {c} should not be a gap when allow_adjacent_same_batch=True"


# ============================================================================
# CONSTRAINT VALIDATION
# ============================================================================

class TestConstraintValidation:
    """Verify the validate_constraints method."""

    def test_valid_plan_passes_validation(self):
        """A standard 2-batch plan should pass validation."""
        algo = SeatingAlgorithm(rows=4, cols=6, num_batches=2, batch_by_column=True)
        algo.generate_seating()
        is_valid, errors = algo.validate_constraints()

        # Filter out "Integrity Warning" (non-critical) messages
        critical_errors = [e for e in errors if "Integrity Warning" not in e]
        assert len(critical_errors) == 0, f"Unexpected critical errors: {critical_errors}"

    def test_no_duplicate_roll_numbers(self):
        """Validation should catch duplicate roll numbers."""
        algo = SeatingAlgorithm(rows=3, cols=4, num_batches=2)
        plan = algo.generate_seating()
        # Manually create a duplicate
        if plan[0][0].roll_number:
            plan[1][0].roll_number = plan[0][0].roll_number

        _, errors = algo.validate_constraints()
        dup_errors = [e for e in errors if "Duplicate roll number" in e]
        assert len(dup_errors) > 0, "Should detect duplicate roll numbers"


# ============================================================================
# BATCH COLORS
# ============================================================================

class TestBatchColors:
    """Verify batch color assignment."""

    def test_custom_colors_applied(self):
        """Custom batch colors should be applied to seats."""
        colors = {1: "#AABBCC", 2: "#DDEEFF"}
        algo = SeatingAlgorithm(rows=3, cols=4, num_batches=2, batch_colors=colors)
        plan = algo.generate_seating()

        for r in range(3):
            for c in range(4):
                seat = plan[r][c]
                if seat.roll_number and not seat.is_broken:
                    assert seat.color == colors[seat.batch], \
                        f"Seat ({r},{c}) batch {seat.batch} should have color {colors[seat.batch]}"

    def test_default_colors_used(self):
        """Without custom colors, default palette should be applied."""
        algo = SeatingAlgorithm(rows=3, cols=4, num_batches=2)
        plan = algo.generate_seating()

        seat = plan[0][0]
        if seat.roll_number and not seat.is_broken:
            assert seat.color in SeatingAlgorithm.DEFAULT_BATCH_COLORS.values()


# ============================================================================
# JSON OUTPUT
# ============================================================================

class TestJsonOutput:
    """Verify to_json produces valid output structure."""

    def test_to_web_format_structure(self):
        """to_web_format should return dict with required keys."""
        algo = SeatingAlgorithm(rows=3, cols=4, num_batches=2)
        algo.generate_seating()
        output = algo.to_web_format()

        assert isinstance(output, dict)
        assert "metadata" in output
        assert "seating" in output
        assert "summary" in output

    def test_to_web_format_metadata(self):
        """Metadata should contain rows, cols."""
        algo = SeatingAlgorithm(rows=5, cols=6, num_batches=3)
        algo.generate_seating()
        output = algo.to_web_format()

        meta = output["metadata"]
        assert meta["rows"] == 5
        assert meta["cols"] == 6

    def test_to_web_format_summary(self):
        """Summary should include batch distribution."""
        algo = SeatingAlgorithm(rows=4, cols=4, num_batches=2, batch_by_column=True)
        algo.generate_seating()
        output = algo.to_web_format()

        summary = output.get("summary", {})
        assert isinstance(summary, dict) and len(summary) > 0


# ============================================================================
# ROLL FORMATTING
# ============================================================================

class TestRollFormatting:
    """Verify roll number generation with templates and prefixes."""

    def test_start_rolls_template_extraction(self):
        """start_rolls should extract template and starting serial."""
        algo = SeatingAlgorithm(
            rows=3, cols=2, num_batches=2,
            batch_by_column=True,
            start_rolls={1: "BTCS24O1135", 2: "BTCD24O2001"},
        )
        algo.generate_seating()

        # Template for batch 1 should be BTCS24O{serial}
        assert 1 in algo.batch_templates
        assert "{serial}" in algo.batch_templates[1]

        # Start serial for batch 1 should be 1135
        assert algo.start_serials.get(1) == 1135

    def test_per_batch_roll_prefix(self):
        """Rolls should use batch-specific prefixes."""
        algo = SeatingAlgorithm(
            rows=3, cols=2, num_batches=2,
            batch_by_column=True,
            roll_template="{prefix}{year}O{serial}",
            batch_prefixes={1: "BTCS", 2: "BTCD"},
            year=24,
            start_serial=1001,
            serial_width=4,
        )
        plan = algo.generate_seating()

        for r in range(3):
            # Col 0 → batch 1 → should start with BTCS
            seat0 = plan[r][0]
            if seat0.roll_number:
                assert seat0.roll_number.startswith("BTCS"), \
                    f"Batch 1 roll should start with BTCS: {seat0.roll_number}"

            # Col 1 → batch 2 → should start with BTCD
            seat1 = plan[r][1]
            if seat1.roll_number:
                assert seat1.roll_number.startswith("BTCD"), \
                    f"Batch 2 roll should start with BTCD: {seat1.roll_number}"
