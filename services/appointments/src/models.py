import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class SlotStatus(enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(SlotStatus), default=SlotStatus.AVAILABLE, nullable=False)

    appointment = relationship("Appointment", back_populates="slot", uselist=False)

    __table_args__ = (
        UniqueConstraint('doctor_id', 'start_time', name='_doctor_slot_uc'),
    )

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    slot_id = Column(Integer, ForeignKey("slots.id"), unique=True, nullable=False)
    patient_id = Column(Integer, nullable=False, index=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    slot = relationship("Slot", back_populates="appointment")
