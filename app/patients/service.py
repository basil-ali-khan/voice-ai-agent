from sqlalchemy.orm import Session

from app.errors import PatientNotFoundError
from app.patients.repository import PatientRepository
from app.patients.schemas import PatientCreate, PatientFilter, PatientUpdate


class PatientService:
    def __init__(self, session: Session) -> None:
        self.repository = PatientRepository(session)

    def create_patient(self, patient: PatientCreate, source_call_id: str | None = None):
        if source_call_id:
            existing = self.repository.get_by_source_call_id(source_call_id)
            if existing:
                return existing, True
        return self.repository.create(patient.model_dump(), source_call_id), False

    def list_patients(self, filters: PatientFilter):
        return self.repository.list_active(filters.model_dump())

    def get_patient(self, patient_id: str):
        patient = self.repository.get_active(patient_id)
        if patient is None:
            raise PatientNotFoundError(patient_id)
        return patient

    def update_patient(self, patient_id: str, update: PatientUpdate):
        patient = self.get_patient(patient_id)
        return self.repository.update(patient, update.model_dump(exclude_unset=True))

    def delete_patient(self, patient_id: str) -> None:
        self.repository.soft_delete(self.get_patient(patient_id))
