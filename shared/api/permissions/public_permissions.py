from rest_framework.permissions import BasePermission
from rest_framework.viewsets import ReadOnlyModelViewSet


class IsReadOnly(BasePermission):
    """
    Permission class to allow only read-only access.
    """

    def has_permission(self, request, view):
        return request.method in ("GET", "HEAD", "OPTIONS")


class BasePublicReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    Base viewset for public APIs with read-only access.
    """

    permission_classes = [IsReadOnly]
