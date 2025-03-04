import re
from django.core.exceptions import ValidationError


def validate_numeric(value):
    if not re.fullmatch(r"^\d+$", value):
        raise ValidationError('This field can only contain numeric digits (0-9).')
    
def validate_phone_number(value):
    if not re.fullmatch(r"^\+?\d+$", value):
        raise ValidationError('Phone number can only contain numeric digits (0-9) and one leading plus (+) sign.')
    
def validate_name(value):
    if not re.fullmatch(r"^[A-Za-zÀ-ÖØ-öø-ÿ'’\-\s\.]+$", value):
        raise ValidationError('Name can only contain letters (including accented characters), apostrophes, hyphens, spaces, and periods.')
    
def validate_address(value):
    if not re.fullmatch(r"^[A-Za-z0-9 .,\-#'/&@:()]*$", value):
        raise ValidationError('Address can only contain letters, numbers, spaces, and common punctuation: . , - # / & @ : ()')
    