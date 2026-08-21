from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class BatchStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DEPLETED = "depleted"

class MedicationBatchBase(BaseModel):
    medication_name: str
    batch_number: str
    quantity: int
    expiry_date: datetime

class MedicationBatchCreate(MedicationBatchBase):
    pass

class MedicationBatchUpdate(BaseModel):
    quantity: Optional[int] = None
    status: Optional[BatchStatus] = None

class MedicationBatchOut(MedicationBatchBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: BatchStatus
    created_at: datetime

class DispenseLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    medication_name: str
    quantity_dispensed: int
    batch_id: int
    dispensed_at: datetime
    staff_id: int
