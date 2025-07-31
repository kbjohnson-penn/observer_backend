from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, BasePermission
from accounts.models import Tier
from clinical.models import Encounter, Patient, Provider


def filter_queryset_by_user_tier(queryset, user, related_field="tier"):
    """
    Filters a queryset based on the user's tier level, using a related field to traverse relationships if needed.
    For Encounter models, use related_field="tier_id" since tier is now an IntegerField.
    For nested relationships like EncounterFile, use related_field="encounter__tier_id".
    """
    if user.is_superuser:
        return queryset
    if hasattr(user, 'profile') and user.profile.tier:
        user_tier = user.profile.tier
        
        # Handle different field types
        if related_field.endswith("tier_id"):
            # For IntegerField references to tier (direct or nested), filter by accessible tier IDs
            accessible_tiers = Tier.objects.using('accounts').filter(level__lte=user_tier.level)
            accessible_tier_ids = list(accessible_tiers.values_list('id', flat=True))
            filter_kwargs = {f"{related_field}__in": accessible_tier_ids}
        else:
            # For ForeignKey relationships, filter by tier objects
            accessible_tiers = Tier.objects.using('accounts').filter(level__lte=user_tier.level)
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

    def has_permission(self, request, view):
        """
        View-level permission check - require authentication.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Directly check the tier for Encounter objects
        if isinstance(obj, Encounter):
            # Manual lookup for tier from accounts database
            try:
                tier = Tier.objects.using('accounts').get(id=obj.tier_id)
                return view.has_access_to_tier(request.user, tier)
            except Tier.DoesNotExist:
                return False  # Invalid tier_id, deny access

        # For Patient and Provider, check encounters linked to the object
        if isinstance(obj, Patient):
            encounters = Encounter.objects.using('clinical').filter(patient=obj)
        elif isinstance(obj, Provider):
            encounters = Encounter.objects.using('clinical').filter(provider=obj)
        else:
            return False

        # Collect unique tier_ids from encounters (all encounters have tier_id now)
        tier_ids = {encounter.tier_id for encounter in encounters}
        
        # If no encounters found, deny access
        if not tier_ids:
            return False
            
        # Bulk fetch tiers from accounts database and check access
        tiers = Tier.objects.using('accounts').filter(id__in=tier_ids)
        for tier in tiers:
            if view.has_access_to_tier(request.user, tier):
                return True
                
        return False
