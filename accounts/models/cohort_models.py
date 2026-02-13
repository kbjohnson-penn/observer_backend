"""
Cohort model for saving user's research filter configurations.

A cohort represents a saved set of filter criteria that a user can reuse
for querying research data. This allows researchers to save interesting
filter combinations for repeated analysis.
"""

from django.conf import settings
from django.db import models


class Cohort(models.Model):
    """
    Represents a saved cohort (filtered set of visits) for research purposes.

    A cohort captures a specific filter configuration and the number of visits
    that matched those filters at creation time. This allows researchers to:
    - Save interesting subsets of data for later analysis
    - Share filter configurations with colleagues
    - Track which data subsets are being used in research

    Relationships:
        - user: The researcher who created this cohort (ForeignKey to User)

    Filter Storage:
        - filters: JSON field storing VisitSearchFilters structure
        - Supports nested filters: visit, person_demographics, provider_demographics, clinical

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

    # Filter Configuration (JSON)
    filters = models.JSONField(help_text="VisitSearchFilters structure as JSON")

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
        ]

    def __str__(self):
        return f"{self.name} ({self.visit_count} visits) - {self.user.username}"
