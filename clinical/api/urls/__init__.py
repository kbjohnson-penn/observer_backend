from django.urls import path, include

app_name = 'clinical_api'

urlpatterns = [
    path('private/', include('clinical.api.urls.private_urls')),
    path('public/', include('clinical.api.urls.public_urls')),
]