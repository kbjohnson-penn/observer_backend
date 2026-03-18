"""
Tests for the sync_elasticsearch management command.
All data sourced from research DB only (no PHI from clinical DB).
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from search.management.commands.sync_elasticsearch import Command


class SyncEncountersCommandTest(TestCase):
    def _make_command(self):
        cmd = Command()
        cmd.stdout = MagicMock()
        cmd.stderr = MagicMock()
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda x: x
        cmd.style.WARNING = lambda x: x
        return cmd

    @patch("search.management.commands.sync_elasticsearch.get_es_client")
    @patch("search.management.commands.sync_elasticsearch.create_index_if_not_exists")
    def test_full_reindex_deletes_then_recreates(self, mock_create, mock_get_es):
        mock_es = MagicMock()
        mock_es.indices.exists.return_value = True
        mock_get_es.return_value = mock_es

        cmd = self._make_command()
        cmd._sync_encounters = MagicMock()
        cmd._sync_texts = MagicMock()

        cmd.handle(index="all", batch_size=500, full_reindex=True, confirm=True)

        delete_calls = mock_es.indices.delete.call_args_list
        self.assertEqual(len(delete_calls), 2)
        mock_create.assert_called()
        cmd._sync_encounters.assert_called_once()
        cmd._sync_texts.assert_called_once()

    @patch("search.management.commands.sync_elasticsearch.get_es_client")
    @patch("search.management.commands.sync_elasticsearch.create_index_if_not_exists")
    def test_encounters_only_skips_texts(self, mock_create, mock_get_es):
        mock_es = MagicMock()
        mock_get_es.return_value = mock_es

        cmd = self._make_command()
        cmd._sync_encounters = MagicMock()
        cmd._sync_texts = MagicMock()

        cmd.handle(index="encounters", batch_size=500, full_reindex=False, confirm=False)

        cmd._sync_encounters.assert_called_once()
        cmd._sync_texts.assert_not_called()

    @patch("search.management.commands.sync_elasticsearch.get_es_client")
    def test_full_reindex_without_confirm_aborts(self, mock_get_es):
        mock_es = MagicMock()
        mock_get_es.return_value = mock_es

        cmd = self._make_command()
        cmd._sync_encounters = MagicMock()
        cmd._sync_texts = MagicMock()

        cmd.handle(index="all", batch_size=500, full_reindex=True, confirm=False)

        mock_es.indices.delete.assert_not_called()
        cmd._sync_encounters.assert_not_called()
        cmd._sync_texts.assert_not_called()

    @patch("search.management.commands.sync_elasticsearch.bulk")
    @patch("search.management.commands.sync_elasticsearch.Note")
    @patch("search.management.commands.sync_elasticsearch.ProcedureOccurrence")
    @patch("search.management.commands.sync_elasticsearch.DrugExposure")
    @patch("search.management.commands.sync_elasticsearch.ConditionOccurrence")
    @patch("search.management.commands.sync_elasticsearch.Observation")
    @patch("search.management.commands.sync_elasticsearch.VisitOccurrence")
    def test_encounter_doc_shape_no_phi(
        self, mock_vo, mock_obs, mock_cond, mock_drug, mock_proc, mock_note, mock_bulk
    ):
        """Encounter ES docs must not contain PHI fields and must have demographics."""
        mock_bulk.return_value = (1, [])

        # _sync_encounters now calls .count() first, then batches via order_by().select_related()[offset:limit]
        mock_vo.objects.using.return_value.count.return_value = 1

        # Observation (file_types)
        mock_obs.objects.using.return_value.filter.return_value.values.return_value = [
            {"visit_occurrence_id": 1, "file_type": "transcript"},
            {"visit_occurrence_id": 1, "file_type": "audio"},
        ]
        # Conditions with descriptions
        mock_cond.objects.using.return_value.filter.return_value.values.return_value = [
            {
                "visit_occurrence_id": 1,
                "concept_code": "E11.9",
                "condition_source_value": "Type 2 diabetes",
            },
        ]
        # Procedures with descriptions
        mock_proc.objects.using.return_value.filter.return_value.values.return_value = [
            {"visit_occurrence_id": 1, "name": "Lab", "description": "Hemoglobin A1c"},
        ]
        # No drugs or notes
        for mock_m in (mock_drug, mock_note):
            mock_m.objects.using.return_value.filter.return_value.values.return_value = []

        # Build a mock visit
        mock_person = MagicMock()
        mock_person.gender_source_value = "Female"
        mock_person.race_source_value = "Asian"
        mock_person.ethnicity_source_value = "Not Hispanic"
        mock_person.year_of_birth = 1980

        mock_provider = MagicMock()
        mock_provider.gender_source_value = "Male"
        mock_provider.race_source_value = "White"
        mock_provider.ethnicity_source_value = "Not Hispanic"
        mock_provider.year_of_birth = 1975

        mock_visit = MagicMock()
        mock_visit.id = 1
        mock_visit.visit_source_value = "ANON-001"
        mock_visit.visit_source_id = 42
        mock_visit.visit_start_date = None
        mock_visit.tier_level = 2
        mock_visit.department = "Internal Medicine"
        mock_visit.person = mock_person
        mock_visit.provider = mock_provider

        # First slice returns one visit; second slice returns [] to stop the batch loop
        mock_vo.objects.using.return_value.select_related.return_value.order_by.return_value.__getitem__.side_effect = [
            [mock_visit],
            [],
        ]

        cmd = self._make_command()
        mock_es = MagicMock()
        cmd._sync_encounters(mock_es, batch_size=500)

        mock_bulk.assert_called_once()
        actions = mock_bulk.call_args[0][1]
        self.assertEqual(len(actions), 1)

        doc = actions[0]["_source"]
        # Must NOT contain PHI fields
        for phi_field in (
            "csn_number",
            "case_id",
            "patient_name",
            "provider_name",
            "patient_id",
            "provider_id",
            "encounter_source",
            "visit_type",
            "created_at",
            "is_deidentified",
            "is_restricted",
        ):
            self.assertNotIn(phi_field, doc, f"PHI field '{phi_field}' must not be in ES doc")

        # Must contain demographic fields
        self.assertEqual(doc["patient_gender"], "Female")
        self.assertEqual(doc["patient_race"], "Asian")
        self.assertEqual(doc["patient_year_of_birth"], 1980)
        self.assertEqual(doc["provider_gender"], "Male")
        self.assertEqual(doc["department"], "Internal Medicine")

        # Multimodal flags from Observation
        self.assertTrue(doc["has_transcript"])
        self.assertTrue(doc["has_audio"])
        self.assertFalse(doc["has_provider_view"])

        self.assertEqual(doc["tier_level"], 2)

        # New description fields
        self.assertIn("Type 2 diabetes", doc["condition_descriptions"])
        self.assertIn("Hemoglobin A1c", doc["procedure_descriptions"])

    @patch("search.management.commands.sync_elasticsearch.bulk")
    @patch("search.management.commands.sync_elasticsearch.Note")
    @patch("search.management.commands.sync_elasticsearch.VisitOccurrence")
    def test_note_doc_shape_in_texts_sync(self, mock_vo, mock_note, mock_bulk):
        """Notes synced to observer-texts must have required fields and no PHI."""
        mock_bulk.return_value = (1, [])

        mock_visit = MagicMock()
        mock_visit.visit_occurrence_id = 7
        mock_visit.tier_level = 2

        mock_note_obj = MagicMock()
        mock_note_obj.id = 42
        mock_note_obj.note_text = "Patient presents with chest pain."
        mock_note_obj.note_type = "H&P"
        mock_note_obj.visit_occurrence = mock_visit
        mock_note_obj.visit_occurrence_id = 7

        mock_note.objects.using.return_value.select_related.return_value.iterator.return_value = [
            mock_note_obj
        ]

        cmd = self._make_command()
        mock_es = MagicMock()
        cmd._sync_texts(mock_es, batch_size=500)

        mock_bulk.assert_called_once()
        actions = mock_bulk.call_args[0][1]
        self.assertEqual(len(actions), 1)

        doc = actions[0]["_source"]
        self.assertEqual(doc["source_type"], "clinical_note")
        self.assertEqual(doc["encounter_id"], str(7))
        self.assertEqual(doc["text"], "Patient presents with chest pain.")
        self.assertEqual(doc["note_type"], "H&P")
        self.assertIsNone(doc["speaker_label"])
        self.assertEqual(doc["entities"], [])
        self.assertIsNone(doc["embedding"])
        self.assertEqual(doc["tier_level"], 2)
        self.assertEqual(actions[0]["_id"], "note_42")
