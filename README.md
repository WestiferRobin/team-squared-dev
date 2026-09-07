# Team Squared Development Environment

Local development and integration workspace for the Team Squared CS 514 database product project.

## Responsibilities

- Pin the frontend and backend repositories as Git submodules
- Docker Compose orchestration
- Local relational database
- Environment configuration
- Service networking
- Database migration and seed workflow
- Health checks
- Integration, smoke, and end-to-end test entry points
- Reproducible full-product startup instructions

## Repository Layout

Planned layout:

    app/       -> team-squared-app
    service/   -> team-squared-service

Documentation remains in `team-squared-wiki` and does not need to be a runtime submodule.

This repository does not own application business logic or database schema definitions. Those belong in `team-squared-service`.
