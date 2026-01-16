# API Layer (Blueprints)

The `api/` directory manages the RESTful communication between the frontend and the backend services. It is organized into Flask Blueprints for clean separation of concerns.

## Key Modules

- **[admin.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/api/blueprints/admin.py)**: Administrative controls, user authentication (JWT/OAuth), and bulk DB operations.
- **[allocations.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/api/blueprints/allocations.py)**: Orchestrates seating generation requests and manual cache interactions.
- **[classrooms.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/api/blueprints/classrooms.py)**: CRUD operations for classroom configurations and broken seat management.
- **[dashboard.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/api/blueprints/dashboard.py)**: Provides aggregated statistics and overview data for the management UI.
- **[sessions.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/api/blueprints/sessions.py)**: Manages allocation session lifecycles, heartbeats, and finalization logic.
- **[students.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/api/blueprints/students.py)**: Handles file uploads and persistence of student/batch data.
- **[pdf.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/api/blueprints/pdf.py)**: Endpoints for generating and downloading PDF reports and attendance sheets.

## Connections
- **Frontend**: Consumes these endpoints via HTTP/JSON.
- **Services**: All blueprints call their corresponding service in `algo/services/` to execute business logic.
- **Auth Service**: Integrated into most blueprints via the `@token_required` decorator.
