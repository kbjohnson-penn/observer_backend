"""
Tests for SearchRequestSerializer validation.
"""

from django.test import TestCase, override_settings

from search.api.serializers.search_serializers import ALLOWED_FILTER_KEYS, SearchRequestSerializer


class QueryValidationTest(TestCase):
    def test_blank_query_allowed(self):
        s = SearchRequestSerializer(data={"query": ""})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["query"], "")

    def test_query_whitespace_stripped(self):
        s = SearchRequestSerializer(data={"query": "  hello  "})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["query"], "hello")

    def test_query_max_length_exceeded(self):
        s = SearchRequestSerializer(data={"query": "x" * 501})
        self.assertFalse(s.is_valid())
        self.assertIn("query", s.errors)

    def test_query_exactly_500_chars_allowed(self):
        s = SearchRequestSerializer(data={"query": "x" * 500})
        self.assertTrue(s.is_valid(), s.errors)


class FilterValidationTest(TestCase):
    def test_empty_filters_allowed(self):
        s = SearchRequestSerializer(data={"filters": {}})
        self.assertTrue(s.is_valid(), s.errors)

    def test_unknown_filter_key_rejected(self):
        s = SearchRequestSerializer(data={"filters": {"patient_name": "John"}})
        self.assertFalse(s.is_valid())
        self.assertIn("filters", s.errors)

    def test_all_allowed_keys_pass(self):
        filters = {k: [] for k in ALLOWED_FILTER_KEYS}
        # Date fields require YYYY-MM-DD format, not an empty list
        filters["date_from"] = "2024-01-01"
        filters["date_to"] = "2024-12-31"
        # Boolean fields must be actual booleans, not empty lists
        for bool_field in (
            "has_transcript",
            "has_audio",
            "has_provider_view",
            "has_patient_view",
            "has_room_view",
            "has_notes",
        ):
            filters[bool_field] = False
        s = SearchRequestSerializer(data={"filters": filters})
        self.assertTrue(s.is_valid(), s.errors)

    def test_known_and_unknown_key_rejected(self):
        s = SearchRequestSerializer(data={"filters": {"drug_names": ["metformin"], "bad_key": "x"}})
        self.assertFalse(s.is_valid())
        self.assertIn("filters", s.errors)

    def test_list_filter_as_dict_rejected(self):
        s = SearchRequestSerializer(data={"filters": {"drug_names": {"bad": "value"}}})
        self.assertFalse(s.is_valid())
        self.assertIn("filters", s.errors)

    def test_list_filter_as_string_rejected(self):
        s = SearchRequestSerializer(data={"filters": {"icd_codes": "Z00.00"}})
        self.assertFalse(s.is_valid())
        self.assertIn("filters", s.errors)

    def test_list_filter_with_non_string_items_rejected(self):
        s = SearchRequestSerializer(data={"filters": {"drug_names": [1, 2]}})
        self.assertFalse(s.is_valid())
        self.assertIn("filters", s.errors)

    def test_boolean_filter_as_string_rejected(self):
        s = SearchRequestSerializer(data={"filters": {"has_transcript": "true"}})
        self.assertFalse(s.is_valid())
        self.assertIn("filters", s.errors)

    def test_boolean_filter_as_integer_rejected(self):
        s = SearchRequestSerializer(data={"filters": {"has_notes": 1}})
        self.assertFalse(s.is_valid())
        self.assertIn("filters", s.errors)

    def test_valid_boolean_filter_passes(self):
        s = SearchRequestSerializer(data={"filters": {"has_transcript": True}})
        self.assertTrue(s.is_valid(), s.errors)

    def test_valid_list_filter_passes(self):
        s = SearchRequestSerializer(data={"filters": {"drug_names": ["metformin"]}})
        self.assertTrue(s.is_valid(), s.errors)


class PaginationValidationTest(TestCase):
    def test_page_zero_rejected(self):
        s = SearchRequestSerializer(data={"page": 0})
        self.assertFalse(s.is_valid())
        self.assertIn("page", s.errors)

    def test_page_101_rejected(self):
        s = SearchRequestSerializer(data={"page": 101})
        self.assertFalse(s.is_valid())
        self.assertIn("page", s.errors)

    def test_page_size_zero_rejected(self):
        s = SearchRequestSerializer(data={"page_size": 0})
        self.assertFalse(s.is_valid())
        self.assertIn("page_size", s.errors)

    def test_page_size_101_rejected(self):
        s = SearchRequestSerializer(data={"page_size": 101})
        self.assertFalse(s.is_valid())
        self.assertIn("page_size", s.errors)

    def test_valid_pagination(self):
        s = SearchRequestSerializer(data={"page": 1, "page_size": 20})
        self.assertTrue(s.is_valid(), s.errors)

    def test_page_100_allowed(self):
        s = SearchRequestSerializer(data={"page": 100})
        self.assertTrue(s.is_valid(), s.errors)


class SortValidationTest(TestCase):
    def test_none_sort_allowed(self):
        s = SearchRequestSerializer(data={"sort": None})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertIsNone(s.validated_data["sort"])

    def test_valid_sort_visit_date_asc(self):
        s = SearchRequestSerializer(data={"sort": {"visit_date": "asc"}})
        self.assertTrue(s.is_valid(), s.errors)

    def test_valid_sort_score_desc(self):
        s = SearchRequestSerializer(data={"sort": {"_score": "desc"}})
        self.assertTrue(s.is_valid(), s.errors)

    def test_unknown_sort_field_rejected(self):
        s = SearchRequestSerializer(data={"sort": {"patient_name": "asc"}})
        self.assertFalse(s.is_valid())
        self.assertIn("sort", s.errors)

    def test_bad_sort_direction_rejected(self):
        s = SearchRequestSerializer(data={"sort": {"visit_date": "random"}})
        self.assertFalse(s.is_valid())
        self.assertIn("sort", s.errors)


class SearchTypeValidationTest(TestCase):
    def test_keyword_always_passes(self):
        s = SearchRequestSerializer(data={"search_type": "keyword"})
        self.assertTrue(s.is_valid(), s.errors)

    @override_settings(SEARCH_FEATURES={"semantic_enabled": False})
    def test_semantic_rejected_when_disabled(self):
        s = SearchRequestSerializer(data={"search_type": "semantic"})
        self.assertFalse(s.is_valid())
        self.assertIn("search_type", s.errors)

    @override_settings(SEARCH_FEATURES={"semantic_enabled": True})
    def test_semantic_passes_when_enabled(self):
        s = SearchRequestSerializer(data={"search_type": "semantic"})
        self.assertTrue(s.is_valid(), s.errors)

    def test_invalid_search_type_rejected(self):
        s = SearchRequestSerializer(data={"search_type": "fuzzy"})
        self.assertFalse(s.is_valid())
        self.assertIn("search_type", s.errors)
