import secrets
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models.organization_models import Organization

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for JWT token to add claims if needed.
    Allows login with either username or email.
    """

    username_field = "username"

    def validate(self, attrs):
        username_or_email = attrs.get(self.username_field)

        # Check if input is an email
        if "@" in username_or_email:
            try:
                user = User.objects.using("accounts").get(email=username_or_email)
                attrs[self.username_field] = user.username
            except User.DoesNotExist:
                # Use generic error message to prevent user enumeration
                raise serializers.ValidationError("Invalid email or password.")

        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims if needed
        # Example: token['email'] = user.email
        return token


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Creates a pending user account that requires email verification.
    """

    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)
    organization_name = serializers.CharField(max_length=200, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "organization_name",
        )
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate_email(self, value):
        """Ensure email is unique"""
        if User.objects.using("accounts").filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        """Validate password fields if provided"""
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        # If passwords are provided, validate them
        if password or password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError(
                    {"password_confirm": "Password fields didn't match."}
                )

            if password:
                try:
                    validate_password(password)
                except ValidationError as e:
                    raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        """Create user account"""
        # Remove password confirmation and organization name from user data
        validated_data.pop("password_confirm", None)
        organization_name = validated_data.pop("organization_name", None)
        password = validated_data.pop("password", None)

        # Generate username from email
        username = validated_data["email"].split("@")[0]

        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.using("accounts").filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        validated_data["username"] = username

        # Create user
        if password:
            # If password provided, create active user
            user = User.objects.db_manager("accounts").create_user(**validated_data)
            user.set_password(password)
        else:
            # Create inactive user for email verification flow
            user = User.objects.db_manager("accounts").create_user(**validated_data)
            user.is_active = False
            # Generate temporary password that will be changed during verification
            temp_password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
            )
            user.set_password(temp_password)

        user.save(using="accounts")

        # Handle organization
        if organization_name:
            try:
                organization, created = Organization.objects.using("accounts").get_or_create(
                    name=organization_name.strip()
                )
                # Create profile will be handled by signals
                if hasattr(user, "profile"):
                    user.profile.organization = organization
                    user.profile.save(using="accounts")
            except Exception:
                # Don't fail registration if organization creation fails
                pass

        return user


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification and password setup.
    """

    token = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})

        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request (forgot password).
    Only requires email.
    """

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    Validates token and new password.
    """

    token = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})

        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs
