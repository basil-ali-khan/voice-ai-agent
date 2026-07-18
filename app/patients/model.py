from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = (
        CheckConstraint("length(first_name) BETWEEN 1 AND 50", name="first_name_length"),
        CheckConstraint("length(last_name) BETWEEN 1 AND 50", name="last_name_length"),
        CheckConstraint("sex IN ('Male', 'Female', 'Other', 'Decline to Answer')", name="valid_sex"),
        CheckConstraint("length(state) = 2", name="state_length"),
        CheckConstraint("length(phone_number) = 10", name="phone_length"),
        Index("ix_patients_last_name", "last_name"),
        Index("ix_patients_date_of_birth", "date_of_birth"),
        Index("ix_patients_phone_number", "phone_number"),
    )

    patient_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    sex: Mapped[str] = mapped_column(String(20), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(10), nullable=False)
    email: Mapped[str | None] = mapped_column(String(254))
    address_line_1: Mapped[str] = mapped_column(String(150), nullable=False)
    address_line_2: Mapped[str | None] = mapped_column(String(150))
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=False)
    insurance_provider: Mapped[str | None] = mapped_column(String(100))
    insurance_member_id: Mapped[str | None] = mapped_column(String(100))
    preferred_language: Mapped[str | None] = mapped_column(String(50), default="English")
    emergency_contact_name: Mapped[str | None] = mapped_column(String(100))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(10))
    source_call_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
