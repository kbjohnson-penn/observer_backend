"""
Tests for the Elasticsearch client singleton.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from search.es_client import get_es_client, ping_es


class GetEsClientTest(TestCase):
    def test_returns_elasticsearch_instance(self):
        # _client is instantiated at module load time (not lazily)
        from elasticsearch import Elasticsearch

        client = get_es_client()
        self.assertIsInstance(client, Elasticsearch)

    def test_returns_same_instance_on_subsequent_calls(self):
        client1 = get_es_client()
        client2 = get_es_client()
        self.assertIs(client1, client2)


class PingEsTest(TestCase):
    @patch("search.es_client.get_es_client")
    def test_returns_true_when_reachable(self, mock_get):
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_get.return_value = mock_client

        self.assertTrue(ping_es())

    @patch("search.es_client.get_es_client")
    def test_returns_false_on_exception(self, mock_get):
        mock_get.side_effect = Exception("connection refused")

        self.assertFalse(ping_es())
