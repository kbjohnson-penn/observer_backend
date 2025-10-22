import logging
import mimetypes
import os
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import Storage

from azure.core.exceptions import AzureError, ResourceExistsError, ResourceNotFoundError
from azure.storage.filedatalake import ContentSettings, DataLakeServiceClient

logger = logging.getLogger(__name__)


class AzureDataLakeStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.file_system_name = settings.AZURE_STORAGE_FILE_SYSTEM_NAME
        self.sas_token = settings.AZURE_SAS_TOKEN
        self.service_client = DataLakeServiceClient(
            account_url=f"https://{self.account_name}.dfs.core.windows.net",
            credential=self.sas_token,
        )
        self.file_system_client = self.service_client.get_file_system_client(self.file_system_name)
        super().__init__(*args, **kwargs)

    def _sanitize_path_component(self, component):
        """Sanitize a path component to prevent directory traversal."""
        if not component:
            raise ValidationError("Path component cannot be empty")

        # Remove any path traversal attempts
        component = component.replace("..", "").replace("/", "").replace("\\", "")

        # Only allow alphanumeric, dash, underscore, and dot
        if not re.match(r"^[a-zA-Z0-9\-_.]+$", component):
            raise ValidationError(f"Invalid characters in path component: {component}")

        # Prevent hidden files
        if component.startswith("."):
            raise ValidationError("Path component cannot start with dot")

        return component

    def _get_content_type(self, file_name):
        """Determine the content type based on the file extension."""
        content_type, _ = mimetypes.guess_type(file_name)
        return content_type or "application/octet-stream"  # Default to binary if unknown

    def _save(self, file_name, content, encounter_id, field_type):
        """Save a file to Azure Data Lake Storage."""
        # Sanitize path components
        encounter_id = str(encounter_id)
        sanitized_encounter_id = self._sanitize_path_component(encounter_id)
        sanitized_field_type = self._sanitize_path_component(field_type)
        sanitized_file_name = self._sanitize_path_component(file_name)

        directory_path = f"{sanitized_encounter_id}/{sanitized_field_type}"
        directory_client = self.file_system_client.get_directory_client(directory_path)

        try:
            directory_client.create_directory()
        except ResourceExistsError:
            # Directory already exists, which is fine
            logger.debug(f"Directory '{directory_path}' already exists.")
        except AzureError as e:
            logger.error(f"Azure error creating directory '{directory_path}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating directory '{directory_path}': {str(e)}")
            raise

        content_type = self._get_content_type(file_name)

        try:
            file_client = directory_client.create_file(
                sanitized_file_name, content_settings=ContentSettings(content_type=content_type)
            )
        except ResourceExistsError:
            logger.warning(
                f"File '{sanitized_file_name}' already exists in '{directory_path}'. Overwriting."
            )
            file_client = directory_client.get_file_client(sanitized_file_name)
            file_client.delete_file()
            file_client = directory_client.create_file(
                sanitized_file_name, content_settings=ContentSettings(content_type=content_type)
            )
        except AzureError as e:
            logger.error(f"Azure error creating file '{file_name}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating file '{file_name}': {str(e)}")
            raise

        chunk_size = 4 * 1024 * 1024  # 4MB chunk size
        offset = 0

        try:
            while True:
                chunk = content.read(chunk_size)
                if not chunk:
                    break
                file_client.append_data(data=chunk, offset=offset, length=len(chunk))
                offset += len(chunk)

            file_client.flush_data(offset)
        except AzureError as e:
            logger.error(f"Azure error writing file '{file_name}': {str(e)}")
            # Attempt to clean up partial file
            try:
                file_client.delete_file()
            except Exception:
                pass
            raise
        except Exception as e:
            logger.error(f"Unexpected error writing file '{file_name}': {str(e)}")
            # Attempt to clean up partial file
            try:
                file_client.delete_file()
            except Exception:
                pass
            raise

        return f"{directory_path}/{sanitized_file_name}"

    def _delete(self, path):
        """Delete a file from Azure Data Lake."""
        try:
            directory_path, file_name = os.path.split(path)
            directory_client = self.file_system_client.get_directory_client(directory_path)
            file_client = directory_client.get_file_client(file_name)
            file_client.delete_file()
            logger.info(f"File '{path}' deleted successfully.")
        except ResourceNotFoundError:
            logger.warning(f"File '{path}' not found. It may have already been deleted.")
        except AzureError as e:
            logger.error(f"Azure error deleting file '{path}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting file '{path}': {str(e)}")
            raise

    def _file_exists(self, name):
        """Check if a file exists in Azure Data Lake."""
        try:
            directory_path, file_name = os.path.split(name)
            directory_client = self.file_system_client.get_directory_client(directory_path)
            file_client = directory_client.get_file_client(file_name)
            properties = file_client.get_file_properties()
            if "metadata" in properties and properties["metadata"].get("hdi_isfolder") == "true":
                return False
            return "size" in properties
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
        relative_path = self._save(file_name, file, encounter_id=encounter_id, field_type=file_type)
        return relative_path

    def delete_from_storage(self, file_path):
        """Delete a file from Azure Data Lake Storage."""
        try:
            self._delete(file_path)
            logger.info(f"File '{file_path}' deleted successfully.")
        except ResourceNotFoundError:
            logger.warning(f"File '{file_path}' not found. It may have already been deleted.")
        except AzureError as e:
            logger.error(f"Azure error deleting file '{file_path}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting file '{file_path}': {str(e)}")
            raise
