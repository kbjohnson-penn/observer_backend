from django.urls import path

from search.api.views.search_views import EncounterSearchView

urlpatterns = [
    path("encounters/", EncounterSearchView.as_view(), name="encounter-search"),
]
