# Seat Allocation System - Backend

This directory contains the core logic, API endpoints, and services for the Seat Allocation System. The backend is built with Flask and follows a modular architecture designed for scalability and maintainability.

## Directory Structure

- **[api/](file:///home/blazex/Documents/git/seat-allocation-sys/algo/api/)**: Contains Flask blueprints and API routing logic.
- **[core/](file:///home/blazex/Documents/git/seat-allocation-sys/algo/core/)**: The "brain" of the application, housing the seating algorithm and cache management.
- **[database/](file:///home/blazex/Documents/git/seat-allocation-sys/algo/database/)**: Database schema, initializations, and modular query handlers.
- **[services/](file:///home/blazex/Documents/git/seat-allocation-sys/algo/services/)**: Business logic layer that orchestrates operations between APIs and the core/database layers.
- **[utils/](file:///home/blazex/Documents/git/seat-allocation-sys/algo/utils/)**: General-purpose utilities and parsing logic (e.g., Excel/CSV parsing).
- **[pdf_gen/](file:///home/blazex/Documents/git/seat-allocation-sys/algo/pdf_gen/)**: Specialized modules for generating PDF reports, seating vectors, and attendance sheets.
- **[config/](file:///home/blazex/Documents/git/seat-allocation-sys/algo/config/)**: Centralized configuration management and environment settings.

## Core Features

- **Automated Seating Algorithm**: Intelligent placement with batch constraints and paper set alternation.
- **Hybrid Caching System**: Session-specific manual caching for high performance and "experimental" seating workflows.
- **Modular API**: RESTful endpoints for classrooms, students, sessions, and report generation.
- **Extensive Reporting**: Generation of PDF seating plans, vectors, and attendance sheets.

## Architecture & Flow

The system follows a standard service-oriented pattern:
1. **Request** enters through **API Blueprints**.
2. **Blueprints** call the appropriate **Service**.
3. **Services** interact with the **Core** logic (Algorithm/Cache) or the **Database**.
4. **Result** is returned to the user or cached for subsequent operations.
