"""
Cohort model for saving user's research filter configurations.

A cohort represents a saved set of filter criteria that a user can reuse
for querying research data. Cohorts can originate from two sources:

- **research**: Dashboard research tab (nested VisitSearchFilters format)
- **search**: Encounter Search page (flat EncounterSearchFilters format)

Optionally, a cohort may store explicit encounter IDs instead of (or in
addition to) filter criteria, enabling users to hand-pick specific visits.
"""

from django.conf import settings
from django.db import models


class Cohort(models.Model):
    """
    Represents a saved cohort (filtered set of visits) for research purposes.

    A cohort can be created from two sources:
    - **research**: Dashboard research tab — filters stored in nested VisitSearchFilters format
    - **search**: Encounter Search page — filters stored in flat EncounterSearchFilters format

    Optionally stores ``encounter_ids`` for hand-picked visit selections.

    Database:
        Routed to 'accounts' database via DatabaseRouter (same as User model).
        Table: cohort
    """

    id = models.AutoField(primary_key=True, verbose_name="Cohort ID")

    # Ownership
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cohorts",
        help_text="The user who created this cohort",
    )

    # Basic Info
    name = models.CharField(max_length=255, help_text="User-friendly name for the cohort")
    description = models.TextField(
        blank=True, default="", help_text="Optional description of the cohort's purpose"
    )

    # Source discriminator
    SOURCE_RESEARCH = "research"
    SOURCE_SEARCH = "search"
    SOURCE_CHOICES = [
        (SOURCE_RESEARCH, "Research Tab"),
        (SOURCE_SEARCH, "Encounter Search"),
    ]
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_RESEARCH,
        help_text="Origin of the cohort: 'research' for nested filters, 'search' for flat ES filters",
    )

    # Filter Configuration (JSON)
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filter criteria as JSON (format depends on source field)",
    )

    # Optional: explicit encounter IDs (for hand-picked cohorts)
    encounter_ids = models.JSONField(
        null=True,
        blank=True,
        default=None,
        help_text="Optional list of encounter ID strings. When set, overrides filter-based lookup.",
    )

    # Free-text query captured from Encounter Search
    search_query = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Free-text search query (only used when source='search')",
    )

    # Metadata
    visit_count = models.IntegerField(
        help_text="Number of visits matching filters at creation time"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        db_table = "cohort"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["name"]),
            models.Index(fields=["source"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.visit_count} visits) - {self.user.username}"
