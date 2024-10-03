import re
import logging


def sanitize_log_message(message):
    # Regular expression to match SAS tokens
    sas_token_pattern = re.compile(r'[?&]([a-zA-Z]+)=([^&]+)')
    sanitized_message = sas_token_pattern.sub(r'\1=REDACTED', message)
    return sanitized_message


class SanitizingHandler(logging.StreamHandler):
    def emit(self, record):
        record.msg = sanitize_log_message(record.msg)
        super().emit(record)
