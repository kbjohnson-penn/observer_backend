from django.db import models
from .clinical_models import VisitOccurrence


class AuditLogs(models.Model):
    """
    This table tracks access and actions performed within the audit logs of the visit.
    """
    id = models.AutoField(primary_key=True, verbose_name="Audit Log ID")
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id', null=True, blank=True)
    access_time = models.DateTimeField()
    user_id = models.CharField(max_length=255)
    workstation_id = models.CharField(max_length=255)
    access_action = models.CharField(max_length=255)
    metric_id = models.IntegerField(null=True, blank=True)
    metric_name = models.CharField(max_length=255)
    metric_desc = models.CharField(max_length=255)
    metric_type = models.CharField(max_length=255)
    metric_group = models.CharField(max_length=255)
    event_action_type = models.CharField(max_length=255)
    event_action_subtype = models.CharField(max_length=255)

    def __str__(self):
        return f"Audit Log {self.id}"
    class Meta:
        app_label = 'research'
        db_table = 'audit_logs'
        verbose_name_plural = 'Audit Logs'