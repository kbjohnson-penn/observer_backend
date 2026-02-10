"""
Tests for Note API endpoints.
Basic CRUD operations with authentication and authorization.
"""

from rest_framework import status

from research.models import Note, VisitOccurrence

from .test_base import BaseResearchAPITestCase


class NoteAPITest(BaseResearchAPITestCase):
    """Test cases for Note API endpoints."""

    def setUp(self):
        super().setUp()  # Sets up authenticated user, profile, tier, person, and provider
        self.visit = VisitOccurrence.objects.using("research").create(
            tier_level=self.tier.level,  # Reuse self.tier from BaseResearchAPITestCase
            person=self.person,
            provider=self.provider,
            visit_source_id=1,
        )
        self.note = Note.objects.using("research").create(
            person=self.person,
            provider=self.provider,
            visit_occurrence=self.visit,
            note_date="2025-09-16",
            note_text="Sample clinical note",
            note_type="Progress Notes",
            note_status="Signed",
        )

    def test_get_notes_authenticated(self):
        """Test retrieving notes for authenticated user."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/notes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_note_detail_authenticated(self):
        """Test retrieving note detail for authenticated user."""
        self.authenticate_user()

        response = self.client.get(f"/api/v1/research/private/notes/{self.note.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.note.id)

    def test_get_notes_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get("/api/v1/research/private/notes/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_note_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(f"/api/v1/research/private/notes/{self.note.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_note_detail_not_found(self):
        """Test 404 for non-existent note ID."""
        self.authenticate_user()
        response = self.client.get("/api/v1/research/private/notes/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
