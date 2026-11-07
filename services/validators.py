"""Simple input validation functions."""
import re


def valid_phone(phone):
    """Check that an Indian phone number contains ten digits."""
    return bool(re.fullmatch(r'[6-9]\d{9}', phone or ''))


def valid_email(email):
    """Perform a basic email format check."""
    return bool(re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email or ''))


def required_fields(data, fields):
    """Return names of required fields that are empty."""
    return [field for field in fields if not str(data.get(field, '')).strip()]
