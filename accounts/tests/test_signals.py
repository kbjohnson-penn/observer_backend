from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.models import Profile

User = get_user_model()


class SignalTest(TestCase):
    """Test cases for Django signals."""
    
    databases = ['default', 'accounts']
    
    def test_profile_created_on_user_creation(self):
        """Test that profile is automatically created when user is created."""
        initial_profile_count = Profile.objects.using('accounts').count()
        
        user = User.objects.db_manager('accounts').create_user(
            username='signaltest',
            email='signal@example.com',
            password='testpass123'
        )
        
        # Check that profile was created
        self.assertEqual(Profile.objects.using('accounts').count(), initial_profile_count + 1)
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.user, user)
    
    def test_profile_saved_when_user_saved(self):
        """Test that profile is saved when user is saved."""
        user = User.objects.db_manager('accounts').create_user(
            username='profilesavetest',
            email='profilesave@example.com',
            password='testpass123'
        )
        
        # Modify profile
        user.profile.bio = 'Updated bio'
        user.profile.save(using='accounts')
        
        # Save user (should trigger save_user_profile signal)
        user.first_name = 'Updated'
        user.save(using='accounts')
        
        # Refresh and check profile was saved
        user.profile.refresh_from_db(using='accounts')
        self.assertEqual(user.profile.bio, 'Updated bio')