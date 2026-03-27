from django.urls import include, path

app_name = "search_api"

urlpatterns = [
    path("private/", include("search.api.urls.private_urls")),
]
