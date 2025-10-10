"""
Base settings shared across all environments
"""
from pathlib import Path
from decouple import config
import os
import pymysql
from datetime import timedelta

pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

APPEND_SLASH = True

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Basic Security Settings
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'clinical',
    'research',
    'shared',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Base database configuration (to be overridden in environment-specific settings)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('ACCOUNTS_DB_NAME', default='observer_accounts'),
        'USER': config('ACCOUNTS_DB_USER', default=config('DB_USER')),
        'PASSWORD': config('ACCOUNTS_DB_PASSWORD', default=config('DB_PASSWORD')),
        'HOST': config('ACCOUNTS_DB_HOST', default=config('DB_HOST')),
        'PORT': config('ACCOUNTS_DB_PORT', default=config('DB_PORT')),
    },
    'accounts': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('ACCOUNTS_DB_NAME', default='observer_accounts'),
        'USER': config('ACCOUNTS_DB_USER', default=config('DB_USER')),
        'PASSWORD': config('ACCOUNTS_DB_PASSWORD', default=config('DB_PASSWORD')),
        'HOST': config('ACCOUNTS_DB_HOST', default=config('DB_HOST')),
        'PORT': config('ACCOUNTS_DB_PORT', default=config('DB_PORT')),
    },
    'clinical': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('CLINICAL_DB_NAME', default='observer_clinical'),
        'USER': config('CLINICAL_DB_USER', default=config('DB_USER')),
        'PASSWORD': config('CLINICAL_DB_PASSWORD', default=config('DB_PASSWORD')),
        'HOST': config('CLINICAL_DB_HOST', default=config('DB_HOST')),
        'PORT': config('CLINICAL_DB_PORT', default=config('DB_PORT')),
    },
    'research': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('RESEARCH_DB_NAME', default='observer_research'),
        'USER': config('RESEARCH_DB_USER', default=config('DB_USER')),
        'PASSWORD': config('RESEARCH_DB_PASSWORD', default=config('DB_PASSWORD')),
        'HOST': config('RESEARCH_DB_HOST', default=config('DB_HOST')),
        'PORT': config('RESEARCH_DB_PORT', default=config('DB_PORT')),
    }
}

# Database routing
DATABASE_ROUTERS = ['shared.db_router.DatabaseRouter']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'first_name', 'last_name', 'email'),
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media files (user uploads, videos, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Azure Data Lake Storage settings
AZURE_STORAGE_ACCOUNT_NAME = config('AZURE_STORAGE_ACCOUNT_NAME')
AZURE_STORAGE_FILE_SYSTEM_NAME = config('AZURE_STORAGE_FILE_SYSTEM_NAME')
AZURE_SAS_TOKEN = config('AZURE_SAS_TOKEN')

# REST Framework base configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'shared.authentication.CookieJWTAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Fallback
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Observer Platform <noreply@observer.com>')

# Frontend URL for email verification links
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')