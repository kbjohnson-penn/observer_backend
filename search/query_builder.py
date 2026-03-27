"""
Elasticsearch query builder for Observer encounter search.
"""

import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


# Characters that have special meaning in Lucene query syntax
_LUCENE_SPECIAL = re.compile(r'([+\-!(){}[\]^"~*?:\\/]|\|\||&&)')


def _escape_query(text: str) -> str:
    """Escape Lucene special characters in a free-text query string."""
    return _LUCENE_SPECIAL.sub(r"\\\1", text)


def get_note_match_ids(
    es: "Elasticsearch",
    texts_index: str,
    query_text: str,
    user_tier: int | None,
    is_superuser: bool,
) -> list[str]:
    """
    Query the texts index for note content matching query_text.
    Returns a list of encounter_id strings that have matching notes.
    Respects tier access the same way as the encounters index.
    """
    tier_filter: list[dict] = []
    if not is_superuser:
        if user_tier is not None:
            # gt:0 excludes unassigned (tier_level=0) docs, matching encounters index behaviour
            tier_filter.append({"range": {"tier_level": {"gt": 0, "lte": user_tier}}})
        else:
            return []

    body = {
        "size": 0,
        "query": {
            "bool": {
                "must": [{"match": {"text": query_text}}],
                "filter": tier_filter,
            }
        },
        "aggs": {
            "encounter_ids": {
                # NOTE: caps at 10,000 unique encounter IDs. If the dataset grows
                # beyond ~10k note-matching encounters, switch to a composite
                # aggregation to paginate buckets without truncation.
                "terms": {"field": "encounter_id", "size": 10000}
            }
        },
    }
    try:
        response = es.search(index=texts_index, body=body)
        return [bucket["key"] for bucket in response["aggregations"]["encounter_ids"]["buckets"]]
    except Exception:
        logger.warning("Note text search failed; returning empty match list.", exc_info=True)
        return []


def build_encounter_search_query(
    query_text: str,
    filters: dict,
    user_tier: int | None,
    is_superuser: bool,
    page: int,
    page_size: int,
    sort: dict | None = None,
    note_match_ids: list[str] | None = None,
) -> dict:
    """
    Build an Elasticsearch bool query for the observer-encounters index.

    Args:
        query_text: Free-text search string (may be empty).
        filters: Dict of structured filter values (see SearchRequestSerializer).
        user_tier: The authenticated user's tier level (1-5), or None for superusers.
        is_superuser: If True, skip tier filter entirely.
        page: 1-based page number.
        page_size: Number of results per page.
        sort: Optional dict of sort criteria e.g. {"visit_date": "desc"}.
        note_match_ids: Encounter IDs whose notes matched the query (from texts index).
                        When provided, encounters with matching notes are boosted via should.

    Returns:
        A dict suitable for passing to ``es.search(body=...)``.
    """
    filter_clauses: list[dict] = []

    # ---- Build the match clause ----
    # An encounter is returned if it matches via its own fields (icd_codes, drug_names, etc.)
    # OR if any of its notes matched the same query text (note_match_ids from texts index).
    # Using should + minimum_should_match=1 achieves the OR; both paths boost _score.
    should: list[dict] = []

    if query_text and query_text.strip():
        escaped = _escape_query(query_text.strip())
        should.append(
            {
                "multi_match": {
                    "query": escaped,
                    "fields": [
                        "icd_codes.text^2",
                        "condition_descriptions.text^2",
                        "cpt_codes.text^2",
                        "procedure_descriptions.text^2",
                        "drug_names.text^2",
                        "note_types",
                        "patient_gender",
                        "patient_race",
                        "patient_ethnicity",
                        "provider_gender",
                        "provider_race",
                        "provider_ethnicity",
                        "file_types",
                    ],
                    "type": "best_fields",
                }
            }
        )

    if note_match_ids:
        should.append({"terms": {"encounter_id": note_match_ids, "boost": 1.5}})

    # must stays empty when we have should clauses with minimum_should_match
    must: list[dict] = [] if should else [{"match_all": {}}]

    # ---- Tier filter ----
    if not is_superuser:
        if user_tier is not None:
            # Mirrors filter_queryset_by_user_tier: gt:0 excludes unassigned (tier_level=0) docs
            filter_clauses.append({"range": {"tier_level": {"gt": 0, "lte": user_tier}}})
        else:
            # No tier assigned — exclude everything by requiring a field value that never exists
            filter_clauses.append({"range": {"tier_level": {"lt": 0}}})

    # ---- Structured filters ----
    _apply_filters(filter_clauses, filters)

    # ---- Aggregations ----
    aggs = _build_aggregations()

    # ---- Highlight ----
    highlight = {
        "pre_tags": ["<mark>"],
        "post_tags": ["</mark>"],
        "fields": {
            "icd_codes.text": {"number_of_fragments": 0},
            "cpt_codes.text": {"number_of_fragments": 0},
            "drug_names.text": {"number_of_fragments": 0},
            "condition_descriptions.text": {"number_of_fragments": 0},
            "procedure_descriptions.text": {"number_of_fragments": 0},
        },
    }

    # ---- Sort ----
    sort_clause = _build_sort(sort)

    bool_query: dict[str, Any] = {"filter": filter_clauses}
    if should:
        bool_query["should"] = should
        bool_query["minimum_should_match"] = 1
    else:
        bool_query["must"] = must

    query: dict[str, Any] = {
        "from": (page - 1) * page_size,
        "size": page_size,
        "query": {"bool": bool_query},
        "aggs": aggs,
        "highlight": highlight,
        "sort": sort_clause,
    }

    return query


def _apply_filters(filter_clauses: list, filters: dict) -> None:
    """Translate validated filter dict into ES filter clauses (in-place)."""
    if not filters:
        return

    # Date range
    date_from = filters.get("date_from")
    date_to = filters.get("date_to")
    if date_from or date_to:
        date_range: dict = {}
        if date_from:
            date_range["gte"] = date_from
        if date_to:
            date_range["lte"] = date_to
        filter_clauses.append({"range": {"visit_date": date_range}})

    # Keyword array filters
    _add_terms_filter(filter_clauses, filters, "department")
    _add_terms_filter(filter_clauses, filters, "icd_codes")
    _add_terms_filter(filter_clauses, filters, "cpt_codes")
    _add_text_filter(filter_clauses, filters, "drug_names")
    _add_terms_filter(filter_clauses, filters, "note_types")
    _add_terms_filter(filter_clauses, filters, "patient_gender")
    _add_terms_filter(filter_clauses, filters, "patient_race")
    _add_terms_filter(filter_clauses, filters, "patient_ethnicity")
    _add_terms_filter(filter_clauses, filters, "provider_gender")
    _add_terms_filter(filter_clauses, filters, "provider_race")
    _add_terms_filter(filter_clauses, filters, "provider_ethnicity")

    # Boolean capability filters
    for field in (
        "has_transcript",
        "has_audio",
        "has_provider_view",
        "has_patient_view",
        "has_room_view",
        "has_notes",
    ):
        if field in filters and filters[field] is not None:
            filter_clauses.append({"term": {field: filters[field]}})


def _add_terms_filter(filter_clauses: list, filters: dict, field: str) -> None:
    value = filters.get(field)
    if value:
        if isinstance(value, list) and value:
            filter_clauses.append({"terms": {field: value}})
        elif isinstance(value, str) and value:
            filter_clauses.append({"term": {field: value}})


def _add_text_filter(filter_clauses: list, filters: dict, field: str) -> None:
    """Use the analyzed .text subfield for case-insensitive partial matching.

    When multiple values are supplied the semantics are OR: an encounter
    matches if it contains ANY of the supplied terms.  Each individual term
    still uses operator="and" so all tokens within a single value must appear
    (e.g. "metformin hcl" requires both tokens).
    """
    value = filters.get(field)
    if not value:
        return
    terms = [value] if isinstance(value, str) else value
    should = [{"match": {f"{field}.text": {"query": term, "operator": "and"}}} for term in terms]
    if len(should) == 1:
        filter_clauses.append(should[0])
    else:
        # Multiple values → OR: match encounters that contain at least one of the terms.
        filter_clauses.append({"bool": {"should": should, "minimum_should_match": 1}})


def _build_aggregations() -> dict:
    return {
        "departments": {"terms": {"field": "department", "size": 50}},
        "patient_genders": {"terms": {"field": "patient_gender", "size": 20}},
        "patient_races": {"terms": {"field": "patient_race", "size": 20}},
        "patient_ethnicities": {"terms": {"field": "patient_ethnicity", "size": 20}},
        "provider_genders": {"terms": {"field": "provider_gender", "size": 20}},
        "provider_races": {"terms": {"field": "provider_race", "size": 20}},
        "provider_ethnicities": {"terms": {"field": "provider_ethnicity", "size": 20}},
        "tier_distribution": {"terms": {"field": "tier_level", "size": 5}},
        "note_types": {"terms": {"field": "note_types", "size": 30}},
        "file_types": {"terms": {"field": "file_types", "size": 20}},
    }


def _build_sort(sort: dict | None) -> list:
    allowed_fields = {"visit_date", "_score", "tier_level"}
    if not sort:
        return [{"_score": "desc"}, {"visit_date": "desc"}]

    clauses = []
    for field, direction in sort.items():
        if field in allowed_fields and direction in ("asc", "desc"):
            clauses.append({field: direction})

    return clauses if clauses else [{"_score": "desc"}, {"visit_date": "desc"}]


def build_search_response(
    es_response: dict,
    page: int,
    page_size: int,
    base_url: str = "",
    note_match_ids: set[str] | None = None,
) -> dict:
    """Format a raw Elasticsearch response into the Observer API response shape."""
    hits = es_response.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    raw_hits = hits.get("hits", [])

    results = []
    for hit in raw_hits:
        src = dict(hit.get("_source", {}))  # shallow copy — avoids mutating the ES response object
        highlight = hit.get("highlight") or {}
        src["highlights"] = dict(highlight)

        matched_in: list[str] = []
        if highlight.get("icd_codes.text"):
            matched_in.append("ICD codes")
        if highlight.get("condition_descriptions.text"):
            matched_in.append("Diagnoses")
        if highlight.get("cpt_codes.text") or highlight.get("procedure_descriptions.text"):
            matched_in.append("Procedures")
        if highlight.get("drug_names.text"):
            matched_in.append("Drugs")
        if note_match_ids and src.get("encounter_id") in note_match_ids:
            matched_in.append("Notes")
        src["matched_in"] = matched_in

        results.append(src)

    # Pagination links — these are informational indicators only.
    # Because this is a POST endpoint, the authoritative search state lives in
    # the request body.  Clients (including the frontend useSearch hook) should
    # re-POST with an incremented `page` field rather than following these URLs.
    # The URLs only carry `?page=N` so that API browsers can see which pages
    # exist; they do NOT reproduce filters or sort parameters.
    next_page = page + 1 if (page * page_size) < total else None
    prev_page = page - 1 if page > 1 else None

    def page_url(p: int | None) -> str | None:
        if p is None:
            return None
        return f"{base_url}?page={p}"

    # Aggregations
    raw_aggs = es_response.get("aggregations", {})
    aggregations = {
        key: [
            {"key": bucket["key"], "count": bucket["doc_count"]}
            for bucket in agg_data.get("buckets", [])
        ]
        for key, agg_data in raw_aggs.items()
    }

    return {
        "count": total,
        "page": page,
        "page_size": page_size,
        "next": page_url(next_page),
        "previous": page_url(prev_page),
        "results": results,
        "aggregations": aggregations,
    }
