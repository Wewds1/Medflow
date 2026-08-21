import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base

class BatchStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DEPLETED = "depleted"

class MedicationBatch(Base):
    __tablename__ = "medication_batches"

    id = Column(Integer, primary_key=True, index=True)
    medication_name = Column(String, nullable=False, index=True)
    batch_number = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    expiry_date = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(BatchStatus), default=BatchStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DispenseLog(Base):
    __tablename__ = "dispense_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    medication_name = Column(String, nullable=False)
    quantity_dispensed = Column(Integer, nullable=False)
    batch_id = Column(Integer, ForeignKey("medication_batches.id"), nullable=False)
    dispensed_at = Column(DateTime, default=datetime.utcnow)
    staff_id = Column(Integer, nullable=False) # Who dispensed it
