"""
Centralized error handling for Observer Backend API.
Provides consistent error responses and logging across all endpoints.
"""
import logging
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework.exceptions import APIException


logger = logging.getLogger(__name__)


class ObserverAPIException(APIException):
    """Base exception class for Observer API errors."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An error occurred.'
    default_code = 'error'


class ObserverNotFound(ObserverAPIException):
    """Exception for resource not found errors."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'not_found'


class ObserverPermissionDenied(ObserverAPIException):
    """Exception for permission denied errors."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied.'
    default_code = 'permission_denied'


class ObserverValidationError(ObserverAPIException):
    """Exception for validation errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input provided.'
    default_code = 'validation_error'


def handle_not_found(detail="Resource not found", log_message=None):
    """
    Standard handler for 404 errors.
    
    Args:
        detail: User-facing error message
        log_message: Internal message for logging (optional)
    
    Returns:
        Response with 404 status
    """
    if log_message:
        logger.warning(f"404 Error: {log_message}")
    
    return Response(
        {"detail": detail, "code": "not_found"},
        status=status.HTTP_404_NOT_FOUND
    )


def handle_permission_denied(detail="Permission denied", log_message=None):
    """
    Standard handler for permission denied errors.
    
    Args:
        detail: User-facing error message
        log_message: Internal message for logging (optional)
    
    Returns:
        Response with 403 status
    """
    if log_message:
        logger.warning(f"Permission denied: {log_message}")
    
    return Response(
        {"detail": detail, "code": "permission_denied"},
        status=status.HTTP_403_FORBIDDEN
    )


def handle_validation_error(detail="Invalid input provided", errors=None, log_message=None):
    """
    Standard handler for validation errors.
    
    Args:
        detail: User-facing error message
        errors: Dictionary of field-specific errors (optional)
        log_message: Internal message for logging (optional)
    
    Returns:
        Response with 400 status
    """
    if log_message:
        logger.info(f"Validation error: {log_message}")
    
    response_data = {"detail": detail, "code": "validation_error"}
    if errors:
        response_data["errors"] = errors
    
    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


def handle_server_error(detail="An internal error occurred", log_message=None, exception=None):
    """
    Standard handler for server errors.
    
    Args:
        detail: User-facing error message (keep generic for security)
        log_message: Internal message for logging (optional)
        exception: The original exception for logging (optional)
    
    Returns:
        Response with 500 status
    """
    if exception:
        logger.error(f"Server error: {log_message or 'Unhandled exception'}", exc_info=exception)
    elif log_message:
        logger.error(f"Server error: {log_message}")
    
    return Response(
        {"detail": detail, "code": "server_error"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def safe_get_object_or_404(model_class, error_message="Resource not found", **kwargs):
    """
    Safely get an object or return standardized 404 response.
    
    Args:
        model_class: Django model class
        error_message: Custom error message for user
        **kwargs: Lookup parameters for get()
    
    Returns:
        Object if found
    
    Raises:
        ObserverNotFound: If object not found
    """
    try:
        return model_class.objects.get(**kwargs)
    except model_class.DoesNotExist:
        logger.info(f"Object not found: {model_class.__name__} with {kwargs}")
        raise ObserverNotFound(detail=error_message)


class ErrorHandlerMixin:
    """
    Mixin to add consistent error handling to ViewSets.
    """
    
    def handle_exception(self, exc):
        """
        Handle exceptions with consistent error responses.
        """
        if isinstance(exc, Http404):
            return handle_not_found()
        elif isinstance(exc, PermissionDenied):
            return handle_permission_denied()
        elif isinstance(exc, ValidationError):
            return handle_validation_error(
                detail="Validation failed",
                errors=exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            )
        elif isinstance(exc, (ObserverAPIException,)):
            return Response(
                {"detail": exc.detail, "code": exc.default_code},
                status=exc.status_code
            )
        else:
            # Log unexpected errors but don't expose details
            logger.error(f"Unhandled exception in {self.__class__.__name__}", exc_info=exc)
            return handle_server_error()