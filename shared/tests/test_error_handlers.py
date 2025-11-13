"""
Error handler tests for shared app.
Tests for API error handling utilities and custom exceptions.
"""

from unittest.mock import MagicMock, patch

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from shared.api.error_handlers import (
    ErrorHandlerMixin,
    ObserverAPIException,
    ObserverNotFound,
    ObserverPermissionDenied,
    ObserverValidationError,
    handle_not_found,
    handle_permission_denied,
    handle_server_error,
    handle_validation_error,
    safe_get_object_or_404,
)


class CustomExceptionsTest(TestCase):
    """Test cases for custom API exceptions."""

    def test_observer_api_exception_base(self):
        """Test base ObserverAPIException."""
        exc = ObserverAPIException()
        self.assertEqual(exc.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(exc.default_detail, "An error occurred.")
        self.assertEqual(exc.default_code, "error")

    def test_observer_not_found_exception(self):
        """Test ObserverNotFound exception."""
        exc = ObserverNotFound()
        self.assertEqual(exc.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(exc.default_detail, "Resource not found.")
        self.assertEqual(exc.default_code, "not_found")

        # Test with custom detail
        exc_custom = ObserverNotFound(detail="Custom not found message")
        self.assertEqual(str(exc_custom.detail), "Custom not found message")

    def test_observer_permission_denied_exception(self):
        """Test ObserverPermissionDenied exception."""
        exc = ObserverPermissionDenied()
        self.assertEqual(exc.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(exc.default_detail, "Permission denied.")
        self.assertEqual(exc.default_code, "permission_denied")

        # Test with custom detail
        exc_custom = ObserverPermissionDenied(detail="Custom permission message")
        self.assertEqual(str(exc_custom.detail), "Custom permission message")

    def test_observer_validation_error_exception(self):
        """Test ObserverValidationError exception."""
        exc = ObserverValidationError()
        self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(exc.default_detail, "Invalid input provided.")
        self.assertEqual(exc.default_code, "validation_error")

        # Test with custom detail
        exc_custom = ObserverValidationError(detail="Custom validation message")
        self.assertEqual(str(exc_custom.detail), "Custom validation message")


class ErrorHandlersTest(TestCase):
    """Test cases for error handler functions."""

    def test_handle_not_found_basic(self):
        """Test basic not found handler."""
        response = handle_not_found()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Resource not found")
        self.assertEqual(response.data["code"], "not_found")

    def test_handle_not_found_custom_detail(self):
        """Test not found handler with custom detail."""
        custom_detail = "User not found"
        response = handle_not_found(detail=custom_detail)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], custom_detail)
        self.assertEqual(response.data["code"], "not_found")

    @patch("shared.api.error_handlers.logger")
    def test_handle_not_found_with_logging(self, mock_logger):
        """Test not found handler with logging."""
        log_message = "User ID 123 not found"
        response = handle_not_found(log_message=log_message)

        mock_logger.warning.assert_called_once_with("404 Error: %s", log_message)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_handle_permission_denied_basic(self):
        """Test basic permission denied handler."""
        response = handle_permission_denied()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "Permission denied")
        self.assertEqual(response.data["code"], "permission_denied")

    def test_handle_permission_denied_custom_detail(self):
        """Test permission denied handler with custom detail."""
        custom_detail = "Insufficient tier level"
        response = handle_permission_denied(detail=custom_detail)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], custom_detail)
        self.assertEqual(response.data["code"], "permission_denied")

    @patch("shared.api.error_handlers.logger")
    def test_handle_permission_denied_with_logging(self, mock_logger):
        """Test permission denied handler with logging."""
        log_message = "User lacks tier 3 access"
        response = handle_permission_denied(log_message=log_message)

        mock_logger.warning.assert_called_once_with("Permission denied: %s", log_message)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_handle_validation_error_basic(self):
        """Test basic validation error handler."""
        response = handle_validation_error()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid input provided")
        self.assertEqual(response.data["code"], "validation_error")
        self.assertNotIn("errors", response.data)

    def test_handle_validation_error_with_errors(self):
        """Test validation error handler with field errors."""
        field_errors = {
            "email": ["This field is required."],
            "age": ["Must be a positive integer."],
        }
        response = handle_validation_error(errors=field_errors)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["errors"], field_errors)

    @patch("shared.api.error_handlers.logger")
    def test_handle_validation_error_with_logging(self, mock_logger):
        """Test validation error handler with logging."""
        log_message = "Invalid phone number format"
        response = handle_validation_error(log_message=log_message)

        mock_logger.info.assert_called_once_with("Validation error: %s", log_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_handle_server_error_basic(self):
        """Test basic server error handler."""
        response = handle_server_error()

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["detail"], "An internal error occurred")
        self.assertEqual(response.data["code"], "server_error")

    def test_handle_server_error_custom_detail(self):
        """Test server error handler with custom detail."""
        custom_detail = "Database connection failed"
        response = handle_server_error(detail=custom_detail)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["detail"], custom_detail)
        self.assertEqual(response.data["code"], "server_error")

    @patch("shared.api.error_handlers.logger")
    def test_handle_server_error_with_exception(self, mock_logger):
        """Test server error handler with exception logging."""
        test_exception = ValueError("Test error")
        log_message = "Database query failed"

        response = handle_server_error(log_message=log_message, exception=test_exception)

        mock_logger.error.assert_called_once_with(
            "Server error: %s", log_message, exc_info=test_exception
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch("shared.api.error_handlers.logger")
    def test_handle_server_error_log_only(self, mock_logger):
        """Test server error handler with log message only."""
        log_message = "Cache operation failed"

        response = handle_server_error(log_message=log_message)

        mock_logger.error.assert_called_once_with("Server error: %s", log_message)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class SafeGetObjectTest(TestCase):
    """Test cases for safe_get_object_or_404 function."""

    def test_safe_get_object_found(self):
        """Test safe get object when object exists."""
        # Create mock model class
        mock_model = MagicMock()
        mock_instance = MagicMock()
        mock_model.objects.get.return_value = mock_instance

        # Should return the object
        result = safe_get_object_or_404(mock_model, id=1)
        self.assertEqual(result, mock_instance)
        mock_model.objects.get.assert_called_once_with(id=1)

    def test_safe_get_object_not_found(self):
        """Test safe get object when object doesn't exist."""
        # Create mock model class that raises DoesNotExist
        mock_model = MagicMock()
        mock_model.DoesNotExist = Exception  # Mock the DoesNotExist exception
        mock_model.objects.get.side_effect = mock_model.DoesNotExist()
        mock_model.__name__ = "TestModel"

        # Should raise ObserverNotFound
        with self.assertRaises(ObserverNotFound):
            safe_get_object_or_404(mock_model, id=999)

    @patch("shared.api.error_handlers.logger")
    def test_safe_get_object_not_found_logging(self, mock_logger):
        """Test safe get object logging when not found."""
        # Create mock model class
        mock_model = MagicMock()
        mock_model.DoesNotExist = Exception
        mock_model.objects.get.side_effect = mock_model.DoesNotExist()
        mock_model.__name__ = "TestModel"

        # Should log the not found event
        with self.assertRaises(ObserverNotFound):
            safe_get_object_or_404(mock_model, id=999, name="test")

        mock_logger.info.assert_called_once_with(
            "Object not found: %s with %s", "TestModel", {"id": 999, "name": "test"}
        )

    def test_safe_get_object_custom_error_message(self):
        """Test safe get object with custom error message."""
        # Create mock model class
        mock_model = MagicMock()
        mock_model.DoesNotExist = Exception
        mock_model.objects.get.side_effect = mock_model.DoesNotExist()
        mock_model.__name__ = "TestModel"

        custom_message = "Test model not found"

        # Should raise ObserverNotFound with custom message
        with self.assertRaises(ObserverNotFound) as context:
            safe_get_object_or_404(mock_model, error_message=custom_message, id=999)

        self.assertEqual(str(context.exception.detail), custom_message)


class ErrorHandlerMixinTest(APITestCase):
    """Test cases for ErrorHandlerMixin."""

    def setUp(self):
        self.mixin = ErrorHandlerMixin()
        self.mixin.__class__.__name__ = "TestViewSet"  # For logging

    def test_handle_exception_http404(self):
        """Test handling Http404 exception."""
        exc = Http404("Page not found")
        response = self.mixin.handle_exception(exc)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["code"], "not_found")

    def test_handle_exception_permission_denied(self):
        """Test handling PermissionDenied exception."""
        exc = PermissionDenied("Access denied")
        response = self.mixin.handle_exception(exc)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "permission_denied")

    def test_handle_exception_validation_error(self):
        """Test handling ValidationError exception."""
        exc = ValidationError("Invalid data")
        response = self.mixin.handle_exception(exc)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertEqual(response.data["detail"], "Validation failed")

    def test_handle_exception_validation_error_with_dict(self):
        """Test handling ValidationError with message_dict."""
        exc = ValidationError({"field": ["Error message"]})
        response = self.mixin.handle_exception(exc)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["errors"], {"field": ["Error message"]})

    def test_handle_exception_observer_api_exception(self):
        """Test handling custom ObserverAPIException."""
        exc = ObserverNotFound(detail="Custom not found")
        response = self.mixin.handle_exception(exc)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Custom not found")
        self.assertEqual(response.data["code"], "not_found")

    @patch("shared.api.error_handlers.logger")
    def test_handle_exception_unexpected(self, mock_logger):
        """Test handling unexpected exceptions."""
        exc = ValueError("Unexpected error")
        response = self.mixin.handle_exception(exc)

        # Should log the unexpected error
        mock_logger.error.assert_called_once_with(
            "Unhandled exception in %s", "TestViewSet", exc_info=exc
        )

        # Should return generic server error
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["code"], "server_error")
