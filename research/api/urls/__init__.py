from django.urls import include, path

app_name = "research_api"

urlpatterns = [
    path("private/", include("research.api.urls.private_urls")),
    path("public/", include("research.api.urls.public_urls")),
]
