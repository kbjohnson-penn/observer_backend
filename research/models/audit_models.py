from django.db import models
from .clinical_models import VisitOccurrence


class AuditLogs(models.Model):
    """
    This table tracks access and actions performed within the audit logs of the visit.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id', null=True, blank=True)
    access_time = models.TextField()
    user_id = models.TextField()
    workstation_id = models.TextField()
    access_action = models.TextField()
    metric_id = models.IntegerField(null=True, blank=True)
    metric_name = models.TextField()
    metric_desc = models.TextField()
    metric_type = models.TextField()
    metric_group = models.TextField()
    event_action_type = models.TextField()
    event_action_subtype = models.TextField()

    class Meta:
        app_label = 'research'
        db_table = 'audit_logs'