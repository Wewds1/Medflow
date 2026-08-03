# MedFlow

MedFlow is a planned medical resource triage and clinical operations platform. The current workspace is the initial project setup stage, so this README documents the project direction and the first development steps.

## Current Status

- Python virtual environment is set up
- FastAPI has been installed
- Application code has not been built yet
- This repository currently serves as the starting point for the MedFlow backend

## Project Goal

MedFlow is intended to become an event-driven clinical system with separate areas for:

- Authentication and RBAC
- Appointments
- EHR and encounters
- Triage and risk scoring
- Pharmacy and stock management
- Lab integrations
- Billing and revenue cycle management

## Planned Stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic v2
- PostgreSQL
- Redis Streams or Celery
- Docker Compose
- PyJWT
- React for the frontend later

## Local Setup

If you are starting from a fresh clone, the basic setup is:

```bash
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn[standard]
```

## Next Step

The next implementation step is to decide whether to start with:

1. Docker Compose plus the seven-database initialization script
2. Pydantic v2 schemas and SQLAlchemy models for Phase 1 Auth and RBAC

## Notes

The architecture plan for MedFlow is documented in [medflow.md](medflow.md).
