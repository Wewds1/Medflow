from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models import MedicationBatch, DispenseLog, BatchStatus
from schemas import MedicationBatchCreate, MedicationBatchUpdate

async def dispense_medication(db: AsyncSession, med_name: str, qty: int, patient_id: int, staff_id: int):
    """
    Dispense medication using FIFO logic.
    Locks the oldest active batch to prevent race conditions.
    """
    # FIFO: Find the oldest active batch that has enough stock
    result = await db.execute(
        select(MedicationBatch)
        .where(MedicationBatch.medication_name == med_name, MedicationBatch.status == BatchStatus.ACTIVE)
        .order_by(MedicationBatch.expiry_date.asc())
        .with_for_update()
    )
    batch = result.scalar_one_or_none()

    if not batch:
        raise ValueError(f"No active batches found for {med_name}")

    if batch.quantity < qty:
        raise ValueError(f"Insufficient stock in batch {batch.batch_number} (Available: {batch.quantity})")

    # Deduct stock
    batch.quantity -= qty
    if batch.quantity == 0:
        batch.status = BatchStatus.DEPLETED

    # Log the dispense
    log = DispenseLog(
        patient_id=patient_id,
        medication_name=med_name,
        quantity_dispensed=qty,
        batch_id=batch.id,
        staff_id=staff_id
    )
    db.add(log)

    return log

async def create_medication_batch(db: AsyncSession, batch_in: MedicationBatchCreate):
    db_batch = MedicationBatch(**batch_in.model_dump())
    db.add(db_batch)
    await db.commit()
    await db.refresh(db_batch)
    return db_batch

async def get_medication_batches(db: AsyncSession, medication_name: str = None, status: BatchStatus = None):
    query = select(MedicationBatch)
    if medication_name:
        query = query.where(MedicationBatch.medication_name == medication_name)
    if status:
        query = query.where(MedicationBatch.status == status)

    result = await db.execute(query)
    return result.scalars().all()

async def get_medication_batch(db: AsyncSession, batch_id: int):
    result = await db.execute(select(MedicationBatch).where(MedicationBatch.id == batch_id))
    return result.scalar_one_or_none()

async def update_medication_batch(db: AsyncSession, batch_id: int, update_data: MedicationBatchUpdate):
    batch = await get_medication_batch(db, batch_id)
    if not batch:
        return None

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(batch, field, value)

    await db.commit()
    await db.refresh(batch)
    return batch

async def get_patient_dispense_history(db: AsyncSession, patient_id: int):
    result = await db.execute(
        select(DispenseLog).where(DispenseLog.patient_id == patient_id).order_by(DispenseLog.dispensed_at.desc())
    )
    return result.scalars().all()

async def get_dispense_log(db: AsyncSession, log_id: int):
    result = await db.execute(select(DispenseLog).where(DispenseLog.id == log_id))
    return result.scalar_one_or_none()

async def get_aggregate_stock(db: AsyncSession, medication_name: str):
    result = await db.execute(
        select(func.sum(MedicationBatch.quantity))
        .where(MedicationBatch.medication_name == medication_name, MedicationBatch.status == BatchStatus.ACTIVE)
    )
    return result.scalar() or 0
