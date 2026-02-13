"""
Production settings
"""

from .base import *

# Security settings
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS").split(",")

# CORS Configuration - Production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS").split(",")

# Cookie settings for cross-subdomain authentication
# SameSite=None is required for cookies to work across different subdomains (cross-origin requests)
# This is safe because we're using HTTPS (SESSION_COOKIE_SECURE=True and CSRF_COOKIE_SECURE=True)
SESSION_COOKIE_SAMESITE = (
    "None"  # Required for cross-origin requests (frontend on different subdomain)
)
CSRF_COOKIE_SAMESITE = (
    "None"  # Required for cross-origin requests (frontend on different subdomain)
)
SESSION_COOKIE_HTTPONLY = True  # Security: prevent JavaScript access to session cookie
CSRF_COOKIE_HTTPONLY = False  # Frontend JavaScript needs to read CSRF token for API calls

# Documentation URL
DOCUMENTATION_URL = config("DOCUMENTATION_URL")

# Enhanced security for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cross-subdomain cookie sharing (optional)
# Enable these if backend and frontend are on different subdomains
# and need to share authentication cookies
# Example: backend on observer-dev.pmacs.upenn.edu, frontend on observer-dev-d.pmacs.upenn.edu
if config("SESSION_COOKIE_DOMAIN", default=None):
    SESSION_COOKIE_DOMAIN = config("SESSION_COOKIE_DOMAIN")
if config("CSRF_COOKIE_DOMAIN", default=None):
    CSRF_COOKIE_DOMAIN = config("CSRF_COOKIE_DOMAIN")

# Production database test configuration
DATABASES["default"]["TEST"] = {
    "NAME": config("TEST_DEFAULT_DB", default="test_observer_default"),
    "DEPENDENCIES": [],
}
DATABASES["accounts"]["TEST"] = {
    "NAME": config("TEST_ACCOUNTS_DB", default="test_observer_accounts"),
    "DEPENDENCIES": [],
}
DATABASES["clinical"]["TEST"] = {
    "NAME": config("TEST_CLINICAL_DB", default="test_observer_clinical"),
    "DEPENDENCIES": ["accounts"],
}
DATABASES["research"]["TEST"] = {
    "NAME": config("TEST_RESEARCH_DB", default="test_observer_research"),
    "DEPENDENCIES": [],
}

# Template debug setting
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# Production logging with rotation
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "format": '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, config("LOG_FILE", default="django_prd.log")),
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(
                BASE_DIR, config("ERROR_LOG_FILE", default="django_error.log")
            ),
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 5,
            "formatter": "verbose",
            "level": "ERROR",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
        },
        "django": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
        "clinical": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
        "research": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Cache configuration for production (if using Redis)
if config("REDIS_URL", default=None):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": config("REDIS_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

    # Session engine (cache-based for better performance)
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
else:
    # Fallback to database sessions
    SESSION_ENGINE = "django.contrib.sessions.backends.db"
