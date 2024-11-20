from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['username', 'date_of_birth', 'phone_number', 'address',
                  'city', 'state', 'country', 'zip_code', 'bio', 'organization', 'tier']

    def get_username(self, obj):
        return obj.user.username


class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=True)
    bio = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'phone_number', 'address',
                  'city', 'state', 'country', 'zip_code', 'date_of_birth', 'bio']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        profile_data = {
            'phone_number': validated_data.get('phone_number', ''),
            'address': validated_data.get('address', ''),
            'city': validated_data.get('city', ''),
            'state': validated_data.get('state', ''),
            'country': validated_data.get('country', ''),
            'zip_code': validated_data.get('zip_code', ''),
            'date_of_birth': validated_data['date_of_birth'],
            'bio': validated_data.get('bio', '')
        }
        Profile.objects.create(user=user, **profile_data)
        return user
