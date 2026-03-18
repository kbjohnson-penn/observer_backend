"""
Tests for EncounterSearchView.
"""

from unittest.mock import MagicMock, patch

from django.urls import reverse

from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models.profile_models import Profile
from accounts.models.tier_models import Tier
from accounts.models.user_models import User


def _make_es_hit(encounter_id: str = "1") -> dict:
    return {
        "_source": {
            "encounter_id": encounter_id,
            "visit_source_value": "clinic",
            "visit_source_id": 1,
            "visit_date": "2024-03-15",
            "department": "Internal Medicine",
            "patient_gender": "M",
            "patient_race": "W",
            "patient_ethnicity": "NH",
            "patient_year_of_birth": 1970,
            "provider_gender": "F",
            "provider_race": "W",
            "provider_ethnicity": "NH",
            "provider_year_of_birth": 1975,
            "tier_level": 2,
            "has_transcript": True,
            "has_audio": True,
            "has_provider_view": False,
            "has_patient_view": False,
            "has_room_view": False,
            "file_types": ["transcript", "audio"],
            "icd_codes": ["Z00.00"],
            "cpt_codes": [],
            "drug_names": ["metformin"],
            "drug_count": 1,
            "has_notes": True,
            "note_types": ["H&P"],
            "note_count": 1,
        },
        "highlight": {"icd_codes.text": ["<mark>Z00.00</mark>"]},
    }


def _make_es_response(hits=None, total=1) -> dict:
    return {
        "hits": {
            "total": {"value": total},
            "hits": hits or [_make_es_hit()],
        },
        "aggregations": {
            "departments": {"buckets": []},
            "patient_genders": {"buckets": []},
            "patient_races": {"buckets": []},
            "patient_ethnicities": {"buckets": []},
            "provider_genders": {"buckets": []},
            "provider_races": {"buckets": []},
            "provider_ethnicities": {"buckets": []},
            "tier_distribution": {"buckets": []},
            "note_types": {"buckets": []},
            "file_types": {"buckets": []},
        },
    }


class EncounterSearchViewAuthTest(APITestCase):
    def test_unauthenticated_returns_401(self):
        url = reverse("v1:search_api:encounter-search")
        response = self.client.post(url, data={}, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EncounterSearchViewTest(APITestCase):
    databases = ("default", "accounts")

    def setUp(self):
        self.tier = baker.make(Tier, level=5, _using="accounts")
        self.user = baker.make(User, is_superuser=False, _using="accounts")
        # Profile is auto-created by post_save signal; update it with the tier
        self.profile = Profile.objects.using("accounts").get(user=self.user)
        self.profile.tier = self.tier
        self.profile.save(using="accounts")
        self.client.force_authenticate(user=self.user)
        self.url = reverse("v1:search_api:encounter-search")

    @patch("search.api.views.search_views.get_es_client")
    def test_returns_200_with_valid_query(self, mock_get_es):
        mock_es = MagicMock()
        mock_es.search.return_value = _make_es_response()
        mock_get_es.return_value = mock_es

        response = self.client.post(
            self.url, data={"query": "metformin"}, content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("aggregations", response.data)

    @patch("search.api.views.search_views.get_es_client")
    def test_returns_200_with_empty_query(self, mock_get_es):
        mock_es = MagicMock()
        mock_es.search.return_value = _make_es_response(hits=[], total=0)
        mock_get_es.return_value = mock_es

        response = self.client.post(self.url, data={}, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    @patch("search.api.views.search_views.get_es_client")
    def test_returns_503_on_connection_error(self, mock_get_es):
        from elasticsearch import ConnectionError as ESConnectionError

        mock_es = MagicMock()
        mock_es.search.side_effect = ESConnectionError("ES down")
        mock_get_es.return_value = mock_es

        response = self.client.post(
            self.url, data={"query": "test"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("search.api.views.search_views.get_es_client")
    def test_returns_400_for_invalid_sort(self, mock_get_es):
        response = self.client.post(
            self.url,
            data={"sort": {"invalid_field": "asc"}},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("search.api.views.search_views.get_es_client")
    def test_returns_400_for_unknown_filter_key(self, mock_get_es):
        response = self.client.post(
            self.url,
            data={"filters": {"nonexistent_field": "value"}},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("search.api.views.search_views.get_es_client")
    def test_semantic_search_rejected_when_disabled(self, mock_get_es):
        response = self.client.post(
            self.url,
            data={"search_type": "semantic"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
