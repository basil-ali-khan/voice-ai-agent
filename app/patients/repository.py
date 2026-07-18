from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.patients.model import Patient


class PatientRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, values: dict, source_call_id: str | None = None) -> Patient:
        patient = Patient(**values, source_call_id=source_call_id)
        self.session.add(patient)
        self.session.commit()
        self.session.refresh(patient)
        return patient

    def list_active(self, filters: dict) -> list[Patient]:
        statement = select(Patient).where(Patient.deleted_at.is_(None))
        for field, value in filters.items():
            if value is not None:
                statement = statement.where(getattr(Patient, field) == value)
        return list(self.session.scalars(statement.order_by(Patient.created_at.desc())))

    def get_active(self, patient_id: str) -> Patient | None:
        statement = select(Patient).where(Patient.patient_id == patient_id, Patient.deleted_at.is_(None))
        return self.session.scalar(statement)

    def get_by_source_call_id(self, source_call_id: str) -> Patient | None:
        return self.session.scalar(select(Patient).where(Patient.source_call_id == source_call_id))

    def update(self, patient: Patient, values: dict) -> Patient:
        for field, value in values.items():
            setattr(patient, field, value)
        self.session.commit()
        self.session.refresh(patient)
        return patient

    def soft_delete(self, patient: Patient) -> None:
        patient.deleted_at = datetime.now(timezone.utc)
        self.session.commit()
