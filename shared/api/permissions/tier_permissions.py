from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from clinical.models import Encounter, Patient, Provider


def filter_queryset_by_user_tier(queryset, user, related_field="tier_level"):
    """
    Filters a queryset based on the user's tier level.

    The tier_level field stores the tier level (1-5) directly, allowing simple
    integer comparison for access control. Users can access data at or below
    their tier level.

    Args:
        queryset: The queryset to filter
        user: The user making the request
        related_field: Field name for tier filtering (default: "tier_level")
                      For nested relationships, use "encounter__tier_level"

    Returns:
        Filtered queryset where tier_level <= user's tier level

    Example:
        User with tier level 3 can access data with tier_level 1, 2, or 3
    """
    if user.is_superuser:
        return queryset

    if hasattr(user, "profile") and user.profile.tier:
        user_tier_level = user.profile.tier.level
        # User can access data with tier_level <= their tier level
        filter_kwargs = {f"{related_field}__lte": user_tier_level}
        return queryset.filter(**filter_kwargs)

    return queryset.none()


class BaseAuthenticatedViewSet(ReadOnlyModelViewSet):
    """
    A base viewset that applies read-only access and authenticated permissions to all derived viewsets.
    """

    permission_classes = [IsAuthenticated]

    def has_access_to_tier(self, user, tier):
        """
        Check if the user has access to the specified tier.
        """
        if user.is_superuser:
            return True
        if hasattr(user, "profile") and user.profile.tier:
            user_tier = user.profile.tier
            return tier.level <= user_tier.level
        return False


class HasAccessToEncounter(BasePermission):
    """
    Custom permission to check access to objects based on encounters.
    """

    def has_permission(self, request, view):
        """
        View-level permission check - require authentication.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For Encounter objects - check tier_level directly
        if isinstance(obj, Encounter):
            if request.user.is_superuser:
                return True
            if hasattr(request.user, "profile") and request.user.profile.tier:
                user_tier_level = request.user.profile.tier.level
                return obj.tier_level <= user_tier_level
            return False

        # For Patient and Provider, check encounters linked to the object
        if isinstance(obj, Patient):
            encounters = Encounter.objects.using("clinical").filter(patient=obj)
        elif isinstance(obj, Provider):
            encounters = Encounter.objects.using("clinical").filter(provider=obj)
        else:
            return False

        # If no encounters found, deny access
        if not encounters.exists():
            return False

        # Check if user can access any encounter
        if request.user.is_superuser:
            return True
        if hasattr(request.user, "profile") and request.user.profile.tier:
            user_tier_level = request.user.profile.tier.level
            # User can access if ANY encounter has tier_level <= user's level
            return encounters.filter(tier_level__lte=user_tier_level).exists()

        return False
