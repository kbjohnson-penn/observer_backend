import re
from datetime import date, datetime

from django.core.exceptions import ValidationError


def validate_field(value):
    """Generic field validator for text fields."""
    # Treat None and empty string consistently
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return  # Allow empty values

    # Basic validation: reasonable length
    if isinstance(value, str):
        if len(value.strip()) > 1000:
            raise ValidationError("Field value too long (maximum 1000 characters)")


def validate_address(value):
    """Validate address field."""
    # Treat None and empty string consistently
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return  # Allow empty values

    # Basic address validation
    if isinstance(value, str):
        cleaned_value = value.strip()
        if len(cleaned_value) < 5:
            raise ValidationError("Address too short (minimum 5 characters)")
        if len(cleaned_value) > 200:
            raise ValidationError("Address too long (maximum 200 characters)")

        # Check for reasonable characters (letters, numbers, spaces, common punctuation)
        if not re.match(r"^[a-zA-Z0-9\s\.,#\-\/]+$", cleaned_value):
            raise ValidationError("Address contains invalid characters")


def validate_numeric(value):
    """Validate numeric field."""
    # Treat None and empty string consistently
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return  # Allow empty values
    try:
        float(value)
    except (ValueError, TypeError):
        raise ValidationError("Value must be numeric")


def validate_phone_number(value):
    """Validate phone number field."""
    # Treat None and empty string consistently
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return  # Allow empty values
    # Basic phone number validation
    cleaned_value = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    phone_pattern = r"^\+?1?\d{9,15}$"
    if not re.match(phone_pattern, cleaned_value):
        raise ValidationError("Invalid phone number format")


def validate_time(value):
    """Validate time/date field."""
    # Treat None and empty string consistently
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return  # Allow empty values

    # For datetime objects, check if they're in a reasonable range
    if isinstance(value, (datetime, date)):
        current_year = datetime.now().year
        if hasattr(value, "year"):
            # Check for reasonable date range (not too far in past/future)
            if value.year < 1900:
                raise ValidationError("Date too far in the past (before 1900)")
            if value.year > current_year + 10:
                raise ValidationError("Date too far in the future")

    # For string values, try to parse as date
    elif isinstance(value, str):
        try:
            # Try parsing common date formats
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            try:
                datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValidationError(
                    "Invalid date/time format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"
                )


def validate_website(value):
    """Validate website URL field."""
    # Treat None and empty string consistently
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return  # Allow empty values
    url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    if not re.match(url_pattern, value.strip()):
        raise ValidationError("Invalid website URL format")
