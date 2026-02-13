"""
Storage backend tests for clinical app.
Migrated from clinical/tests.py for better organization.
"""

from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase


class AzureStorageTest(TestCase):
    """Test cases for Azure storage backend."""

    @patch("clinical.storage_backend.DataLakeServiceClient")
    def test_storage_initialization(self, mock_client):
        """Test Azure storage client initialization."""
        from clinical.storage_backend import AzureDataLakeStorage

        storage = AzureDataLakeStorage()

        # Should initialize with environment variables
        self.assertIsNotNone(storage.account_name)
        self.assertIsNotNone(storage.file_system_name)

    @patch("clinical.storage_backend.DataLakeServiceClient")
    def test_get_content_type(self, mock_client):
        """Test content type detection."""
        from clinical.storage_backend import AzureDataLakeStorage

        storage = AzureDataLakeStorage()

        # Test different file types
        self.assertEqual(storage._get_content_type("video.mp4"), "video/mp4")
        self.assertEqual(storage._get_content_type("audio.mp3"), "audio/mpeg")
        self.assertEqual(storage._get_content_type("document.pdf"), "application/pdf")
        # Note: .xyz extension may be detected as chemical/x-xyz by mimetypes
        unknown_type = storage._get_content_type("unknown.xyz")
        self.assertIn(unknown_type, ["application/octet-stream", "chemical/x-xyz"])

    @patch("clinical.storage_backend.DataLakeServiceClient")
    def test_path_sanitization(self, mock_client):
        """Test path sanitization methods."""
        from clinical.storage_backend import AzureDataLakeStorage

        storage = AzureDataLakeStorage()

        # Test valid path component
        self.assertEqual(storage._sanitize_path_component("valid_name.mp4"), "valid_name.mp4")

        # Test invalid path components - the sanitizer removes .. and path separators but doesn't raise errors
        # It only raises errors for invalid characters and dot-prefixed files

        # This should pass since the sanitizer removes .. and / characters
        cleaned = storage._sanitize_path_component("../../etc/passwd")
        self.assertEqual(cleaned, "etcpasswd")

        # This should raise error because it starts with dot
        with self.assertRaises(ValidationError):
            storage._sanitize_path_component(".hidden_file")

        # This should raise error because of invalid characters
        with self.assertRaises(ValidationError):
            storage._sanitize_path_component("invalid<>chars")


class EnhancedStorageTest(TestCase):
    """Test cases for enhanced Azure storage exception handling."""

    @patch("clinical.storage_backend.DataLakeServiceClient")
    def test_storage_file_exists_error_handling(self, mock_client):
        """Test file creation when file already exists."""
        from azure.core.exceptions import ResourceExistsError

        from clinical.storage_backend import AzureDataLakeStorage

        storage = AzureDataLakeStorage()

        # Mock directory and file clients
        mock_dir_client = MagicMock()
        mock_file_client = MagicMock()

        # Mock create_file to raise ResourceExistsError first time, succeed second time
        mock_dir_client.create_file.side_effect = [
            ResourceExistsError("File exists"),
            mock_file_client,
        ]
        mock_dir_client.get_file_client.return_value = mock_file_client

        mock_fs_client = MagicMock()
        mock_fs_client.get_directory_client.return_value = mock_dir_client
        storage.file_system_client = mock_fs_client

        # Mock content
        mock_content = MagicMock()
        mock_content.read.side_effect = [b"test data", b""]

        # Test should handle ResourceExistsError and recreate file
        result = storage._save("test.txt", mock_content, 123, "video")

        # Should have called delete_file and create_file again
        mock_file_client.delete_file.assert_called_once()
        self.assertEqual(result, "123/video/test.txt")

    @patch("clinical.storage_backend.DataLakeServiceClient")
    def test_storage_write_error_cleanup(self, mock_client):
        """Test file cleanup when write operation fails."""
        from azure.core.exceptions import AzureError

        from clinical.storage_backend import AzureDataLakeStorage

        storage = AzureDataLakeStorage()

        # Mock directory and file clients
        mock_dir_client = MagicMock()
        mock_file_client = MagicMock()
        mock_file_client.append_data.side_effect = AzureError("Write failed")
        mock_dir_client.create_file.return_value = mock_file_client

        mock_fs_client = MagicMock()
        mock_fs_client.get_directory_client.return_value = mock_dir_client
        storage.file_system_client = mock_fs_client

        # Mock content
        mock_content = MagicMock()
        mock_content.read.return_value = b"test data"

        # Test should cleanup partial file on write error
        with self.assertRaises(AzureError):
            storage._save("test.txt", mock_content, 123, "video")

        # Should have attempted cleanup
        mock_file_client.delete_file.assert_called()
