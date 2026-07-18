class DomainError(Exception):
    code = "domain_error"
    status_code = 400

    def __init__(self, message: str, details: dict | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class PatientNotFoundError(DomainError):
    code = "patient_not_found"
    status_code = 404

    def __init__(self, patient_id: str) -> None:
        super().__init__(f"Patient {patient_id} was not found.")
