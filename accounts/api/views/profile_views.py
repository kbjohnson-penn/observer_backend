from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.api.serializers.profile_serializers import ProfileSerializer
from accounts.models import Profile
from accounts.services import AuditService
from accounts.services.audit_constants import AuditCategories, AuditEventTypes


class ProfileView(RetrieveUpdateAPIView):
    """
    View for retrieving and updating user profiles.
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Fetch the profile for the logged-in user, create if it doesn't exist.
        """
        profile, created = Profile.objects.using("accounts").get_or_create(
            user=self.request.user, defaults={}
        )
        return profile

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the logged-in user's profile.
        """
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Update the logged-in user's profile.
        """
        profile = self.get_object()

        # Capture changed fields for audit (before update)
        old_data = self.get_serializer(profile).data
        changed_fields = [
            key
            for key in request.data.keys()
            if key in old_data and request.data.get(key) != old_data.get(key)
        ]

        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Log profile update (only field names, not values for PII)
            AuditService.log(
                request=request,
                event_type=AuditEventTypes.PROFILE_UPDATE,
                category=AuditCategories.PROFILE,
                description="User updated their profile",
                metadata={"changed_fields": changed_fields},
            )

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
