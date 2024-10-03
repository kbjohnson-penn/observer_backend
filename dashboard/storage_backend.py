import os
import logging
import mimetypes
from azure.storage.filedatalake import DataLakeServiceClient, ContentSettings
from django.core.files.storage import Storage
from azure.core.exceptions import ResourceNotFoundError
from django.conf import settings

logger = logging.getLogger(__name__)


class AzureDataLakeStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.file_system_name = settings.AZURE_STORAGE_FILE_SYSTEM_NAME
        self.sas_token = settings.AZURE_SAS_TOKEN
        self.service_client = DataLakeServiceClient(
            account_url=f"https://{self.account_name}.dfs.core.windows.net",
            credential=self.sas_token
        )
        self.file_system_client = self.service_client.get_file_system_client(
            self.file_system_name)
        super().__init__(*args, **kwargs)

    def _get_content_type(self, file_name):
        """Determine the content type based on the file extension."""
        content_type, _ = mimetypes.guess_type(file_name)
        return content_type or 'application/octet-stream'  # Default to binary if unknown

    def _save(self, file_name, content, encounter_id, field_type):
        directory_path = f"{encounter_id}/{field_type}"
        directory_client = self.file_system_client.get_directory_client(
            directory_path)

        try:
            directory_client.create_directory()
        except Exception:
            pass

        content_type = self._get_content_type(file_name)

        file_client = directory_client.create_file(
            file_name, content_settings=ContentSettings(content_type=content_type))

        chunk_size = 4 * 1024 * 1024  # 4MB chunk size
        offset = 0

        while True:
            chunk = content.read(chunk_size)
            if not chunk:
                break
            file_client.append_data(
                data=chunk, offset=offset, length=len(chunk))
            offset += len(chunk)

        file_client.flush_data(offset)

        return f"{directory_path}/{file_name}"

    def _delete(self, path):
        """Delete a file from Azure Data Lake."""
        try:
            directory_path, file_name = os.path.split(path)
            directory_client = self.file_system_client.get_directory_client(
                directory_path)
            file_client = directory_client.get_file_client(file_name)
            file_client.delete_file()
            logger.info(f"File '{path}' deleted successfully.")
        except ResourceNotFoundError:
            logger.warning(
                f"File '{path}' not found. It may have already been deleted.")
        except Exception as e:
            logger.error(f"Failed to delete file '{path}': {str(e)}")
            raise

    def _file_exists(self, name):
        """Check if a file exists in Azure Data Lake."""
        try:
            directory_path, file_name = os.path.split(name)
            directory_client = self.file_system_client.get_directory_client(
                directory_path)
            file_client = directory_client.get_file_client(file_name)
            file_client.get_file_properties()
            return True
        except ResourceNotFoundError:
            return False

    def file_exists(self, name):
        """Check if a file exists in Azure Data Lake."""
        return self._file_exists(name)

    def get_file_path(self, name):
        """Return the path of the file in Azure Data Lake."""
        return f"{self.file_system_name}/{name}"

    def save_to_storage(self, file, encounter_id, file_type):
        """Save a file to Azure Data Lake Storage."""
        file_name = file.name
        relative_path = self._save(
            file_name, file, encounter_id=encounter_id, field_type=file_type)
        return relative_path

    def delete_from_storage(self, file_path):
        """Delete a file from Azure Data Lake Storage."""
        try:
            self._delete(file_path)
            logger.info(f"File '{file_path}' deleted successfully.")
        except ResourceNotFoundError:
            logger.warning(
                f"File '{file_path}' not found. It may have already been deleted.")
        except Exception as e:
            logger.error(f"Failed to delete file '{file_path}': {str(e)}")
            raise
