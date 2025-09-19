"""
Tests for AuditLogs API endpoints.
Basic CRUD operations with authentication and authorization.
"""
from rest_framework import status
from .test_base import BaseResearchAPITestCase
from research.models import AuditLogs, VisitOccurrence
from django.utils import timezone
import pytz


class AuditLogsAPITest(BaseResearchAPITestCase):
    """Test cases for AuditLogs API endpoints."""

    def setUp(self):
        super().setUp()  # Sets up authenticated user, profile, tier, person, and provider
        self.visit = VisitOccurrence.objects.using('research').create(
            tier_id=self.tier.id,
            person=self.person,
            provider=self.provider,
            visit_source_id=1
        )
        self.audit_log = AuditLogs.objects.using('research').create(
            visit_occurrence=self.visit,
            access_time=timezone.datetime(2023, 1, 1, 9, 0, tzinfo=pytz.UTC),
            user_id="test_user_123",
            workstation_id="test_workstation_456",
            access_action="QUERY",
            metric_id=1,
            metric_name="Test Metric",
            metric_desc="Test metric description",
            metric_type="E-APPLICATION EVENT",
            metric_group="Test Group",
            event_action_type="VIEW",
            event_action_subtype="DETAIL"
        )

    def test_get_audit_logs_authenticated(self):
        """Test retrieving audit logs for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get('/api/v1/research/private/audit-logs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_audit_log_detail_authenticated(self):
        """Test retrieving audit log detail for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/research/private/audit-logs/{self.audit_log.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.audit_log.id)

    def test_get_audit_logs_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get('/api/v1/research/private/audit-logs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_audit_log_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(f'/api/v1/research/private/audit-logs/{self.audit_log.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_audit_log_detail_not_found(self):
        """Test 404 for non-existent audit log ID."""
        self.authenticate_user()
        response = self.client.get('/api/v1/research/private/audit-logs/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)