import re
from datetime import date, datetime

from pydantic import EmailStr

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA",
    "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO",
    "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI",
    "WV", "WY", "DC",
}
NAME_PATTERN = re.compile(r"^[A-Za-z]+(?:[ '-][A-Za-z]+)*$")
MEMBER_ID_PATTERN = re.compile(r"^[A-Za-z0-9-]+$")
ZIP_PATTERN = re.compile(r"^\d{5}(?:-\d{4})?$")


def required_text(value: str, field_name: str, maximum: int = 100) -> str:
    value = value.strip()
    if not value or len(value) > maximum:
        raise ValueError(f"{field_name} must be between 1 and {maximum} characters.")
    return value


def optional_text(value: str | None, maximum: int = 100) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if len(value) > maximum:
        raise ValueError(f"Value must not exceed {maximum} characters.")
    return value


def normalize_name(value: str, field_name: str) -> str:
    value = required_text(value, field_name, 50)
    if not NAME_PATTERN.fullmatch(value):
        raise ValueError(f"{field_name} may only contain letters, spaces, hyphens, and apostrophes.")
    return value


def normalize_date_of_birth(value: date | str) -> date:
    if isinstance(value, datetime):
        value = value.date()
    elif isinstance(value, str):
        for date_format in ("%m/%d/%Y", "%Y-%m-%d"):
            try:
                value = datetime.strptime(value.strip(), date_format).date()
                break
            except ValueError:
                continue
        else:
            raise ValueError("date_of_birth must be MM/DD/YYYY or YYYY-MM-DD.")
    if value > date.today():
        raise ValueError("date_of_birth cannot be in the future.")
    return value


def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10 or digits[0] in "01":
        raise ValueError("phone_number must be a valid U.S. 10-digit phone number.")
    return digits


def normalize_state(value: str) -> str:
    value = value.strip().upper()
    if value not in US_STATES:
        raise ValueError("state must be a valid two-letter U.S. state abbreviation.")
    return value


def normalize_zip(value: str) -> str:
    value = value.strip()
    if not ZIP_PATTERN.fullmatch(value):
        raise ValueError("zip_code must be a 5-digit or ZIP+4 U.S. postal code.")
    return value


def normalize_email(value: str | None) -> str | None:
    value = optional_text(value, 254)
    if value is None:
        return None
    try:
        return str(EmailStr._validate(value))
    except ValueError as error:
        raise ValueError("email must be a valid email address.") from error


def normalize_member_id(value: str | None) -> str | None:
    value = optional_text(value, 100)
    if value is not None and not MEMBER_ID_PATTERN.fullmatch(value):
        raise ValueError("insurance_member_id must be alphanumeric (hyphens allowed).")
    return value
