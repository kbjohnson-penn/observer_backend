"""
Search views for the Observer search API.
"""

import logging

from django.conf import settings
from django.utils.decorators import method_decorator

from django_ratelimit.decorators import ratelimit
from elasticsearch import ConnectionError as ESConnectionError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from search.api.serializers.search_serializers import SearchRequestSerializer
from search.es_client import get_es_client
from search.query_builder import (
    build_encounter_search_query,
    build_search_response,
    get_note_match_ids,
)
from shared.api.permissions import get_user_tier

logger = logging.getLogger(__name__)


@method_decorator(
    ratelimit(key="user", rate=settings.RATE_LIMITS["SEARCH"], method="POST", block=True),
    name="post",
)
class EncounterSearchView(APIView):
    """
    POST /api/v1/search/private/encounters/

    Search the observer-encounters Elasticsearch index using keyword filters
    and optional free-text query. Returns paginated, tier-filtered results
    with aggregations for faceted navigation.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        # data["search_type"] is validated by the serializer but not yet consumed here.
        # It is reserved for Phase 6 semantic search (kNN via the embedding field).
        user = request.user
        is_superuser = user.is_superuser
        user_tier = get_user_tier(user)

        base_url = request.build_absolute_uri(request.path)

        try:
            es = get_es_client()

            # If there is a free-text query, also search note content in the texts index
            note_match_ids: list[str] = []
            if data["query"]:
                note_match_ids = get_note_match_ids(
                    es=es,
                    texts_index=settings.ELASTICSEARCH_INDEX_TEXTS,
                    query_text=data["query"],
                    user_tier=user_tier,
                    is_superuser=is_superuser,
                )

            query = build_encounter_search_query(
                query_text=data["query"],
                filters=data["filters"],
                user_tier=user_tier,
                is_superuser=is_superuser,
                page=data["page"],
                page_size=data["page_size"],
                sort=data["sort"],
                note_match_ids=note_match_ids,
            )

            es_response = es.search(index=settings.ELASTICSEARCH_INDEX_ENCOUNTERS, body=query)
        except ESConnectionError:
            logger.error("Elasticsearch is unreachable.")
            return Response(
                {"detail": "Search service is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception:
            logger.exception("Unexpected error during Elasticsearch search.")
            return Response(
                {"detail": "An unexpected error occurred while searching."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_data = build_search_response(
            es_response=es_response,
            page=data["page"],
            page_size=data["page_size"],
            base_url=base_url,
            note_match_ids=set(note_match_ids),
        )
        return Response(response_data, status=status.HTTP_200_OK)
