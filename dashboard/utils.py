import re
import logging
from datetime import date
from dateutil.relativedelta import relativedelta


def calculate_age(date_of_birth):
    if date_of_birth is None:
        return None
    today = date.today()
    return relativedelta(today, date_of_birth).years


def sanitize_log_message(message):
    """
    Sanitize log messages to remove sensitive information including:
    - SAS tokens
    - Passwords
    - API keys
    - JWT tokens
    - Credit card numbers
    - SSNs
    - Email addresses (partially)
    """
    if not isinstance(message, str):
        message = str(message)
    
    # Patterns for different types of sensitive data
    patterns = [
        # SAS tokens and query parameters
        (r'[?&]([a-zA-Z_]+)=([^&\s]+)', r'\1=REDACTED'),
        
        # JWT tokens (Bearer tokens)
        (r'Bearer\s+([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]*)', r'Bearer REDACTED'),
        
        # API keys (various formats)
        (r'api[_-]?key["\s:=]+([A-Za-z0-9\-_]{20,})', r'api_key=REDACTED', re.IGNORECASE),
        (r'x-api-key["\s:=]+([A-Za-z0-9\-_]+)', r'x-api-key=REDACTED', re.IGNORECASE),
        
        # Passwords in various contexts
        (r'password["\s:=]+([^\s,"\']+)', r'password=REDACTED', re.IGNORECASE),
        (r'pwd["\s:=]+([^\s,"\']+)', r'pwd=REDACTED', re.IGNORECASE),
        (r'pass["\s:=]+([^\s,"\']+)', r'pass=REDACTED', re.IGNORECASE),
        
        # Secret keys
        (r'secret[_-]?key["\s:=]+([A-Za-z0-9\-_]+)', r'secret_key=REDACTED', re.IGNORECASE),
        (r'private[_-]?key["\s:=]+([A-Za-z0-9\-_]+)', r'private_key=REDACTED', re.IGNORECASE),
        
        # Credit card numbers (basic pattern)
        (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', r'CARD_NUMBER_REDACTED'),
        
        # SSN patterns
        (r'\b\d{3}-\d{2}-\d{4}\b', r'SSN_REDACTED'),
        (r'\b\d{9}\b', r'SSN_REDACTED'),
        
        # Email addresses (partially obscure)
        (r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', r'\1***@\2'),
        
        # Phone numbers
        (r'\b\d{3}-\d{3}-\d{4}\b', r'PHONE_REDACTED'),
        (r'\b\(\d{3}\)\s?\d{3}-\d{4}\b', r'PHONE_REDACTED'),
        
        # Database connection strings
        (r'://([^:]+):([^@]+)@', r'://USER:REDACTED@'),
        
        # AWS/Azure secrets
        (r'AKIA[0-9A-Z]{16}', r'AWS_ACCESS_KEY_REDACTED'),
        (r'[A-Za-z0-9/+=]{40}', r'AWS_SECRET_REDACTED'),
    ]
    
    sanitized_message = message
    for pattern_info in patterns:
        if len(pattern_info) == 3:
            pattern, replacement, flags = pattern_info
            sanitized_message = re.sub(pattern, replacement, sanitized_message, flags=flags)
        else:
            pattern, replacement = pattern_info
            sanitized_message = re.sub(pattern, replacement, sanitized_message)
    
    return sanitized_message


class SanitizingHandler(logging.StreamHandler):
    def emit(self, record):
        record.msg = sanitize_log_message(record.msg)
        super().emit(record)
