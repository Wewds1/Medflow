import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from database import Base

class EncounterType(enum.Enum):
    ROUTINE = "routine"
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    medical_history_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    encounters = relationship("Encounter", back_populates="patient")

class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, nullable=False, index=True) # Reference to Auth User
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    encounter_type = Column(Enum(EncounterType), default=EncounterType.ROUTINE, nullable=False)

    # JSONB for unstructured notes as per architecture plan
    clinical_notes = Column(JSON, nullable=True)

    diagnosis = Column(String, nullable=True)
    treatment_plan = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="encounters")
