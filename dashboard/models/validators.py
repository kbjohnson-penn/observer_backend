import re
from django.core.exceptions import ValidationError

def validate_zip_code(value):
    if not re.fullmatch(r"^\d+$", value):
        raise ValidationError('ZIP code can only contain numeric digits (0-9).')
    
def validate_phone_number(value):
    if not re.fullmatch(r"^\+?\d+$", value):
        raise ValidationError('Phone number can only contain numeric digits (0-9) and one leading plus (+) sign.')
    