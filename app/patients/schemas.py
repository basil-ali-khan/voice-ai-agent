from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.patients import validators

Sex = Literal["Male", "Female", "Other", "Decline to Answer"]


class PatientFields(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    date_of_birth: date
    sex: Sex
    phone_number: str
    email: str | None = None
    address_line_1: str = Field(max_length=150)
    address_line_2: str | None = Field(default=None, max_length=150)
    city: str = Field(max_length=100)
    state: str
    zip_code: str
    insurance_provider: str | None = Field(default=None, max_length=100)
    insurance_member_id: str | None = Field(default=None, max_length=100)
    preferred_language: str | None = Field(default="English", max_length=50)
    emergency_contact_name: str | None = Field(default=None, max_length=100)
    emergency_contact_phone: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str, info) -> str:
        return validators.normalize_name(value, info.field_name)

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def validate_date_of_birth(cls, value: date | str) -> date:
        return validators.normalize_date_of_birth(value)

    @field_validator("phone_number", "emergency_contact_phone", mode="before")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return None if value is None else validators.normalize_phone(value)

    @field_validator("address_line_1", "city")
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        maximum = 150 if info.field_name == "address_line_1" else 100
        return validators.required_text(value, info.field_name, maximum)

    @field_validator("address_line_2", "insurance_provider", "preferred_language", "emergency_contact_name")
    @classmethod
    def validate_optional_text(cls, value: str | None, info) -> str | None:
        maximum = 150 if info.field_name == "address_line_2" else 100
        return validators.optional_text(value, maximum)

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str) -> str:
        return validators.normalize_state(value)

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, value: str) -> str:
        return validators.normalize_zip(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        return validators.normalize_email(value)

    @field_validator("insurance_member_id")
    @classmethod
    def validate_member_id(cls, value: str | None) -> str | None:
        return validators.normalize_member_id(value)


class PatientCreate(PatientFields):
    pass


class PatientUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    date_of_birth: date | None = None
    sex: Sex | None = None
    phone_number: str | None = None
    email: str | None = None
    address_line_1: str | None = Field(default=None, max_length=150)
    address_line_2: str | None = Field(default=None, max_length=150)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = None
    zip_code: str | None = None
    insurance_provider: str | None = Field(default=None, max_length=100)
    insurance_member_id: str | None = Field(default=None, max_length=100)
    preferred_language: str | None = Field(default=None, max_length=50)
    emergency_contact_name: str | None = Field(default=None, max_length=100)
    emergency_contact_phone: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str | None, info) -> str | None:
        return None if value is None else validators.normalize_name(value, info.field_name)

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def validate_date_of_birth(cls, value: date | str | None) -> date | None:
        return None if value is None else validators.normalize_date_of_birth(value)

    @field_validator("phone_number", "emergency_contact_phone", mode="before")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return None if value is None else validators.normalize_phone(value)

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str | None) -> str | None:
        return None if value is None else validators.normalize_state(value)

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, value: str | None) -> str | None:
        return None if value is None else validators.normalize_zip(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        return validators.normalize_email(value)

    @field_validator("insurance_member_id")
    @classmethod
    def validate_member_id(cls, value: str | None) -> str | None:
        return validators.normalize_member_id(value)


class PatientFilter(BaseModel):
    last_name: str | None = None
    date_of_birth: date | None = None
    phone_number: str | None = None

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: str | None) -> str | None:
        return None if value is None else validators.normalize_name(value, "last_name")

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def validate_date_of_birth(cls, value: date | str | None) -> date | None:
        return None if value is None else validators.normalize_date_of_birth(value)

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return None if value is None else validators.normalize_phone(value)


class PatientResponse(PatientFields):
    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
