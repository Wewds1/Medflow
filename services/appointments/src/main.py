import asyncio
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from database import get_db
from models import Slot, Appointment, SlotStatus, AppointmentStatus
from schemas import SlotCreate, SlotOut, AppointmentCreate, AppointmentOut

app = FastAPI(title="MedFlow Appointments Service")

@app.post("/slots", response_model=SlotOut)
async def create_slot(slot: SlotCreate, db: AsyncSession = Depends(get_db)):
    # In a real app, this would be protected by a permission check (e.g., doctor:manage)
    db_slot = Slot(**slot.model_dump())
    db.add(db_slot)
    await db.commit()
    await db.refresh(db_slot)
    return db_slot

@app.get("/slots", response_model=List[SlotOut])
async def list_available_slots(doctor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Slot).where(Slot.doctor_id == doctor_id, Slot.status == SlotStatus.AVAILABLE)
    )
    return result.scalars().all()

@app.post("/appointments", response_model=AppointmentOut)
async def book_appointment(appointment: AppointmentCreate, db: AsyncSession = Depends(get_db)):
    # Critical Section: Use SELECT FOR UPDATE to prevent double-booking
    async with db.begin():
        # Lock the slot row
        result = await db.execute(
            select(Slot)
            .where(Slot.id == appointment.slot_id)
            .with_for_update()
        )
        slot = result.scalar_one_or_none()

        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")

        if slot.status != SlotStatus.AVAILABLE:
            raise HTTPException(
                status_code=400,
                detail=f"Slot is no longer available (Status: {slot.status.value})"
            )

        # Update slot status
        slot.status = SlotStatus.BOOKED

        # Create appointment
        db_appointment = Appointment(
            slot_id=appointment.slot_id,
            patient_id=appointment.patient_id,
            reason=appointment.reason,
            status=AppointmentStatus.SCHEDULED
        )
        db.add(db_appointment)

        # The transaction is committed automatically by the 'async with db.begin()' block
        # But we need to refresh the appointment to get the ID and created_at
        await db.flush()
        await db.refresh(db_appointment)
        return db_appointment

@app.get("/appointments/{appointment_id}", response_model=AppointmentOut)
async def get_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
