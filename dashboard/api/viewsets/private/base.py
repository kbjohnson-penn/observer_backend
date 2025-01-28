from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, BasePermission
from dashboard.models import Encounter, Patient, Provider, Tier


def filter_queryset_by_user_tier(queryset, user, related_field="tier"):
    """
    Filters a queryset based on the user's tier level, using a related field to traverse relationships if needed.
    """
    if user.is_superuser:
        return queryset
    if hasattr(user, 'profile') and user.profile.tier:
        user_tier = user.profile.tier
        accessible_tiers = Tier.objects.filter(level__lte=user_tier.level)
        # Dynamically filter using the related field for tier
        filter_kwargs = {f"{related_field}__in": accessible_tiers}
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
        if hasattr(user, 'profile') and user.profile.tier:
            user_tier = user.profile.tier
            return tier.level <= user_tier.level
        return False


class HasAccessToEncounter(BasePermission):
    """
    Custom permission to check access to objects based on encounters.
    """

    def has_object_permission(self, request, view, obj):
        # Directly check the tier for Encounter objects
        if isinstance(obj, Encounter):
            return view.has_access_to_tier(request.user, obj.tier)

        # For Patient and Provider, check encounters linked to the object
        if isinstance(obj, Patient):
            encounters = Encounter.objects.filter(patient=obj)
        elif isinstance(obj, Provider):
            encounters = Encounter.objects.filter(provider=obj)
        else:
            return False

        return any(view.has_access_to_tier(request.user, encounter.tier) for encounter in encounters)
