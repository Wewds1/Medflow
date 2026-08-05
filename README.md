# MedFlow

MedFlow is a planned medical resource triage and clinical operations platform. The current workspace is the initial project setup stage, so this README documents the project direction and the first development steps.

## Current Status

- Python virtual environment is set up
- FastAPI has been installed
- Docker Compose environment is active (PostgreSQL, Redis)
- Seven bounded-context databases have been successfully provisioned
- Moving from environment setup into the implementation of the first service

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

The project has entered **Phase 1: Foundation**. The immediate focus is the implementation of the **Auth and RBAC service skeleton**, including:
- SQLAlchemy models for Users, Roles, and Permissions.
- JWT issuance with RSA signing.
- Shared JWT-decode dependency for other services.

## Notes

The architecture plan for MedFlow is documented in [PLAN.md](PLAN.md).
