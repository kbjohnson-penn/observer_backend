"""
Management command to sync Observer data into Elasticsearch.

All data sourced exclusively from the research DB (de-identified OMOP dataset).
No clinical DB access — clinical DB contains PHI.

Usage:
    python manage.py sync_elasticsearch
    python manage.py sync_elasticsearch --index=encounters
    python manage.py sync_elasticsearch --index=texts
    python manage.py sync_elasticsearch --full-reindex
    python manage.py sync_elasticsearch --batch-size=200
"""

import logging
from collections import defaultdict

from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch.helpers import bulk

from research.models import (
    ConditionOccurrence,
    DrugExposure,
    Note,
    Observation,
    ProcedureOccurrence,
    VisitOccurrence,
)
from search.es_client import get_es_client
from search.index_mappings import (
    ENCOUNTERS_INDEX_MAPPING,
    TEXTS_INDEX_MAPPING,
    create_index_if_not_exists,
)

logger = logging.getLogger(__name__)

# Observation.file_type values that map to multimodal boolean flags
_MULTIMODAL_FLAGS = {
    "has_transcript": "transcript",
    "has_audio": "audio",
    "has_provider_view": "provider_view",
    "has_patient_view": "patient_view",
    "has_room_view": "room_view",
}


class Command(BaseCommand):
    help = "Sync Observer data into Elasticsearch from research DB only (no PHI)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--index",
            choices=["encounters", "texts", "all"],
            default="all",
            help="Which index to sync (default: all)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Number of visits to process per batch (default: 500)",
        )
        parser.add_argument(
            "--full-reindex",
            action="store_true",
            default=False,
            help="Delete and recreate indexes before syncing (requires --confirm)",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            default=False,
            help="Confirm destructive operations such as --full-reindex",
        )

    def handle(self, *args, **options):
        es = get_es_client()
        index = options["index"]
        batch_size = options["batch_size"]
        full_reindex = options["full_reindex"]

        if full_reindex:
            if not options["confirm"]:
                self.stderr.write(
                    self.style.WARNING(
                        "--full-reindex will delete and recreate all search indexes. "
                        "Pass --confirm to proceed."
                    )
                )
                return
            self._delete_indexes(es, index)

        if index in ("encounters", "all"):
            create_index_if_not_exists(
                es, settings.ELASTICSEARCH_INDEX_ENCOUNTERS, ENCOUNTERS_INDEX_MAPPING
            )
            self._sync_encounters(es, batch_size)

        if index in ("texts", "all"):
            create_index_if_not_exists(es, settings.ELASTICSEARCH_INDEX_TEXTS, TEXTS_INDEX_MAPPING)
            self._sync_texts(es, batch_size)

        self.stdout.write(self.style.SUCCESS("Elasticsearch sync complete."))

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def _delete_indexes(self, es, index: str) -> None:
        targets = []
        if index in ("encounters", "all"):
            targets.append(settings.ELASTICSEARCH_INDEX_ENCOUNTERS)
        if index in ("texts", "all"):
            targets.append(settings.ELASTICSEARCH_INDEX_TEXTS)

        for idx in targets:
            if es.indices.exists(index=idx):
                es.indices.delete(index=idx)
                self.stdout.write(f"Deleted index '{idx}'.")

    # ------------------------------------------------------------------
    # Encounter sync — research DB only
    # ------------------------------------------------------------------

    def _build_encounter_lookup_maps(self, visit_ids: list) -> dict:
        """Build per-visit lookup dicts for all related data in one pass each."""
        visit_to_file_types: dict[int, set[str]] = defaultdict(set)
        for row in (
            Observation.objects.using("research")
            .filter(visit_occurrence_id__in=visit_ids)
            .values("visit_occurrence_id", "file_type")
        ):
            if row["file_type"]:
                visit_to_file_types[row["visit_occurrence_id"]].add(row["file_type"])

        visit_to_icds: dict[int, list[str]] = defaultdict(list)
        visit_to_condition_descs: dict[int, list[str]] = defaultdict(list)
        for row in (
            ConditionOccurrence.objects.using("research")
            .filter(visit_occurrence_id__in=visit_ids)
            .values("visit_occurrence_id", "concept_code", "condition_source_value")
        ):
            if row["concept_code"]:
                visit_to_icds[row["visit_occurrence_id"]].append(row["concept_code"])
            if row["condition_source_value"]:
                visit_to_condition_descs[row["visit_occurrence_id"]].append(
                    row["condition_source_value"]
                )

        visit_to_cpts: dict[int, list[str]] = defaultdict(list)
        visit_to_proc_descs: dict[int, list[str]] = defaultdict(list)
        for row in (
            ProcedureOccurrence.objects.using("research")
            .filter(visit_occurrence_id__in=visit_ids)
            .values("visit_occurrence_id", "name", "description")
        ):
            if row["name"]:
                visit_to_cpts[row["visit_occurrence_id"]].append(row["name"])
            if row["description"]:
                visit_to_proc_descs[row["visit_occurrence_id"]].append(row["description"])

        visit_to_drug_names: dict[int, list[str]] = defaultdict(list)
        for row in (
            DrugExposure.objects.using("research")
            .filter(visit_occurrence_id__in=visit_ids)
            .values("visit_occurrence_id", "description")
        ):
            if row["description"]:
                visit_to_drug_names[row["visit_occurrence_id"]].append(row["description"])

        visit_to_note_types: dict[int, list[str]] = defaultdict(list)
        for row in (
            Note.objects.using("research")
            .filter(visit_occurrence_id__in=visit_ids)
            .values("visit_occurrence_id", "note_type")
        ):
            if row["note_type"]:
                visit_to_note_types[row["visit_occurrence_id"]].append(row["note_type"])

        return {
            "file_types": visit_to_file_types,
            "icds": visit_to_icds,
            "condition_descs": visit_to_condition_descs,
            "cpts": visit_to_cpts,
            "proc_descs": visit_to_proc_descs,
            "drug_names": visit_to_drug_names,
            "note_types": visit_to_note_types,
        }

    def _build_encounter_doc(self, visit, maps: dict) -> dict:
        """Build a single Elasticsearch action document for a VisitOccurrence."""
        vid = visit.id
        file_types = maps["file_types"].get(vid, set())
        raw_drug_names = maps["drug_names"].get(vid, [])
        drug_names = list(set(raw_drug_names))  # unique drug names for filtering/display
        note_types = list(set(maps["note_types"].get(vid, [])))  # unique note type labels
        return {
            "_index": settings.ELASTICSEARCH_INDEX_ENCOUNTERS,
            "_id": str(vid),
            "_source": {
                "encounter_id": str(vid),
                "visit_source_value": visit.visit_source_value,
                "visit_source_id": visit.visit_source_id,
                "visit_date": (
                    visit.visit_start_date.isoformat() if visit.visit_start_date else None
                ),
                "department": (visit.department or None),
                "patient_gender": (
                    (visit.person.gender_source_value or None) if visit.person else None
                ),
                "patient_race": (visit.person.race_source_value or None) if visit.person else None,
                "patient_ethnicity": (
                    (visit.person.ethnicity_source_value or None) if visit.person else None
                ),
                "patient_year_of_birth": visit.person.year_of_birth if visit.person else None,
                "provider_gender": (
                    (visit.provider.gender_source_value or None) if visit.provider else None
                ),
                "provider_race": (
                    (visit.provider.race_source_value or None) if visit.provider else None
                ),
                "provider_ethnicity": (
                    (visit.provider.ethnicity_source_value or None) if visit.provider else None
                ),
                "provider_year_of_birth": (
                    visit.provider.year_of_birth if visit.provider else None
                ),
                "has_transcript": "transcript" in file_types,
                "has_audio": "audio" in file_types,
                "has_provider_view": "provider_view" in file_types,
                "has_patient_view": "patient_view" in file_types,
                "has_room_view": "room_view" in file_types,
                "file_types": list(file_types),
                "icd_codes": list(set(maps["icds"].get(vid, []))),
                "condition_descriptions": list(set(maps["condition_descs"].get(vid, []))),
                "cpt_codes": list(set(maps["cpts"].get(vid, []))),
                "procedure_descriptions": list(set(maps["proc_descs"].get(vid, []))),
                "drug_names": drug_names,
                "drug_count": len(raw_drug_names),  # total drug exposures (not unique names)
                "has_notes": bool(note_types),
                "note_types": note_types,
                "note_count": len(
                    maps["note_types"].get(vid, [])
                ),  # total notes (not unique types)
                "tier_level": visit.tier_level,
            },
        }

    def _sync_encounters(self, es, batch_size: int) -> None:
        self.stdout.write("Syncing observer-encounters (research DB only) …")

        total_count = VisitOccurrence.objects.using("research").count()
        if not total_count:
            self.stdout.write("No visits found in research DB.")
            return

        # Process in batches to keep memory proportional to batch_size.
        # Each iteration: fetch one batch of visits, build lookup maps for only
        # that batch's IDs, index, then advance. Avoids loading all IDs or all
        # related rows into RAM at once (which would OOM on large OMOP datasets).
        # Uses ORDER BY id + LIMIT/OFFSET which is stable because id is a PK.
        total_synced = 0
        offset = 0
        while True:
            batch_qs = (
                VisitOccurrence.objects.using("research")
                .select_related("person", "provider")
                .order_by("id")[offset : offset + batch_size]
            )
            batch = list(batch_qs)
            if not batch:
                break

            batch_ids = [v.id for v in batch]
            maps = self._build_encounter_lookup_maps(batch_ids)
            actions = [self._build_encounter_doc(visit, maps) for visit in batch]

            success, errors = bulk(es, actions, raise_on_error=False, stats_only=False)
            total_synced += success
            if errors:
                logger.warning(
                    "%d bulk indexing errors in encounters batch at offset %d", len(errors), offset
                )

            offset += batch_size
            self.stdout.write(f"  … {total_synced} encounters indexed")

        self.stdout.write(
            self.style.SUCCESS(f"Encounters sync complete: {total_synced} documents.")
        )

    # ------------------------------------------------------------------
    # Texts sync (clinical notes from research DB)
    # ------------------------------------------------------------------

    def _sync_texts(self, es, batch_size: int) -> None:
        self.stdout.write("Syncing observer-texts (clinical notes from research DB) …")

        total_synced = 0
        actions = []

        for note in (
            Note.objects.using("research")
            .select_related("visit_occurrence")
            .iterator(chunk_size=batch_size)
        ):
            if note.visit_occurrence is None:
                logger.warning("Note %s has no visit_occurrence — skipping.", note.id)
                continue
            actions.append(
                {
                    "_index": settings.ELASTICSEARCH_INDEX_TEXTS,
                    "_id": f"note_{note.id}",
                    "_source": {
                        "encounter_id": str(note.visit_occurrence_id),
                        "source_type": "clinical_note",
                        "text": note.note_text,
                        "speaker_label": None,
                        "note_type": note.note_type,
                        "entities": [],
                        "embedding": None,
                        "segment_start": None,
                        "segment_end": None,
                        "tier_level": note.visit_occurrence.tier_level,
                    },
                }
            )

            if len(actions) >= batch_size:
                success, errors = bulk(es, actions, raise_on_error=False, stats_only=False)
                total_synced += success
                if errors:
                    logger.warning("%d bulk indexing errors in texts batch", len(errors))
                actions = []
                self.stdout.write(f"  … {total_synced} notes indexed")

        if actions:
            success, errors = bulk(es, actions, raise_on_error=False, stats_only=False)
            total_synced += success
            if errors:
                logger.warning("%d bulk indexing errors in final texts batch", len(errors))

        self.stdout.write(self.style.SUCCESS(f"Texts sync complete: {total_synced} documents."))
