"""
Test settings
"""
from .base import *

# Test mode
DEBUG = False
TESTING = True

ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# CORS Configuration - Testing
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ['http://testserver', 'http://localhost:3000']

# Documentation URL
DOCUMENTATION_URL = 'http://testserver/docs/'

# Use in-memory database for faster tests (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'accounts': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'clinical': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'research': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Password hashers - Use secure hasher even in tests
# MD5 is cryptographically broken and should never be used
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Test JWT settings (shorter lifetimes)
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=1),
})

# Disable Azure storage for tests
AZURE_STORAGE_ACCOUNT_NAME = 'test_account'
AZURE_STORAGE_FILE_SYSTEM_NAME = 'test_filesystem'
AZURE_SAS_TOKEN = 'test_token'

# Test media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}