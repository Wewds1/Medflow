import os
import json
import asyncio
import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from database import get_db
from models import Patient, Encounter, EncounterType, OutboxEvent
from schemas import PatientCreate, PatientOut, EncounterCreate, EncounterOut, PrescriptionCreate, PrescriptionOut
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Load env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(str(env_path))

app = FastAPI(title="MedFlow EHR Service")

# Redis setup for caching
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def get_cached_patient(patient_id: int):
    cache_key = f"patient:{patient_id}"
    data = await redis_client.get(cache_key)
    return json.loads(data) if data else None

async def set_cached_patient(patient_id: int, patient_data: dict):
    cache_key = f"patient:{patient_id}"
    await redis_client.setex(cache_key, 3600, json.dumps(patient_data))

async def invalidate_patient_cache(patient_id: int):
    await redis_client.delete(f"patient:{patient_id}")

@app.post("/patients", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate, db: AsyncSession = Depends(get_db)):
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    return db_patient

@app.get("/patients/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    cached = await get_cached_patient(patient_id)
    if cached:
        return cached

    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_out = PatientOut.model_validate(patient).model_dump()
    await set_cached_patient(patient_id, patient_out)

    return patient_out

@app.put("/patients/{patient_id}", response_model=PatientOut)
async def update_patient(patient_id: int, patient_data: PatientCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    db_patient = result.scalar_one_or_none()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    for key, value in patient_data.model_dump().items():
        setattr(db_patient, key, value)

    await db.commit()
    await db.refresh(db_patient)
    await invalidate_patient_cache(patient_id)
    return db_patient

@app.post("/encounters", response_model=EncounterOut, status_code=status.HTTP_201_CREATED)
async def create_encounter(encounter: EncounterCreate, db: AsyncSession = Depends(get_db)):
    db_encounter = Encounter(**encounter.model_dump())
    db.add(db_encounter)
    await db.commit()
    await db.refresh(db_encounter)
    return db_encounter

@app.get("/patients/{patient_id}/encounters", response_model=List[EncounterOut])
async def list_encounters(patient_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Encounter).where(Encounter.patient_id == patient_id)
    )
    return result.scalars().all()

@app.post("/prescriptions", status_code=status.HTTP_202_ACCEPTED)
async def create_prescription(prescription: PrescriptionCreate, db: AsyncSession = Depends(get_db)):
    """
    Creates a prescription and writes an event to the outbox in the same transaction.
    """
    async with db.begin():
        # 1. Logic for 'writing' the prescription would go here (e.g. into a prescriptions table)
        # For now, we focus on the Outbox pattern.

        # 2. Write to Outbox
        event = OutboxEvent(
            event_type="prescription_created",
            payload=prescription.model_dump()
        )
        db.add(event)
        # commit happens automatically by db.begin()

    return {"status": "Prescription accepted and queued for fulfillment"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
