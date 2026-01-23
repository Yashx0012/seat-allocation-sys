# Core Logic Module

The `core/` directory contains the fundamental algorithmic and data management components of the system. This is the application's engine.

## Key Modules

- **Primary Function**: The `SeatingAlgorithm` class implements multi-constraint logic to arrange students following a **Sequence-Centric** model.
- **Features**: 
    - **Sequence-Strict Paper Sets**: Guarantees A-B-A-B alternation by treating students as a continuous sequence, strictly skipping broken seats and empty spaces.
    - **Collision Resolution**: Prioritizes physical adjacency (dist 1) in conflict cases to ensure no two side-by-side students ever share the same set.
    - **Pragmatic Validation**: Includes a dual-tier validator that distinguishes between critical Physical Errors and layout-forced Sequence Warnings.

### [Cache](file:///home/blazex/Documents/git/seat-allocation-sys/algo/core/cache/cache_manager.py)
- **Primary Function**: The `CacheManager` provides a manual "Snapshot" system for active seating plans.
- **Necessity**: Enables high-performance PDF generation without re-running the algorithm.
- **Experimental Workflow**: Supports saving multiple room plans within a single session-bound file (`PLAN-<session_id>.json`) and prunes unfinalized data upon session completion.

## Architecture
- **Stateless Algorithm**: The algorithm itself is stateless; it takes configuration and returns a structured plan.
- **Persistence Layer**: The CacheManager acts as a fast-access bridge between memory and the relational database.
