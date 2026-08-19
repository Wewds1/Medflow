from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any, List
from models import EncounterType

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    medical_history_summary: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientOut(PatientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class EncounterBase(BaseModel):
    patient_id: int
    doctor_id: int
    encounter_type: EncounterType = EncounterType.ROUTINE
    clinical_notes: Optional[Dict[str, Any]] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None

class EncounterCreate(EncounterBase):
    pass

class EncounterOut(EncounterBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True
