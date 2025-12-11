"""
Audit Trail Models for HIPAA Compliance.

This module provides a general-purpose audit trail for logging user actions
including data access, exports, searches, and configuration changes.
"""

from django.conf import settings
from django.db import models


class AuditTrail(models.Model):
    """
    General-purpose audit trail for HIPAA compliance.

    Logs all user actions including data access, exports, searches,
    and configuration changes. Designed to be flexible with a JSONField
    for event-specific metadata.
    """

    CATEGORY_CHOICES = [
        ("DATA_EXPORT", "Data Export"),
        ("DATA_VIEW", "Data View"),
        ("DATA_SEARCH", "Data Search"),
        ("AUTHENTICATION", "Authentication"),
        ("CONFIGURATION", "Configuration"),
        ("COHORT_MANAGEMENT", "Cohort Management"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="audit_trail",
        help_text="The user who performed the action",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action was performed",
    )
    event_type = models.CharField(
        max_length=100,
        help_text="Specific event type (e.g., EXPORT_SINGLE_TABLE, VIEW_PATIENT_RECORD)",
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text="High-level category of the event",
    )
    description = models.TextField(
        blank=True,
        help_text="Human-readable description of the action",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Event-specific data (table names, record counts, etc.)",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Client IP address",
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Client user agent string",
    )

    class Meta:
        app_label = "accounts"
        db_table = "audit_trail"
        ordering = ["-timestamp"]
        verbose_name = "Audit Trail Entry"
        verbose_name_plural = "Audit Trail Entries"
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["category", "-timestamp"]),
            models.Index(fields=["event_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.event_type} at {self.timestamp}"
