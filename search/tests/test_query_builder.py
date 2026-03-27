"""
Tests for the Elasticsearch query builder.
"""

from django.test import TestCase

from search.query_builder import build_encounter_search_query, build_search_response


class TierFilterTest(TestCase):
    def test_tier_filter_present_for_regular_user(self):
        query = build_encounter_search_query(
            query_text="",
            filters={},
            user_tier=2,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        tier_filter = next(
            (f for f in filters if "range" in f and "tier_level" in f["range"]),
            None,
        )
        self.assertIsNotNone(tier_filter, "Tier range filter must be present for regular users")
        self.assertEqual(tier_filter["range"]["tier_level"]["lte"], 2)

    def test_zero_result_injection_when_no_tier(self):
        query = build_encounter_search_query(
            query_text="",
            filters={},
            user_tier=None,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        zero_filter = next(
            (
                f
                for f in filters
                if "range" in f and f["range"].get("tier_level", {}).get("lt") == 0
            ),
            None,
        )
        self.assertIsNotNone(
            zero_filter, "Zero-result injection must be present when user has no tier"
        )

    def test_no_tier_filter_for_superuser(self):
        query = build_encounter_search_query(
            query_text="",
            filters={},
            user_tier=None,
            is_superuser=True,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        tier_filters = [
            f
            for f in filters
            if "range" in f
            and "tier_level" in f.get("range", {})
            or f.get("term", {}).get("tier_level") == 0
        ]
        self.assertEqual(len(tier_filters), 0, "No tier filter for superusers")


class MustClauseTest(TestCase):
    def test_match_all_for_empty_query(self):
        query = build_encounter_search_query(
            query_text="",
            filters={},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        must = query["query"]["bool"]["must"]
        self.assertEqual(len(must), 1)
        self.assertIn("match_all", must[0])

    def test_multi_match_for_non_empty_query(self):
        query = build_encounter_search_query(
            query_text="metformin",
            filters={},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        should = query["query"]["bool"]["should"]
        multi_match = next((c for c in should if "multi_match" in c), None)
        self.assertIsNotNone(multi_match)
        self.assertIn("metformin", multi_match["multi_match"]["query"])
        fields = multi_match["multi_match"]["fields"]
        self.assertIn("condition_descriptions.text^2", fields)
        self.assertIn("procedure_descriptions.text^2", fields)

    def test_lucene_special_chars_escaped(self):
        query = build_encounter_search_query(
            query_text="test+query",
            filters={},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        should = query["query"]["bool"]["should"]
        multi_match = next((c for c in should if "multi_match" in c), None)
        self.assertIsNotNone(multi_match)
        self.assertNotIn("+", multi_match["multi_match"]["query"].replace("\\+", ""))


class StructuredFiltersTest(TestCase):
    def test_icd_codes_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"icd_codes": ["Z00.00", "I10"]},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        icd_filter = next(
            (f for f in filters if "terms" in f and "icd_codes" in f["terms"]),
            None,
        )
        self.assertIsNotNone(icd_filter)
        self.assertIn("Z00.00", icd_filter["terms"]["icd_codes"])

    def test_cpt_codes_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"cpt_codes": ["99213"]},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        cpt_filter = next(
            (f for f in filters if "terms" in f and "cpt_codes" in f["terms"]),
            None,
        )
        self.assertIsNotNone(cpt_filter)
        self.assertIn("99213", cpt_filter["terms"]["cpt_codes"])

    def test_date_from_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"date_from": "2024-01-01"},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        date_filter = next(
            (f for f in filters if "range" in f and "visit_date" in f["range"]),
            None,
        )
        self.assertIsNotNone(date_filter)
        self.assertEqual(date_filter["range"]["visit_date"]["gte"], "2024-01-01")

    def test_date_to_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"date_to": "2024-12-31"},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        date_filter = next(
            (f for f in filters if "range" in f and "visit_date" in f["range"]),
            None,
        )
        self.assertIsNotNone(date_filter)
        self.assertEqual(date_filter["range"]["visit_date"]["lte"], "2024-12-31")

    def test_date_range_combined(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"date_from": "2024-01-01", "date_to": "2024-12-31"},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        date_filters = [f for f in filters if "range" in f and "visit_date" in f["range"]]
        self.assertEqual(
            len(date_filters), 1, "date_from + date_to should produce a single range clause"
        )
        self.assertIn("gte", date_filters[0]["range"]["visit_date"])
        self.assertIn("lte", date_filters[0]["range"]["visit_date"])

    def test_patient_gender_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"patient_gender": ["M"]},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        gender_filter = next(
            (f for f in filters if "terms" in f and "patient_gender" in f["terms"]),
            None,
        )
        self.assertIsNotNone(gender_filter)
        self.assertIn("M", gender_filter["terms"]["patient_gender"])

    def test_patient_race_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"patient_race": ["B", "W"]},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        race_filter = next(
            (f for f in filters if "terms" in f and "patient_race" in f["terms"]),
            None,
        )
        self.assertIsNotNone(race_filter)
        self.assertIn("B", race_filter["terms"]["patient_race"])
        self.assertIn("W", race_filter["terms"]["patient_race"])

    def test_patient_ethnicity_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"patient_ethnicity": ["NH"]},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        eth_filter = next(
            (f for f in filters if "terms" in f and "patient_ethnicity" in f["terms"]),
            None,
        )
        self.assertIsNotNone(eth_filter)
        self.assertIn("NH", eth_filter["terms"]["patient_ethnicity"])

    def test_provider_gender_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"provider_gender": ["F"]},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        gender_filter = next(
            (f for f in filters if "terms" in f and "provider_gender" in f["terms"]),
            None,
        )
        self.assertIsNotNone(gender_filter)
        self.assertIn("F", gender_filter["terms"]["provider_gender"])

    def test_multimodal_flag_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"has_transcript": True},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        flag_filter = next(
            (f for f in filters if f.get("term", {}).get("has_transcript") is True),
            None,
        )
        self.assertIsNotNone(flag_filter)

    def test_tier_filter_always_present_with_other_filters(self):
        query = build_encounter_search_query(
            query_text="",
            filters={
                "drug_names": ["metformin"],
                "date_from": "2024-01-01",
                "patient_gender": ["M"],
                "patient_race": ["B"],
            },
            user_tier=3,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        tier_filter = next(
            (f for f in filters if "range" in f and "tier_level" in f["range"]),
            None,
        )
        self.assertIsNotNone(tier_filter, "Tier filter must be present even with other filters")
        self.assertEqual(tier_filter["range"]["tier_level"]["lte"], 3)

    def test_drug_names_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"drug_names": ["metformin"]},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        drug_filter = next(
            (f for f in filters if "match" in f and "drug_names.text" in f["match"]),
            None,
        )
        self.assertIsNotNone(drug_filter)
        self.assertEqual(drug_filter["match"]["drug_names.text"]["query"], "metformin")

    def test_drug_names_filter_multiple_uses_or_semantics(self):
        """Multiple drug names produce a bool.should (OR) wrapper."""
        query = build_encounter_search_query(
            query_text="",
            filters={"drug_names": ["metformin", "lisinopril"]},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        bool_filter = next(
            (f for f in filters if "bool" in f and "should" in f.get("bool", {})),
            None,
        )
        self.assertIsNotNone(bool_filter, "Multi-drug filter must use bool.should wrapper")
        self.assertEqual(bool_filter["bool"]["minimum_should_match"], 1)
        self.assertEqual(len(bool_filter["bool"]["should"]), 2)
        drug_queries = [
            clause["match"]["drug_names.text"]["query"] for clause in bool_filter["bool"]["should"]
        ]
        self.assertIn("metformin", drug_queries)
        self.assertIn("lisinopril", drug_queries)

    def test_department_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"department": ["Internal Medicine"]},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        dept_filter = next(
            (f for f in filters if "terms" in f and "department" in f["terms"]),
            None,
        )
        self.assertIsNotNone(dept_filter)
        self.assertIn("Internal Medicine", dept_filter["terms"]["department"])

    def test_has_notes_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"has_notes": True},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        notes_filter = next(
            (f for f in filters if f.get("term", {}).get("has_notes") is True),
            None,
        )
        self.assertIsNotNone(notes_filter)

    def test_note_types_filter(self):
        query = build_encounter_search_query(
            query_text="",
            filters={"note_types": ["H&P"]},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        filters = query["query"]["bool"]["filter"]
        nt_filter = next(
            (f for f in filters if "terms" in f and "note_types" in f["terms"]),
            None,
        )
        self.assertIsNotNone(nt_filter)

    def test_departments_aggregation_present(self):
        query = build_encounter_search_query(
            query_text="",
            filters={},
            user_tier=5,
            is_superuser=False,
            page=1,
            page_size=20,
        )
        self.assertIn("departments", query["aggs"])
        self.assertEqual(query["aggs"]["departments"]["terms"]["field"], "department")


class PaginationTest(TestCase):
    def test_pagination_offset(self):
        query = build_encounter_search_query(
            query_text="",
            filters={},
            user_tier=5,
            is_superuser=False,
            page=3,
            page_size=10,
        )
        self.assertEqual(query["from"], 20)
        self.assertEqual(query["size"], 10)


class BuildSearchResponseTest(TestCase):
    def _make_es_response(self, total, hits):
        return {
            "hits": {
                "total": {"value": total},
                "hits": hits,
            },
            "aggregations": {
                "departments": {"buckets": [{"key": "Internal Medicine", "doc_count": 10}]},
                "patient_genders": {"buckets": [{"key": "M", "doc_count": 5}]},
            },
        }

    def test_count_and_results(self):
        es_resp = self._make_es_response(
            total=1,
            hits=[{"_source": {"encounter_id": "1"}, "highlight": {}}],
        )
        result = build_search_response(es_resp, page=1, page_size=20)
        self.assertEqual(result["count"], 1)
        self.assertEqual(len(result["results"]), 1)

    def test_next_page_when_more_results(self):
        es_resp = self._make_es_response(total=25, hits=[{"_source": {}, "highlight": {}}])
        result = build_search_response(es_resp, page=1, page_size=20)
        self.assertIsNotNone(result["next"])
        self.assertIsNone(result["previous"])

    def test_no_next_page_on_last_page(self):
        es_resp = self._make_es_response(total=20, hits=[{"_source": {}, "highlight": {}}])
        result = build_search_response(es_resp, page=1, page_size=20)
        self.assertIsNone(result["next"])

    def test_aggregations_formatted(self):
        es_resp = self._make_es_response(total=5, hits=[])
        result = build_search_response(es_resp, page=1, page_size=20)
        self.assertIn("patient_genders", result["aggregations"])
        bucket = result["aggregations"]["patient_genders"][0]
        self.assertEqual(bucket["key"], "M")
        self.assertEqual(bucket["count"], 5)

    def test_departments_aggregation_passed_through(self):
        es_resp = self._make_es_response(total=5, hits=[])
        result = build_search_response(es_resp, page=1, page_size=20)
        self.assertIn("departments", result["aggregations"])
        dept_bucket = result["aggregations"]["departments"][0]
        self.assertEqual(dept_bucket["key"], "Internal Medicine")
        self.assertEqual(dept_bucket["count"], 10)
