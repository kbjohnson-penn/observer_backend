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
    # Regular expression to match SAS tokens
    sas_token_pattern = re.compile(r'[?&]([a-zA-Z]+)=([^&]+)')
    sanitized_message = sas_token_pattern.sub(r'\1=REDACTED', message)
    return sanitized_message


class SanitizingHandler(logging.StreamHandler):
    def emit(self, record):
        record.msg = sanitize_log_message(record.msg)
        super().emit(record)
