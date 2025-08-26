from django.urls import path, include

app_name = 'research_api'

urlpatterns = [
    path('public/', include('research.api.urls.public_urls')),
]