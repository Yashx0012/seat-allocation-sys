# Core Logic Module

The `core/` directory contains the fundamental algorithmic and data management components of the system. This is the application's engine.

## Key Modules

### [Algorithm](file:///home/blazex/Documents/git/seat-allocation-sys/algo/core/algorithm/seating.py)
- **Primary Function**: The `SeatingAlgorithm` class implements complex logic to arrange students based on batch constraints, column-major filling, and paper set alternation.
- **Features**: Supports broken seat avoidance, block boundaries, and custom batch coloring.

### [Cache](file:///home/blazex/Documents/git/seat-allocation-sys/algo/core/cache/cache_manager.py)
- **Primary Function**: The `CacheManager` provides a manual "Snapshot" system for active seating plans.
- **Necessity**: Enables high-performance PDF generation without re-running the algorithm.
- **Experimental Workflow**: Supports saving multiple room plans within a single session-bound file (`PLAN-<session_id>.json`) and prunes unfinalized data upon session completion.

## Architecture
- **Stateless Algorithm**: The algorithm itself is stateless; it takes configuration and returns a structured plan.
- **Persistence Layer**: The CacheManager acts as a fast-access bridge between memory and the relational database.
