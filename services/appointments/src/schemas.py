from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import SlotStatus, AppointmentStatus

class SlotBase(BaseModel):
    doctor_id: int
    start_time: datetime
    end_time: datetime
    status: SlotStatus = SlotStatus.AVAILABLE

class SlotCreate(SlotBase):
    pass

class SlotOut(SlotBase):
    id: int

    class Config:
        from_attributes = True

class AppointmentBase(BaseModel):
    slot_id: int
    patient_id: int
    reason: Optional[str] = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentOut(AppointmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
