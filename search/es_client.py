"""
Elasticsearch client singleton for the Observer search app.

The client is instantiated at module load time (after Django settings are ready)
so there is no lazy-init race condition under multi-threaded gunicorn workers.
"""

import logging

from django.conf import settings

from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)

_client: Elasticsearch = Elasticsearch(
    hosts=[settings.ELASTICSEARCH_HOST],
    request_timeout=settings.ELASTICSEARCH_TIMEOUT,
)


def get_es_client() -> Elasticsearch:
    """Return the shared Elasticsearch client."""
    return _client


def ping_es() -> bool:
    """Return True if Elasticsearch is reachable."""
    try:
        return get_es_client().ping()
    except Exception:
        logger.exception("Elasticsearch ping failed")
        return False
