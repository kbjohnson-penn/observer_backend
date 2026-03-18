"""
Elasticsearch index mappings for Observer search indexes.
"""

import logging

from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)

ENCOUNTERS_INDEX_MAPPING: dict = {
    "settings": {
        "analysis": {
            "tokenizer": {
                "clinical_code_tokenizer": {
                    "type": "pattern",
                    "pattern": "[.\\s]+",
                }
            },
            "analyzer": {
                "clinical_code_analyzer": {
                    "type": "custom",
                    "tokenizer": "clinical_code_tokenizer",
                    "filter": ["lowercase"],
                }
            },
        }
    },
    "mappings": {
        "properties": {
            # Visit identifiers (de-identified)
            "encounter_id": {"type": "keyword"},
            "visit_source_value": {"type": "keyword"},
            "visit_source_id": {"type": "integer"},
            "visit_date": {"type": "date"},
            "department": {"type": "keyword"},
            # Patient demographics (de-identified — no name)
            "patient_gender": {"type": "keyword"},
            "patient_race": {"type": "keyword"},
            "patient_ethnicity": {"type": "keyword"},
            "patient_year_of_birth": {"type": "integer"},
            # Provider demographics (de-identified — no name)
            "provider_gender": {"type": "keyword"},
            "provider_race": {"type": "keyword"},
            "provider_ethnicity": {"type": "keyword"},
            "provider_year_of_birth": {"type": "integer"},
            # Multimodal flags (derived from Observation.file_type)
            "has_transcript": {"type": "boolean"},
            "has_audio": {"type": "boolean"},
            "has_provider_view": {"type": "boolean"},
            "has_patient_view": {"type": "boolean"},
            "has_room_view": {"type": "boolean"},
            "file_types": {"type": "keyword"},
            # Clinical data (all from research DB)
            # keyword used for exact/filter queries; text sub-field tokenized for free-text search
            # icd_codes/cpt_codes use clinical_code_analyzer to split on "." so "R73" matches "R73.03"
            "icd_codes": {
                "type": "keyword",
                "fields": {"text": {"type": "text", "analyzer": "clinical_code_analyzer"}},
            },
            "cpt_codes": {
                "type": "keyword",
                "fields": {"text": {"type": "text", "analyzer": "clinical_code_analyzer"}},
            },
            "drug_names": {"type": "keyword", "fields": {"text": {"type": "text"}}},
            "condition_descriptions": {"type": "keyword", "fields": {"text": {"type": "text"}}},
            "procedure_descriptions": {"type": "keyword", "fields": {"text": {"type": "text"}}},
            "drug_count": {"type": "integer"},
            "has_notes": {"type": "boolean"},
            "note_types": {"type": "keyword"},
            "note_count": {"type": "integer"},
            # Access control
            "tier_level": {"type": "integer"},
        }
    },
}

TEXTS_INDEX_MAPPING: dict = {
    "mappings": {
        "properties": {
            "encounter_id": {"type": "keyword"},
            "source_type": {"type": "keyword"},
            "text": {"type": "text", "analyzer": "english"},
            "speaker_label": {"type": "keyword"},
            "note_type": {"type": "keyword"},
            "entities": {
                "type": "nested",
                "properties": {
                    "text": {"type": "text"},
                    "label": {"type": "keyword"},
                    "cui": {"type": "keyword"},
                },
            },
            "embedding": {
                "type": "dense_vector",
                "dims": 768,
                # kNN index enabled in Phase 6. Enabling it on a live index requires
                # a full reindex: manage.py sync_elasticsearch --full-reindex --confirm
                "index": False,
            },
            "segment_start": {"type": "float"},
            "segment_end": {"type": "float"},
            "tier_level": {"type": "integer"},
        }
    }
}


def create_index_if_not_exists(es: Elasticsearch, index_name: str, mapping: dict) -> bool:
    """
    Create an ES index with the given mapping if it does not already exist.
    Returns True if the index was created, False if it already existed.
    """
    if es.indices.exists(index=index_name):
        logger.debug("Index '%s' already exists, skipping creation.", index_name)
        return False
    es.indices.create(index=index_name, body=mapping)
    logger.info("Created Elasticsearch index '%s'.", index_name)
    return True
