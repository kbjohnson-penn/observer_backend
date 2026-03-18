"""
Phase 5 stub: load transcripts and debriefs exported from Databricks into observer-texts.

This command will be implemented in Phase 5 once the Databricks export pipeline
(WhisperX transcription + MedSpaCy NER + MedCPT embeddings) is complete.

Usage (Phase 5):
    python manage.py load_texts_to_es --file /path/to/export.parquet --source-type exam_video
    python manage.py load_texts_to_es --file /path/to/debriefs.csv --source-type debrief
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load Databricks-exported transcripts into observer-texts (Phase 5)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            required=False,
            help="Path to Parquet or CSV export file from Databricks",
        )
        parser.add_argument(
            "--source-type",
            choices=["exam_video", "debrief"],
            required=False,
            help="Source type for the text documents",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "Not yet implemented. "
                "Use this command in Phase 5 to load Databricks transcript exports "
                "into the observer-texts Elasticsearch index."
            )
        )
