"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings by default for WSGI
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.prd")

application = get_wsgi_application()
