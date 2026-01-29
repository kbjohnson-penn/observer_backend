"""
Base settings shared across all environments
"""

import os
from datetime import timedelta
from pathlib import Path

import pymysql
from decouple import config

pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

APPEND_SLASH = True

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# Basic Security Settings
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Health Check Configuration
# Whitelist IPs that can access detailed health check endpoint
# Add your load balancer, monitoring services, and internal network IPs here
HEALTH_CHECK_ALLOWED_IPS = config(
    "HEALTH_CHECK_ALLOWED_IPS",
    default="127.0.0.1,::1",
    cast=lambda v: [ip.strip() for ip in v.split(",")],
)

# API Version
API_VERSION = "1.0.0"

# Rate Limiting Configuration
# Format: 'number/period' where period can be s (second), m (minute), h (hour), d (day)
RATE_LIMITS = {
    "LOGIN": config("RATE_LIMIT_LOGIN", default="5/m"),
    "REGISTRATION": config("RATE_LIMIT_REGISTRATION", default="3/m"),
    "PASSWORD_CHANGE": config("RATE_LIMIT_PASSWORD_CHANGE", default="10/m"),
    "PASSWORD_RESET_REQUEST": config("RATE_LIMIT_PASSWORD_RESET_REQUEST", default="3/m"),
    "PASSWORD_RESET_CONFIRM": config("RATE_LIMIT_PASSWORD_RESET_CONFIRM", default="5/m"),
    "EMAIL_VERIFICATION": config("RATE_LIMIT_EMAIL_VERIFICATION", default="10/m"),
    "PROFILE_UPDATE": config("RATE_LIMIT_PROFILE_UPDATE", default="10/m"),
    "USERNAME_UPDATE": config("RATE_LIMIT_USERNAME_UPDATE", default="5/m"),
    "LOGOUT": config("RATE_LIMIT_LOGOUT", default="5/m"),
    "TOKEN_REFRESH": config("RATE_LIMIT_TOKEN_REFRESH", default="30/m"),
    "TOKEN_VERIFY": config("RATE_LIMIT_TOKEN_VERIFY", default="30/m"),
    "DATA_EXPORT": config("RATE_LIMIT_DATA_EXPORT", default="10/m"),
}

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "clinical",
    "research",
    "shared",
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",  # API documentation
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS Configuration
# Note: CORS_ALLOW_CREDENTIALS and CORS_ALLOWED_ORIGINS are set in environment-specific settings
# These additional settings ensure proper CORS header handling for all requests
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# Base database configuration (to be overridden in environment-specific settings)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("ACCOUNTS_DB_NAME", default="observer_accounts"),
        "USER": config("ACCOUNTS_DB_USER", default=config("DB_USER")),
        "PASSWORD": config("ACCOUNTS_DB_PASSWORD", default=config("DB_PASSWORD")),
        "HOST": config("ACCOUNTS_DB_HOST", default=config("DB_HOST")),
        "PORT": config("ACCOUNTS_DB_PORT", default=config("DB_PORT")),
    },
    "accounts": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("ACCOUNTS_DB_NAME", default="observer_accounts"),
        "USER": config("ACCOUNTS_DB_USER", default=config("DB_USER")),
        "PASSWORD": config("ACCOUNTS_DB_PASSWORD", default=config("DB_PASSWORD")),
        "HOST": config("ACCOUNTS_DB_HOST", default=config("DB_HOST")),
        "PORT": config("ACCOUNTS_DB_PORT", default=config("DB_PORT")),
    },
    "clinical": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("CLINICAL_DB_NAME", default="observer_clinical"),
        "USER": config("CLINICAL_DB_USER", default=config("DB_USER")),
        "PASSWORD": config("CLINICAL_DB_PASSWORD", default=config("DB_PASSWORD")),
        "HOST": config("CLINICAL_DB_HOST", default=config("DB_HOST")),
        "PORT": config("CLINICAL_DB_PORT", default=config("DB_PORT")),
    },
    "research": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("RESEARCH_DB_NAME", default="observer_research"),
        "USER": config("RESEARCH_DB_USER", default=config("DB_USER")),
        "PASSWORD": config("RESEARCH_DB_PASSWORD", default=config("DB_PASSWORD")),
        "HOST": config("RESEARCH_DB_HOST", default=config("DB_HOST")),
        "PORT": config("RESEARCH_DB_PORT", default=config("DB_PORT")),
    },
}

# Database routing
DATABASE_ROUTERS = ["shared.db_router.DatabaseRouter"]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "user_attributes": ("username", "first_name", "last_name", "email"),
            "max_similarity": 0.7,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Media files (user uploads, videos, etc.)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Azure Data Lake Storage settings
AZURE_STORAGE_ACCOUNT_NAME = config("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_FILE_SYSTEM_NAME = config("AZURE_STORAGE_FILE_SYSTEM_NAME")
AZURE_SAS_TOKEN = config("AZURE_SAS_TOKEN")

# REST Framework base configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "shared.authentication.CookieJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # Fallback
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # API Versioning Strategy
    # - Uses namespace-based versioning (e.g., /api/v1/, /api/v2/)
    # - Current version: v1
    # - Deprecation policy: Maintain N-1 versions for 6 months minimum
    # - Breaking changes require new version number
    # - Version should be included in response headers
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],  # Add 'v2' when ready for new version
    "VERSION_PARAM": "version",
    # Pagination
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "MAX_PAGE_SIZE": 100,  # Prevent DoS via large page sizes
    # API Documentation
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# API Documentation Configuration (drf-spectacular)
SPECTACULAR_SETTINGS = {
    "TITLE": "Observer API",
    "DESCRIPTION": "Healthcare platform for medical encounter data collection, analysis, and visualization",
    "VERSION": API_VERSION,
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/v[0-9]",
}

# JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=15, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=1, cast=int)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Email Configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL", default="Observer Platform <noreply@observer.com>"
)

# Frontend URL for email verification links
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")

# Email Domain Validation
# Allowed email domains for registration (institutional domains)
ALLOWED_EMAIL_DOMAINS = config(
    "ALLOWED_EMAIL_DOMAINS",
    default="edu,ac.uk,gov,mil",
    cast=lambda v: [d.strip() for d in v.split(",")],
)

# Test domains allowed in development mode (controlled by DEBUG or ALLOW_TEST_EMAILS)
TEST_EMAIL_DOMAINS = config(
    "TEST_EMAIL_DOMAINS",
    default="gmail.com,outlook.com,yahoo.com",
    cast=lambda v: [d.strip() for d in v.split(",")],
)

# Set to True to allow test email domains regardless of DEBUG setting
ALLOW_TEST_EMAILS = config("ALLOW_TEST_EMAILS", default=False, cast=bool)
