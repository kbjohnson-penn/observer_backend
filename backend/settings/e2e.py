"""
E2E test settings.

Uses real MariaDB (same as dev), but with:
- Rate limiting disabled
- Long JWT lifetimes (tests don't hit expiry)
- Test email domains allowed
- Console email backend

Usage:
    DJANGO_SETTINGS_MODULE=backend.settings.e2e python manage.py runserver
"""

from datetime import timedelta

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "backend"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://frontend:3000",
]

# CORS Configuration
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://frontend:3000",
]

# Disable rate limiting for E2E tests
RATELIMIT_ENABLE = False

# Long JWT lifetimes so tests don't expire mid-run
SIMPLE_JWT.update(
    {
        "ACCESS_TOKEN_LIFETIME": timedelta(hours=4),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    }
)

# Disable Azure storage for E2E
AZURE_STORAGE_ACCOUNT_NAME = "test_account"
AZURE_STORAGE_FILE_SYSTEM_NAME = "test_filesystem"
AZURE_SAS_TOKEN = "test_token"

# Allow test email domains
ALLOW_TEST_EMAILS = True
TEST_EMAIL_DOMAINS = ["example.com", "gmail.com", "outlook.com", "yahoo.com"]

# Console email backend (no real emails sent)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Frontend URL for email links
FRONTEND_URL = "http://localhost:3000"
