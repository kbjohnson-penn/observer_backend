from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.api.serializers.profile_serializers import ProfileSerializer
from accounts.models import Profile


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
        profile, created = Profile.objects.using('accounts').get_or_create(
            user=self.request.user,
            defaults={}
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
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
