import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from schemas import (
    MedicationBatchCreate, MedicationBatchOut, MedicationBatchUpdate,
    DispenseLogOut, BatchStatus
)
import services

app = FastAPI(title="MedFlow Pharmacy Service")

# --- Inventory Endpoints ---

@app.post("/batches", response_model=MedicationBatchOut, status_code=status.HTTP_201_CREATED)
async def create_batch(batch_in: MedicationBatchCreate, db: AsyncSession = Depends(get_db)):
    return await services.create_medication_batch(db, batch_in)

@app.get("/batches", response_model=List[MedicationBatchOut])
async def list_batches(
    medication_name: str = None,
    status: BatchStatus = None,
    db: AsyncSession = Depends(get_db)
):
    return await services.get_medication_batches(db, medication_name, status)

@app.get("/batches/{batch_id}", response_model=MedicationBatchOut)
async def get_batch(batch_id: int, db: AsyncSession = Depends(get_db)):
    batch = await services.get_medication_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Medication batch not found")
    return batch

@app.patch("/batches/{batch_id}", response_model=MedicationBatchOut)
async def update_batch(batch_id: int, update_data: MedicationBatchUpdate, db: AsyncSession = Depends(get_db)):
    batch = await services.update_medication_batch(db, batch_id, update_data)
    if not batch:
        raise HTTPException(status_code=404, detail="Medication batch not found")
    return batch

# --- Dispense Tracking Endpoints ---

@app.get("/dispense-logs/patient/{patient_id}", response_model=List[DispenseLogOut])
async def get_patient_history(patient_id: int, db: AsyncSession = Depends(get_db)):
    return await services.get_patient_dispense_history(db, patient_id)

@app.get("/dispense-logs/{log_id}", response_model=DispenseLogOut)
async def get_dispense_log(log_id: int, db: AsyncSession = Depends(get_db)):
    log = await services.get_dispense_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Dispense log not found")
    return log

# --- Stock Audit Endpoint ---

@app.get("/stock/{medication_name}")
async def get_stock_level(medication_name: str, db: AsyncSession = Depends(get_db)):
    total = await services.get_aggregate_stock(db, medication_name)
    return {"medication_name": medication_name, "total_available_stock": total}

if __name__ == "__main__":
    # Pharmacy service typically runs on a specific port, e.g., 8003
    uvicorn.run(app, host="0.0.0.0", port=8003)
