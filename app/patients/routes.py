from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.patients.schemas import PatientCreate, PatientFilter, PatientResponse, PatientUpdate
from app.patients.service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])


def get_service(session: Session = Depends(get_session)) -> PatientService:
    return PatientService(session)


@router.get("")
def list_patients(filters: PatientFilter = Depends(), service: PatientService = Depends(get_service)):
    patients = service.list_patients(filters)
    return {"data": [PatientResponse.model_validate(patient).model_dump(mode="json") for patient in patients], "error": None}


@router.get("/{patient_id}")
def get_patient(patient_id: str, service: PatientService = Depends(get_service)):
    patient = service.get_patient(patient_id)
    return {"data": PatientResponse.model_validate(patient).model_dump(mode="json"), "error": None}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, service: PatientService = Depends(get_service)):
    created, _ = service.create_patient(patient)
    return {"data": PatientResponse.model_validate(created).model_dump(mode="json"), "error": None}


@router.put("/{patient_id}")
def update_patient(patient_id: str, update: PatientUpdate, service: PatientService = Depends(get_service)):
    patient = service.update_patient(patient_id, update)
    return {"data": PatientResponse.model_validate(patient).model_dump(mode="json"), "error": None}


@router.delete("/{patient_id}", status_code=status.HTTP_200_OK)
def delete_patient(patient_id: str, service: PatientService = Depends(get_service)):
    service.delete_patient(patient_id)
    return {"data": {"patient_id": patient_id, "deleted": True}, "error": None}
