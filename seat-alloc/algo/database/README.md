# Database Layer

The `database/` directory handles all relational data persistence and retrieval using SQLite.

## Key Modules

- **[db.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/database/db.py)**: Manages SQLite connections. Provides a global `get_db_connection` utility for threading-safe access within Flask requests and standalone scripts.
- **[schema.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/database/schema.py)**: Defines the SQL tables, indices, and constraints. Includes initialization logic for fresh installations.
- **[queries/](file:///home/blazex/Documents/git/seat-allocation-sys/algo/database/queries/)**: Contains modular sub-modules for specialized queries (e.g., `student_queries.py`, `allocation_queries.py`) to keep the DB logic decoupled from services.

## Special Features
- **Foreign Key Enforcement**: Explicitly enabled to ensure data integrity across sessions, students, and allocations.
- **Row Factory**: Uses `sqlite3.Row` for dictionary-like access to query results.
