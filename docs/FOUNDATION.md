# CyberLab: Phase 1.1 - Foundation Core

## Overview
This phase establishes the foundational backend structure for the CyberLab Education Platform. It strictly adheres to the approved Application Factory Pattern and Clean Architecture principles, ensuring scalability for future phases.

## Components

### 1. Application Factory (`core/app_factory.py`)
Replaces the standard global Flask instance with a `create_app()` function. This prevents circular dependencies, allows dynamic configuration swapping (e.g., Development vs. Testing), and ensures isolated application contexts.

### 2. Configuration System (`config/settings.py`)
Utilizes a class-based hierarchy (`BaseConfig`, `DevelopmentConfig`, `TestingConfig`). This isolates environment-specific variables and prepares placeholders for the SQLite Database URL required in Phase 2.

### 3. Blueprint Architecture (`core/blueprint_loader.py`)
Separates routing logic from the core factory. APIs are versioned under `/api/v1/`. The `health_api.py` serves as a blueprint template for future laboratory and authentication endpoints.

### 4. Logging Strategy (`core/app_factory.py -> configure_logging`)
Implements Python's `RotatingFileHandler`. All logs are safely written to `logs/cyberlab.log` with a max size of 1MB per file (keeping 10 backups). This is critical for debugging offline USB-deployed school environments.

### 5. Future Extension Points (`core/extensions.py`)
Prepared to accept Flask-SQLAlchemy and Flask-Migrate in Phase 2 without requiring structural refactoring of the `app_factory`.

## Development Architecture Rules
- No business logic inside Flask routes.
- Services cannot depend on Flask request/response objects.
- Services cannot directly access database.
- Repositories are the only database access layer.
- No global Flask application instance.
- New features must respect Clean Architecture layers.