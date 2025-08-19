"""
Development settings
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0').split(',')

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000').split(',')

# CORS Configuration - Development
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000').split(',')

# Documentation URL
DOCUMENTATION_URL = config('DOCUMENTATION_URL', default='http://localhost:8000/docs/')

# Development-specific apps - commented out as they're not installed
# INSTALLED_APPS += [
#     'django_extensions',  # Optional: helpful development tools
#     'debug_toolbar',      # Optional: Django Debug Toolbar
# ]

# Debug toolbar middleware (add at the beginning)
# if 'debug_toolbar' in INSTALLED_APPS:
#     MIDDLEWARE = [
#         'debug_toolbar.middleware.DebugToolbarMiddleware',
#     ] + MIDDLEWARE

# Internal IPs for debug toolbar
# INTERNAL_IPS = [
#     '127.0.0.1',
#     'localhost',
# ]

# Template debug setting
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# Email backend for development - use SMTP if configured, otherwise console
if DEBUG:
    if config('EMAIL_HOST_USER', default=''):
        # Use SMTP if email user is configured
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    else:
        # Use console backend for testing without real email
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development database test configuration
DATABASES['default']['TEST'] = {
    'NAME': config('TEST_DEFAULT_DB', default='test_observer_default'),
    'DEPENDENCIES': [],
}
DATABASES['accounts']['TEST'] = {
    'NAME': config('TEST_ACCOUNTS_DB', default='test_observer_accounts'),
    'DEPENDENCIES': [],
}
DATABASES['clinical']['TEST'] = {
    'NAME': config('TEST_CLINICAL_DB', default='test_observer_clinical'),
    'DEPENDENCIES': ['accounts'],
}
DATABASES['research']['TEST'] = {
    'NAME': config('TEST_RESEARCH_DB', default='test_observer_research'),
    'DEPENDENCIES': [],
}

# Development logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, config('LOG_FILE', default='django_dev.log')),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',  # Set to DEBUG to see SQL queries
            'propagate': False,
        },
    },
}