from django.conf import settings


def documentation_url(request):
    return {'DOCUMENTATION_URL': settings.DOCUMENTATION_URL}
