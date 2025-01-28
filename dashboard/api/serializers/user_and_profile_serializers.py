from rest_framework import serializers
from django.contrib.auth.models import User
from dashboard.models import Profile, Organization, Tier


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name']


class TierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tier
        fields = ['id', 'tier_name', 'level']


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(
        source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    date_joined = serializers.DateTimeField(
        source='user.date_joined', read_only=True)
    last_login = serializers.DateTimeField(
        source='user.last_login', read_only=True)
    organization = OrganizationSerializer(read_only=True)
    tier = TierSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'username', 'email', 'date_of_birth', 'phone_number',
            'address', 'city', 'state', 'country', 'zip_code', 'bio', 'organization',
            'tier', 'date_joined', 'last_login'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    zip_code = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=True)
    bio = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email', 'phone_number', 'address', 'city', 'state',
            'country', 'zip_code', 'date_of_birth', 'bio'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        """
        Ensure the email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    def validate_username(self, value):
        """
        Ensure the username is unique.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists.")
        return value

    def create(self, validated_data):
        """
        Create a new user and their associated profile.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        Profile.objects.create(
            user=user,
            phone_number=validated_data.get('phone_number', ''),
            address=validated_data.get('address', ''),
            city=validated_data.get('city', ''),
            state=validated_data.get('state', ''),
            country=validated_data.get('country', ''),
            zip_code=validated_data.get('zip_code', ''),
            date_of_birth=validated_data['date_of_birth'],
            bio=validated_data.get('bio', '')
        )
        return user
