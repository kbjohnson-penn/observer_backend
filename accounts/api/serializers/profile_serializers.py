from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import Profile, Organization, Tier
from shared.address_utils import split_address, combine_address

User = get_user_model()


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
    # Combine address_1 and address_2 into a single address field for frontend compatibility
    address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'username', 'email', 'date_of_birth', 'phone_number',
            'address', 'city', 'state', 'country', 'zip_code', 'bio', 'organization',
            'tier', 'date_joined', 'last_login'
        ]

    def to_representation(self, instance):
        """Customize the serialized representation."""
        data = super().to_representation(instance)
        # Combine address_1 and address_2 into a single address field
        data['address'] = combine_address(instance.address_1, instance.address_2)
        return data

    def update(self, instance, validated_data):
        """Handle address field update by splitting into address_1 and address_2."""
        if 'address' in validated_data:
            address = validated_data.pop('address')
            instance.address_1, instance.address_2 = split_address(address)
        
        return super().update(instance, validated_data)


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
        if User.objects.using('accounts').filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    def validate_username(self, value):
        """
        Ensure the username is unique.
        """
        if User.objects.using('accounts').filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists.")
        return value

    def create(self, validated_data):
        """
        Create a new user and their associated profile.
        """
        user = User.objects.db_manager('accounts').create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        
        # Handle address field splitting into address_1 and address_2
        address = validated_data.get('address', '')
        address_1, address_2 = split_address(address)
        
        # Check if profile already exists (from signals) or create new one
        try:
            profile = user.profile
            # Update existing profile
            profile.phone_number = validated_data.get('phone_number', '')
            profile.address_1 = address_1  
            profile.address_2 = address_2
            profile.city = validated_data.get('city', '')
            profile.state = validated_data.get('state', '')
            profile.country = validated_data.get('country', '')
            profile.zip_code = validated_data.get('zip_code', '')
            profile.date_of_birth = validated_data['date_of_birth']
            profile.bio = validated_data.get('bio', '')
            profile.save(using='accounts')
        except Profile.DoesNotExist:
            # Create new profile if signal didn't create one
            Profile.objects.using('accounts').create(
                user=user,
                phone_number=validated_data.get('phone_number', ''),
                address_1=address_1,
                address_2=address_2,
                city=validated_data.get('city', ''),
                state=validated_data.get('state', ''),
                country=validated_data.get('country', ''),
                zip_code=validated_data.get('zip_code', ''),
                date_of_birth=validated_data['date_of_birth'],
                bio=validated_data.get('bio', '')
            )
        return user
