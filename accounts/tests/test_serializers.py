from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.api.serializers.profile_serializers import UserRegistrationSerializer
from shared.address_utils import split_address

User = get_user_model()


class UserRegistrationSerializerTest(TestCase):
    """Test cases for user registration serializer."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.valid_data = {
            "username": "newuser",
            "password": "securepass123",
            "email": "newuser@example.com",
            "date_of_birth": "1990-01-01",
            "address": "123 Main St, Apt 4B",
            "city": "Boston",
            "state": "MA",
            "country": "US",
            "zip_code": "02101",
            "phone_number": "1234567890",
            "bio": "Test bio",
        }

    def test_registration_with_valid_data(self):
        """Test user registration with valid data."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("securepass123"))

        # Check profile was created with correct data
        self.assertTrue(hasattr(user, "profile"))
        profile = user.profile
        self.assertEqual(profile.city, "Boston")
        self.assertEqual(profile.state, "MA")
        self.assertEqual(profile.phone_number, "1234567890")
        self.assertEqual(profile.bio, "Test bio")

    def test_registration_with_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create first user
        User.objects.db_manager("accounts").create_user(
            username="existing", email="duplicate@example.com", password="testpass123"
        )

        # Try to register with same email
        data = self.valid_data.copy()
        data["email"] = "duplicate@example.com"
        data["username"] = "newuser2"

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("already exists", str(serializer.errors["email"][0]))

    def test_registration_with_duplicate_username(self):
        """Test registration with duplicate username."""
        # Create first user
        User.objects.db_manager("accounts").create_user(
            username="duplicate", email="existing@example.com", password="testpass123"
        )

        # Try to register with same username
        data = self.valid_data.copy()
        data["username"] = "duplicate"
        data["email"] = "newuser2@example.com"

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)
        self.assertIn("already exists", str(serializer.errors["username"][0]))

    def test_address_splitting_in_registration(self):
        """Test that address is properly split into address_1 and address_2."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        profile = user.profile

        # Check address was split correctly
        expected_address_1, expected_address_2 = split_address("123 Main St, Apt 4B")
        self.assertEqual(profile.address_1, expected_address_1)
        self.assertEqual(profile.address_2, expected_address_2)
